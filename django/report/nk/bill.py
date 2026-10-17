import datetime
import logging
import os
from collections import OrderedDict

from dateutil.relativedelta import relativedelta
from django.conf import settings
from stdnum.ch import esr

from cohiva.utils.pdf import PdfGenerator
from finance.accounting import Account, AccountingBook, AccountingManager, AccountKey, AccountRole
from geno.billing import add_invoice, create_qrbill, get_reference_nr, render_qrbill
from geno.models import InvoiceCategory
from geno.utils import fill_template_pod, nformat, odt2pdf
from report.nk.contract import NkContract
from report.nk.cost import NkCost, NkCostValueType
from report.nk.graph import NkGraph
from report.nk.rental_unit import NkRentalUnit

logger = logging.getLogger("report.nk")


class NkBill:
    def __init__(
        self, contract: NkContract, billing_date: datetime.date, output_dir: str, dry_run=True
    ):
        self.contract = contract
        self.billing_date = billing_date
        self.invoice_date = datetime.date.today()
        self.invoice_id = None
        self.dry_run = dry_run
        self.output_dir = output_dir
        self.rental_unit_files = []
        self.has_previous_data = False
        self.odt_bill_template = None
        self.odt_akonto_recommendation_template = None
        self.output_pdf_filename = None
        self.akonto_recommendation_pdf_filename = None
        self.akonto_recommendation_qr_filename = None
        self.regenerate_invoice_id = None
        self.virtual_contract_account = self._get_virtual_contract_account()

    @property
    def dry_run_tag(self):
        return "DRY-RUN: " if self.dry_run else ""

    def set_templates(self, bill_template, akonto_recommendation_template=None):
        self.odt_bill_template = bill_template
        self.odt_akonto_recommendation_template = akonto_recommendation_template

    def set_output_filename(self, filename):
        self.output_pdf_filename = filename

    def create(self, costs: list[NkCost], total_building_costs: float, context: dict = None):
        contract_context = context or {}
        self.contract.update_context(contract_context, costs)
        contract_context["bill_lines"] = []
        for ru in self.contract.rental_units:
            ru_context = contract_context | self._get_rental_unit_context(
                costs, total_building_costs, ru
            )
            self.rental_unit_files.append(self._create_rental_unit_files(ru_context, ru))
            contract_context["bill_lines"].append(self._get_bill_line(ru_context))
        if context["total_akonto"]:
            context["bill_lines"].append(
                {
                    "date": self.billing_date.strftime("%d.%m.%Y"),
                    "text": "Abzüglich Akontozahlungen",
                    "total": nformat(context["total_akonto"] * -1),
                }
            )
        self._create_akonto_recommendation(contract_context)
        with AccountingManager() as book:
            self._do_accounting(contract_context, book)
        self._create_final_pdf(self._get_qrbill(contract_context))

    def get_regeneration_data(self):
        if self.dry_run:
            return None
        return {
            "type": "nk_bills",
            "contract_id": self.contract.id,
            "invoice_id": self.regenerate_invoice_id,
        }

    def _get_rental_unit_context(
        self, costs: list[NkCost], total_building_costs, ru: NkRentalUnit
    ) -> dict:
        context = ru.get_context()
        total_ru_costs = self.contract.get_total_costs(costs, ru)
        paid_ru_akonto = self.contract.get_paid_akonto(ru)
        context["s_chf"] = nformat(total_ru_costs)
        context["akonto_chf"] = nformat(paid_ru_akonto)
        context["diff_chf"] = nformat(total_ru_costs - float(paid_ru_akonto))
        context["costs"] = []
        for name, group in self._get_billing_groups(costs).items():
            cost_context = self._get_billing_group_context(
                name, group, ru, total_building_costs, total_ru_costs
            )
            if cost_context:
                context["costs"].append(cost_context)
        return context

    def _create_rental_unit_files(self, context, ru):
        tmp_filename = fill_template_pod(self.odt_bill_template, context, output_format="odt")
        odt_file = "%s/bills/parts/%s_object_%s.odt" % (self.output_dir, self.contract, ru.id)
        os.rename(tmp_filename, odt_file)
        # nk.log.append("Created %s" % filename)

        graph_files = self._create_rental_unit_graphs(context, ru)

        return {"odt_file": odt_file, "graph_files": graph_files}

    def _create_rental_unit_graphs(self, context, ru):
        file_prefix = "%s/bills/graphs/%s_object_%s" % (self.output_dir, self.contract, ru.id)
        graph_files = {}
        graph = NkGraph(file_prefix)
        if self.has_previous_data:
            self._create_timeseries(
                self.contract,
                ru,
                context,
                file_prefix,
            )
        if ru.section == "Wohnen":
            output_filename = graph.create_energy_consumption_graph(context)
            graph_files["energy_consumption_graph"] = output_filename
        return graph_files

    def _create_timeseries(self, contract, ru, context, file_prefix):
        print("TODO: Create timeseries graphs")
        return None

    @staticmethod
    def _get_billing_groups(costs: list[NkCost]):
        billing_groups = OrderedDict()
        for cost in costs:
            if cost.billing_group not in billing_groups:
                billing_groups[cost.billing_group] = []
            billing_groups[cost.billing_group].append(cost)
        return billing_groups

    def _get_billing_group_context(
        self, name, group, rental_unit, total_building_cost, total_ru_cost
    ):
        object_cost = 0
        building_cost = 0
        for cost in group:
            object_cost += cost.get_assigned_amount(
                NkCostValueType.COST, self.contract, rental_unit
            )
            building_cost += cost.get_building_amount(NkCostValueType.COST)
        if object_cost == 0 and building_cost == 0:
            return None
        if building_cost:
            share = "%s%%" % nformat(object_cost / building_cost * 100.0, 2)
        else:
            share = "-"
        building_cost_percent = (
            building_cost / total_building_cost * 100.0 if total_building_cost else 0
        )
        object_cost_percent = object_cost / total_ru_cost * 100.0 if total_ru_cost else 0
        return {
            "name": name,
            "chft": nformat(building_cost),
            "chf": nformat(object_cost),
            "pctt": nformat(building_cost_percent, 1),
            "pct": nformat(object_cost_percent, 1),
            "share": share,
        }

    def _get_bill_line(self, context):
        return {
            "date": self.billing_date.strftime("%d.%m.%Y"),
            "text": f"Nebenkosten {context['rental_unit']}",
            "total": context["s_chf"],
        }

    def _create_akonto_recommendation(self, input_context):
        context = input_context.copy()
        if (
            not context["total_amount"]
            or not context["total_akonto"]
            or context["total_amount"] < 0
            or context["total_akonto"] < 0
            or context["total_amount"] / context["total_akonto"]
            <= context["akonto_threshold"] / 100
        ):
            # No recommendation needed.
            return

        tmp_filename = fill_template_pod(
            self.odt_akonto_recommendation_template, context, output_format="odt"
        )
        filename = "%s/bills/parts/%s_EmpfehlungAkonto.odt" % (self.output_dir, self.contract)
        os.rename(tmp_filename, filename)
        self.akonto_recommendation_pdf_filename = odt2pdf(filename)
        self.akonto_recommendation_qr_filename = self._get_akonto_qrbill(context)

    def _create_final_pdf(self, qr_bill_pdf):
        # Put everything together.
        # 1. Bill with QR-Code
        # 2. Detail pages per object, including plots
        # 3. Additional payment info (if applicable)

        pdfgen = PdfGenerator()
        pdfgen.append_pdf_file(qr_bill_pdf)

        for ru_files in self.rental_unit_files:
            pdfgen.append_pdf_file(
                odt2pdf(ru_files["odt_file"]),
                merge_pdfs_on_last_page=ru_files.get("graph_files", []),
                transform={"tx": 60, "ty": 560, "dy": -250, "scale": 0.7},
            )

        if self.akonto_recommendation_pdf_filename:
            pdfgen.append_pdf_file(
                self.akonto_recommendation_pdf_filename, self.akonto_recommendation_qr_filename
            )

        pdfgen.write_file(self.output_pdf_filename)

    def _get_qrbill(self, context):
        invoice_category = InvoiceCategory.objects.get(reference_id=12)
        if self.contract.is_virtual:
            ## Virtual contract
            self.invoice_id = 8888888888
            ref_number = get_reference_nr(None, 0, self.invoice_id)
            output_filename = "NK_%s_%s.pdf" % (
                self.virtual_contract_account.name,
                self.invoice_date.strftime("%Y%m%d"),
            )
            context["contract_info"] = self.virtual_contract_account.name
        else:
            if self.dry_run:
                self.invoice_id = 9999999999

            ref_number = get_reference_nr(invoice_category, self.contract.id, self.invoice_id)
            output_filename = "Rechnung_%s_%s_%s.pdf" % (
                invoice_category.name,
                self.invoice_date.strftime("%Y%m%d"),
                esr.compact(ref_number),
            )
            context["contract_info"] = self.contract.geno_contract.get_contract_label()

        total_amount = context["total_amount"]
        if total_amount < 0:
            context["qr_amount"] = 0
            if self.contract.geno_contract and self.contract.geno_contract.bankaccount:
                context["extra_text"] = (
                    "Ohne anderslautenden Gegenbericht in den nächsten 30 Tagen, "
                    "werden wir das Guthaben von CHF %s auf das bei uns registrierte "
                    "Konto %s überweisen."
                    % (nformat(-1 * total_amount), self.contract.geno_contract.bankaccount)
                )
            else:
                context["extra_text"] = (
                    "Wir bitten %s, uns die Kontoangaben für die Rückerstattung des Guthabens "
                    "von CHF %s in den nächsten 30 Tagen mitzuteilen "
                    f"(am liebsten per Email an {settings.SERVER_EMAIL}). Vielen Dank!"
                    % (context["dich"], nformat(-1 * total_amount))
                )
        else:
            context["qr_amount"] = total_amount

        if "betreff" not in context:
            context["betreff"] = "Rechnung %s" % invoice_category.name
        context["invoice_date"] = self.invoice_date.strftime("%d.%m.%Y")
        context["invoice_duedate"] = (self.invoice_date + relativedelta(months=2)).strftime(
            "%d.%m.%Y"
        )
        context["invoice_nr"] = self.invoice_id
        context["show_liegenschaft"] = True
        context["sect_rent"] = False
        context["sect_generic"] = True
        context["generic_info"] = context["bill_lines"]
        context["s_generic_total"] = nformat(total_amount)
        context["qr_extra_info"] = "Rechnung %s" % context["invoice_nr"]
        context["preview"] = self.dry_run

        (ret, mails_sent, mail_recipient) = create_qrbill(
            ref_number,
            self.contract.address,
            context,
            output_filename,
            render=True,
            dry_run=self.dry_run,
        )
        if ret:
            logger.error(
                f"Fehler beim Erzeugen der Rechnung für Vertrag {self.contract.id}: {ret}"
            )
            raise RuntimeError(
                f"Fehler beim erzeugen der Rechnung für Vertrag-ID {self.contract.id} "
                f"(Rechnung Nr. {self.invoice_id}, CHF {total_amount}): {ret}"
            )
        return "/tmp/%s" % output_filename

    def _get_akonto_qrbill(self, context):
        invoice_category = self._get_invoice_category(kind="akonto_recommendation")
        ref_number = get_reference_nr(invoice_category, self.contract.id)

        context["qr_account"] = settings.FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["iban"]
        context["qr_ref_number"] = ref_number
        context["qr_amount"] = None
        context["qr_debtor"] = self.contract.address
        context["qr_extra_info"] = (
            "NK-Akontozahlung ausserordentlich, Vertrag %s" % self.contract.id
        )
        output_filename = "QR-ESR_%s_%s.pdf" % (invoice_category.name, esr.compact(ref_number))

        try:
            render_qrbill(None, context, output_filename)
        except Exception as e:
            logger.error(
                "Could not create QR-bill for NK-Akonto ausserordentlich for contract %s: %s"
                % (self.contract, e)
            )
            raise RuntimeError("Konnte QR Rechnung für Akonto ausserordentlich nicht erstellen.")
        return "/tmp/%s" % output_filename

    def _do_accounting(self, context: dict, book: AccountingBook):
        # TODO: Maybe better explicit arguments or class fields instead of context?
        billing_period_end = datetime.datetime.strptime(context["billing_period_end"], "%Y-%m-%d")
        total_akonto = context["total_akonto"]
        total_amount = context["total_amount"]
        comment = context["comment"]
        account_nk = Account.from_settings(AccountKey.NK).set_code(
            contract=self.contract.geno_contract
        )
        account_nk_receivables = Account.from_settings(AccountKey.NK_RECEIVABLES).set_code(
            contract=self.contract.geno_contract
        )
        if total_akonto:
            ## Transaction: Forderungen>Nebenkosten [1103] -> Passive Abgrenzung>NK-Akonto [2301]
            book.add_transaction(
                total_akonto,
                account_nk,
                account_nk_receivables,
                billing_period_end.date(),
                f"NK-Abrechnung Verrechnung Akontozahlungen {self.contract.geno_contract}",
                autosave=False,
            )
            logger.info(
                "%sAdded transaction: Verrechnung Akontozahlung for contract id %s)."
                % (self.dry_run_tag, self.contract.id)
            )

        if not total_amount:
            return

        if self.contract.geno_contract:
            ## Create invoice for difference (Forderungen>Nebenkosten [1103] -> Forderungen>Mieter [1102])
            ## This will save the book, including the transaction above.
            try:
                invoice_category = self._get_invoice_category()
                invoice = add_invoice(
                    None,
                    invoice_category,
                    invoice_category.name,
                    self.invoice_date,
                    total_amount,
                    book=book,
                    contract=self.contract.geno_contract,
                    dry_run=self.dry_run,
                    comment=comment,
                )
            except Exception as e:
                logger.error(
                    "Could not create invoice for contract id %s: %s" % (self.contract.id, e)
                )
                raise RuntimeError(
                    f"Konnte Rechnung-Objekt für Vertrag ID {self.contract.id} nicht erzeugen."
                )
            logger.info(
                "%sAdded invoice %s for contract id %s: invoice id %s"
                % (
                    self.dry_run_tag,
                    invoice_category,
                    self.contract.id,
                    invoice.id if invoice else "None",
                )
            )
            if not self.dry_run:
                self.invoice_id = invoice.id
        else:
            # Virtual contract: Just do accounting, no invoice
            description = f"NK-Abrechnung {self.virtual_contract_account.name}"
            book.add_transaction(
                context["total_amount"],
                self.virtual_contract_account,
                account_nk_receivables,
                billing_period_end.date(),
                description,
                autosave=not self.dry_run,
            )
            logger.info(
                "%sAdded transaction: %s for virtual contract '%s')."
                % (self.dry_run_tag, description, self.virtual_contract_account.name)
            )

    @staticmethod
    def _get_invoice_category(kind="default"):
        if kind == "default":
            # Nebenkostenabrechnung
            return InvoiceCategory.objects.get(reference_id=12)
        if kind == "akonto_recommendation":
            # Nebenkosten Akonto ausserordentlich
            return InvoiceCategory.objects.get(reference_id=13)
        return None

    def _get_virtual_contract_account(self):
        if not self.contract.is_virtual:
            return None
        # Virtual contracts: Just do accounting, no invoice
        # Example: (configured in settings.FINANCIAL_ACCOUNTS)
        #      1 - Aufwand Gästezimmer [6700]
        #      2 - Aufwand Sitzungszimmer [6720]
        #      3 - Geschäftsstelle -> Büromiete [6500]
        #      4 - Holliger -> Nicht verteilbare NK [4581]  --> von dort manuell umbuchen / in Rechnung stellen
        #      5 - Allgemein -> Nicht verteilbare NK [4581] --> von dort manuell umbuchen / in Rechnung stellen
        #      6 - Leerstand -> NK Leerstand [4582]
        account = None
        for key, account_conf in settings.FINANCIAL_ACCOUNTS.items():
            if (
                account_conf.get("role") == AccountRole.NK_VIRTUAL
                and "virtual_id" in account_conf
                and account_conf["virtual_id"] == self.contract.id
            ):
                account = Account.from_settings(key)
        if account and self.contract.geno_contract:
            account.set_code(contract=self.contract.geno_contract)
        elif account and self.contract.rental_units and self.contract.rental_units[0].building:
            account.set_code(building=self.contract.rental_units[0].building)
        return account
