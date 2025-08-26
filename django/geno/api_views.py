import logging
import os
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models import Q, Sum
from django.http import FileResponse
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from stdnum.ch import esr

import geno.settings as geno_settings
from credit_accounting.api_views import get_capabilities as credit_accounting_capabilities
from geno.gnucash import (
    add_invoice,
    add_transaction,
    create_qrbill,
    get_book,
    get_reference_nr,
    render_qrbill,
)
from geno.models import Address, Contract, Invoice, InvoiceCategory, RentalUnit
from geno.serializers import (
    ContractSerializer,
    GroupSerializer,
    RentalUnitSerializer,
    UserSerializer,
)
from geno.utils import nformat
from reservation.api_views import get_capabilities as reservation_capabilities

logger = logging.getLogger("geno")


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # permission_classes = [permissions.IsAuthenticated]


class RentalUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows active rental units to be viewed.
    """

    queryset = RentalUnit.objects.filter(active=True)
    serializer_class = RentalUnitSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ContractViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows active contracts to be viewed.
    """

    queryset = Contract.objects.filter(state__in=("unterzeichnet", "gekuendigt"))
    serializer_class = ContractSerializer
    # permission_classes = [permissions.IsAuthenticated]


class Akonto(APIView):
    """
    Get paid akonto amount for contract and billing period.
    """

    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]  ## Only admins

    def get(self, request, format=None):
        if "billing_period_start" not in request.query_params:
            raise ValidationError("billing_period_start is required.")
        if "billing_period_end" not in request.query_params:
            raise ValidationError("billing_period_end is required.")
        self.billing_period_start = datetime.strptime(
            request.query_params["billing_period_start"], "%Y-%m-%d"
        )
        self.billing_period_end = datetime.strptime(
            request.query_params["billing_period_end"], "%Y-%m-%d"
        )
        self.invoice_category_nk_ausserordentlich = InvoiceCategory.objects.get(
            name="Nebenkosten Akonto ausserordentlich"
        )
        self.contract_id = None
        if "contract_id" in request.query_params:
            try:
                self.contract_id = int(request.query_params["contract_id"])
            except:
                raise ValidationError("contract_id must be an integer")
            akonto = self.get_akonto_for_contract()
        else:
            akonto = self.get_akonto_for_all_contracts()
        return Response({"akonto_billing": akonto})

    def get_akonto_for_contract(self):
        akonto_total = 0
        if self.contract_id >= 0:
            contract = Contract.objects.get(id=self.contract_id)
            ## Get payments from contract AND linked contracts in case there are invoices before/after billing contract has been changed!
            for c in Contract.objects.filter(Q(id=contract.id) | Q(billing_contract=contract)):
                akonto = Invoice.objects.filter(
                    contract=c,
                    gnc_account=geno_settings.GNUCASH_ACC_NK,
                    date__gte=self.billing_period_start,
                    date__lte=self.billing_period_end,
                ).aggregate(Sum("amount"))
                if akonto["amount__sum"]:
                    akonto_total += akonto["amount__sum"]
            ## Ausserordentliche Akonto-Zahlungen
            for c in Contract.objects.filter(Q(id=contract.id) | Q(billing_contract=contract)):
                akonto = Invoice.objects.filter(
                    contract=c,
                    invoice_category=self.invoice_category_nk_ausserordentlich,
                    invoice_type="Invoice",
                    date__gte=self.billing_period_start,
                    date__lte=self.billing_period_end,
                ).aggregate(Sum("amount"))
                if akonto["amount__sum"]:
                    akonto_total += akonto["amount__sum"]
        return akonto_total

    def get_akonto_for_all_contracts(self):
        ## Get invoices for NK-Akonto and NK-Ausserordentlich
        akonto_invoices = Invoice.objects.filter(
            Q(gnc_account=geno_settings.GNUCASH_ACC_NK)
            | Q(invoice_category=self.invoice_category_nk_ausserordentlich),
            invoice_type="Invoice",
            date__gte=self.billing_period_start,
            date__lte=self.billing_period_end,
        )

        ## Add akonto per contract (linked billing_contract are added to the main contract)
        akonto_total = {}
        for invoice in akonto_invoices:
            contract_id = getattr(invoice.contract.billing_contract, "id", invoice.contract.id)
            if contract_id in akonto_total:
                akonto_total[contract_id] += invoice.amount
            else:
                akonto_total[contract_id] = invoice.amount
        return akonto_total


class QRBill(APIView):
    """
    Create and return QRBill and execute corresponding accounting transactions.
    """

    ## Require token auth
    # authentication_classes = [authentication.TokenAuthentication]  ## Enable this for csrf_exempt?
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]  ## Only admins
    # permission_classes = [permissions.IsAuthenticated] ## Allow all authenticated users

    def __init__(self, **kwargs):
        ## Virtual contract: Just do accounting, no invoice
        #      1 - Aufwand Gästezimmer [6700]
        #      2 - Aufwand Sitzungszimmer [6720]
        #      3 - Geschäftsstelle -> Büromiete [6500]
        #      4 - Holliger -> Nicht verteilbare NK [4581]  --> von dort manuell umbuchen / in Rechnung stellen
        #      5 - Allgemein -> Nicht verteilbare NK [4581] --> von dort manuell umbuchen / in Rechnung stellen
        #      6 - Leerstand -> NK Leerstand [4582]
        self.virtual_contracts = {
            -1: {"name": "Gästezimmer", "account": "6700"},
            -2: {"name": "Sitzungszimmer", "account": "6720"},
            -3: {"name": "Geschäftsstelle", "account": "6500"},
            -4: {"name": "Holliger", "account": "4581"},
            -5: {"name": "Allgemein", "account": "4581"},
            -6: {"name": "Leerstand", "account": "4582"},
        }
        super().__init__(**kwargs)

    def get_akonto_qrbill(self, request):
        invoice_category = InvoiceCategory.objects.get(
            reference_id=13
        )  # Nebenkosten Akonto ausserordentlich
        ref_number = get_reference_nr(invoice_category, self.contract.id)

        self.context["qr_account"] = settings.GENO_FINANCE_ACCOUNTS["default_debtor"]["iban"]
        if self.address.organization:
            bill_name = self.address.organization
        else:
            bill_name = "%s %s" % (self.address.first_name, self.address.name)
        self.context["qr_ref_number"] = ref_number
        self.context["qr_amount"] = None
        self.context["qr_bill_name"] = bill_name
        self.context["qr_addr_line1"] = self.address.street
        self.context["qr_addr_line2"] = self.address.city
        self.context["qr_extra_info"] = (
            "NK-Akontozahlung ausserordentlich, Vertrag %s" % self.contract.id
        )
        output_filename = "QR-ESR_%s_%s.pdf" % (invoice_category.name, esr.compact(ref_number))

        try:
            render_qrbill(None, self.context, output_filename)
        except Exception as e:
            logger.error(
                "Could not create QR-bill for NK-Akonto ausserordentlich for contract %s (id=%s): %s"
                % (self.contract, request.data["contract_id"], e)
            )
            raise ValidationError("Could not create qr slip: %s." % (e))
        if os.path.isfile("/tmp/%s" % output_filename):
            pdf_file = open("/tmp/%s" % output_filename, "rb")
            resp = FileResponse(
                pdf_file,
                content_type="application/pdf",
                as_attachment=True,
                filename=output_filename,
            )
            logger.info("Return QR-bill for NK-Akonto ausserordentlich: %s" % output_filename)
            return resp
        logger.error(
            "Could not create QR-bill for NK-Akonto ausserordentlich for contract %s (id=%s)"
            % (self.contract, request.data["contract_id"])
        )
        raise ValidationError("Could not create qr slip.")

    def do_accounting(self, request):
        messages = []
        book = get_book(messages)
        if not book:
            logger.error(
                "Konnte Buchhaltung nicht öffnen: %s / contract %s (id=%s)"
                % (messages[-1], self.contract, request.data["contract_id"])
            )
            raise ValidationError("Konnte Buchhaltung nicht öffnen: %s" % messages[-1])

        billing_period_end = datetime.strptime(request.data["billing_period_end"], "%Y-%m-%d")
        if request.data["total_akonto"] > 0:
            ## Transaction: Forderungen>Nebenkosten [1104] -> Passive Abgenzung>NK-Akonto [2301]
            description = "NK-Abrechnung Verrechnung Akontozahlungen %s" % (self.contract)
            account_to = geno_settings.GNUCASH_ACC_NK
            account_from = geno_settings.GNUCASH_ACC_NK_RECEIVABLE
            amount = request.data["total_akonto"]
            add_transaction(
                billing_period_end.date(),
                description,
                account_to,
                account_from,
                amount,
                book=book,
                dry_run=self.dry_run,
            )
            logger.info(
                "%sAdded transaction: Verrechnnung Akontozahlung CHF %s for contract %s (id=%s)."
                % (self.dry_run_tag, amount, self.contract, request.data["contract_id"])
            )

        total_amount = request.data["total_amount"]
        comment = request.data["comment"]
        if self.contract:
            ## Create invoice for difference (Forderungen>Nebenkosten [1104] -> Forderungen>Mieter [1102])

            ## Add invoice, this will save the book, i.e. also the transaction above.
            invoice = add_invoice(
                None,
                self.invoice_category,
                self.invoice_category.name,
                self.invoice_date,
                total_amount,
                book=book,
                contract=self.contract,
                dry_run=self.dry_run,
                comment=comment,
            )
            book.close()
            if isinstance(invoice, str):
                logger.error(
                    "Could not create invoice for contract %s (id=%s): %s"
                    % (self.contract, request.data["contract_id"], invoice)
                )
                raise ValidationError("Konnte Rechnungs-Objekt nicht erzeugen: %s" % invoice)
            logger.info(
                "%sAdded invoice %s for contract %s (id=%s): CHF %s / %s"
                % (
                    self.dry_run_tag,
                    self.invoice_category,
                    self.contract,
                    request.data["contract_id"],
                    total_amount,
                    invoice,
                )
            )
            if not self.dry_run:
                self.invoice_id = invoice.id
        else:
            description = (
                "NK-Abrechnung %s" % (self.virtual_contracts[request.data["contract_id"]]["name"])
            )
            account_to = self.virtual_contracts[request.data["contract_id"]]["account"]
            account_from = geno_settings.GNUCASH_ACC_NK_RECEIVABLE
            amount = total_amount
            add_transaction(
                billing_period_end.date(),
                description,
                account_to,
                account_from,
                amount,
                book=book,
                dry_run=self.dry_run,
            )
            if not self.dry_run:
                book.save()
            book.close()
            logger.info(
                "%sAdded transaction: %s CHF %s for virtual contract (id=%s)."
                % (self.dry_run_tag, description, amount, request.data["contract_id"])
            )

    def post(self, request, format=None):
        request.data["contract_id"] = int(request.data["contract_id"])

        if request.data["contract_id"] < 1:
            ## Virtual contract
            self.contract = None
            self.address = Address.objects.filter(organization=settings.GENO_NAME).first()
        else:
            self.contract = Contract.objects.get(id=request.data["contract_id"])
            self.address = self.contract.get_contact_address()
        self.context = self.address.get_context()
        logger.debug(
            "Getting QR-bill for contract %s (id=%s)"
            % (self.contract, request.data["contract_id"])
        )

        if "get_akonto_qrbill" in request.data and request.data["get_akonto_qrbill"]:
            return self.get_akonto_qrbill(request)

        if "dry_run" in request.data and not request.data["dry_run"]:
            self.dry_run = False
            self.dry_run_tag = ""
        else:
            self.dry_run = True
            self.dry_run_tag = "DRY-RUN: "

        if "invoice_date" in request.data and request.data["invoice_date"]:
            self.invoice_date = date.fromisoformat(request.data["invoice_date"])
        else:
            self.invoice_date = date.today()

        self.invoice_category = InvoiceCategory.objects.get(
            reference_id=12
        )  # Nebenkostenabrechnung

        if "regenerate_invoice_id" in request.data:
            self.invoice_id = request.data["regenerate_invoice_id"]
        else:
            self.do_accounting(request)

        return self.get_qrbill(request)

    def get_qrbill(self, request):
        if self.contract:
            if self.dry_run:
                self.invoice_id = 9999999999

            ref_number = get_reference_nr(self.invoice_category, self.contract.id, self.invoice_id)
            output_filename = "Rechnung_%s_%s_%s.pdf" % (
                self.invoice_category.name,
                self.invoice_date.strftime("%Y%m%d"),
                esr.compact(ref_number),
            )
            self.context["contract_info"] = self.contract.get_contract_label()
        else:
            ## Virtual contract
            self.invoice_id = 8888888888
            ref_number = get_reference_nr(None, 0, self.invoice_id)
            output_filename = "NK_%s_%s.odf" % (
                self.virtual_contracts[request.data["contract_id"]]["name"],
                self.invoice_date.strftime("%Y%m%d"),
            )
            self.context["contract_info"] = self.virtual_contracts[request.data["contract_id"]][
                "name"
            ]

        total_amount = request.data["total_amount"]
        if total_amount < 0:
            self.context["qr_amount"] = 0
            if self.contract and self.contract.bankaccount:
                self.context["extra_text"] = (
                    "Ohne anderslautenden Gegenbericht in den nächsten 30 Tagen, werden wir das Guthaben von CHF %s auf das bei uns registrierte Konto %s überweisen."
                    % (nformat(-1 * total_amount), self.contract.bankaccount)
                )
            else:
                self.context["extra_text"] = (
                    f"Wir bitten %s, uns die Kontoangaben für die Rückerstattung des Guthabens von CHF %s in den nächsten 30 Tagen mitzuteilen (am liebsten per Email an {settings.SERVER_EMAIL}). Vielen Dank!"
                    % (self.context["dich"], nformat(-1 * total_amount))
                )
        else:
            self.context["qr_amount"] = total_amount
            if "extra_text" in request.data:
                self.context["extra_text"] = request.data["extra_text"]

        if "betreff" in request.data:
            self.context["betreff"] = request.data["betreff"]
        else:
            self.context["betreff"] = "Rechnung %s" % self.invoice_category.name
        self.context["invoice_date"] = self.invoice_date.strftime("%d.%m.%Y")
        self.context["invoice_duedate"] = (self.invoice_date + relativedelta(months=2)).strftime(
            "%d.%m.%Y"
        )
        self.context["invoice_nr"] = self.invoice_id
        self.context["show_liegenschaft"] = True
        self.context["sect_rent"] = False
        self.context["sect_generic"] = True
        self.context["generic_info"] = request.data["bill_lines"]
        self.context["s_generic_total"] = nformat(total_amount)
        self.context["qr_extra_info"] = "Rechnung %s" % self.context["invoice_nr"]
        self.context["preview"] = self.dry_run

        (ret, mails_sent, mail_recipient) = create_qrbill(
            ref_number,
            self.address,
            self.context,
            output_filename,
            render=True,
            dry_run=self.dry_run,
        )
        info = "%s CHF %s Nr. %s/%s, %s" % (
            self.address,
            total_amount,
            self.context["invoice_nr"],
            self.context["invoice_date"],
            self.context["betreff"],
        )
        if ret:
            logger.error("Fehler beim Erzeugen der Rechnung für %s: %s" % (info, ret))
            raise ValidationError("Fehler beim erzeugen der Rechnung für %s: %s" % (info, ret))
        else:
            pdf_file = open("/tmp/%s" % output_filename, "rb")
            resp = FileResponse(
                pdf_file,
                content_type="application/pdf",
                as_attachment=True,
                filename=output_filename,
            )
            logger.info("Returning QR-Bill %s" % output_filename)
            return resp


def get_capabilities(request, capabilities):
    capabilities["features"] = []
    if hasattr(request.user, "address"):
        roles = request.user.address.get_roles()
        if "user" in roles:
            capabilities["features"].append("calendar")
            capabilities["features"].append("reservation")
        if "member" in roles or "renter" in roles:
            capabilities["features"].append("chat")
            capabilities["features"].append("cloud")
        if "renter" in roles:
            capabilities["features"].append("report")
            capabilities["features"].append("docs")
            capabilities["features"].append("energy-monitoring")
        if "community" in roles or "renter" in roles:
            capabilities["features"].append("chat_community")
    return


class CapabilitiesView(APIView):
    """
    Get capabilities/permissions for user.
    """

    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticated] ## Only admins

    def get(self, request, format=None):
        capabilities = {}
        get_capabilities(request, capabilities)
        reservation_capabilities(request, capabilities)
        credit_accounting_capabilities(request, capabilities)
        return Response({"status": "OK", "capabilities": capabilities})
