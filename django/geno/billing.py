import contextlib
import datetime
import io
import logging
import os.path
import re
import tempfile
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import Http404
from django.template import Context, loader
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from html2text import html2text

## For QR bill and svg -> pdf
from qrbill import QRBill
from reportlab.graphics import renderPDF
from stdnum.ch import esr
from svglib.svglib import svg2rlg

import geno.settings as geno_settings
from cohiva.utils.pdf import PdfGenerator
from cohiva.utils.strings import pluralize
from cohiva.views.admin import CohivaAdminViewMixin, ResponseVariant
from finance.accounting import (
    Account,
    AccountingBook,
    AccountingManager,
    AccountKey,
    AccountRole,
    Split,
    Transaction,
)

from .models import (
    Address,
    ContentTemplate,
    Contract,
    DocumentType,
    Invoice,
    InvoiceCategory,
    LookupTable,
    Member,
    MemberAttribute,
    MemberAttributeType,
    Share,
    ShareType,
)
from .utils import (
    ensure_dir_exists,
    fill_template_pod,
    nformat,
    odt2pdf,
    remove_temp_files,
    send_error_mail,
)

logger = logging.getLogger("geno")


class InvoiceCreationError(Exception):
    pass


class DuplicateInvoiceError(Exception):
    pass


def create_invoices(
    dry_run=True, reference_date=None, single_contract=None, building_ids=None, download_only=None
):
    if not reference_date:
        reference_date = datetime.datetime.today()

    if single_contract:
        contracts = Contract.objects.filter(id=single_contract)
    elif download_only:
        contracts = Contract.objects.filter(id=download_only)
    else:
        contracts = Contract.objects.filter(state="unterzeichnet").filter(main_contract=None)

    if building_ids:
        contracts = contracts.filter(rental_units__building__in=building_ids).distinct()

    invoice_category = InvoiceCategory.objects.get(
        reference_id=10
    )  # name="Mietzins wiederkehrend")

    messages = []
    count = {"invoices": 0, "contracts": 0}
    all_regular_invoices = []
    all_placeholder_invoices = []
    all_email_messages = []

    with AccountingManager(messages) as book:
        if not book:
            return messages
        for contract in contracts:
            ## Create monthly invoices starting from the reference date
            options = {
                "download_only": download_only,
                "single_contract": single_contract,
                "dry_run": dry_run,
            }
            try:
                result_tuple = create_monthly_invoices(
                    book, contract, reference_date, invoice_category, options
                )
            except InvoiceCreationError as e:
                logger.error(f"Could not create invoice for contract {contract}: {e}")
                messages.append(
                    CohivaAdminViewMixin.make_response_item(
                        _("FEHLER beim Erzeugen der Rechnungen für {contract}: {e}").format(
                            contract=contract, e=e
                        ),
                        variant=ResponseVariant.ERROR,
                    )
                )
                messages.append(
                    CohivaAdminViewMixin.make_response_item(
                        _("VERARBEITUNG ABGEBROCHEN!"), variant=ResponseVariant.ERROR
                    )
                )
                break

            if isinstance(result_tuple[0], str):
                # We got a filename back, so we're done here
                return result_tuple[0]

            result, regular_invoices, placeholder_invoices, email_messages = result_tuple
            if result > 0:
                count["invoices"] += result
                count["contracts"] += 1
                all_regular_invoices.extend(regular_invoices)
                all_placeholder_invoices.extend(placeholder_invoices)
                all_email_messages.extend(email_messages)

    email_objects = []
    if all_email_messages:
        email_objects.append(
            {
                "label": _("Email mit QR-Rechnung an:"),
                "items": all_email_messages,
                "variant": ResponseVariant.INFO.value,
            }
        )
    if email_objects:
        messages.append(
            CohivaAdminViewMixin.make_response_item(_("Email-Versand"), objects=email_objects)
        )

    invoice_objects = []
    if all_regular_invoices:
        invoice_objects.append(
            {
                "label": str(_("Monatsrechnungen hinzugefügt")),
                "items": all_regular_invoices,
                "variant": ResponseVariant.DEFAULT.value,
            }
        )
    if all_placeholder_invoices:
        invoice_objects.append(
            {
                "label": str(_("Platzhalter-Monatsrechnungen hinzugefügt")),
                "items": all_placeholder_invoices,
                "variant": ResponseVariant.INFO.value,
            }
        )

    if invoice_objects:
        messages.append(
            CohivaAdminViewMixin.make_response_item(
                str(_("Rechnungen in Buchhaltung erstellen")), objects=invoice_objects
            )
        )

    if count["invoices"] > 0:
        summary_msg = str(_("%(invoice_count)s für %(contract_count)s")) % {
            "invoice_count": pluralize(count["invoices"], "Rechnung", "Rechnungen"),
            "contract_count": pluralize(count["contracts"], "Vertrag", "Verträge"),
        }
        messages.append(
            CohivaAdminViewMixin.make_response_item(summary_msg, variant=ResponseVariant.INFO)
        )

    return messages


def create_monthly_invoices(book, contract, reference_date, invoice_category, options):
    download_only = options.get("download_only")
    single_contract = options.get("single_contract")
    dry_run = options.get("dry_run")
    start_date = contract.billing_date_start or contract.date
    end_date = contract.billing_date_end or contract.date_end
    if end_date and end_date < reference_date:
        # Don't try to create invoices after the end date of the contract
        month = end_date.month
        year = end_date.year
    else:
        month = reference_date.month
        year = reference_date.year
    stop = False
    billed_months_count = 0
    regular_invoices = []
    placeholder_invoices = []
    messages = []
    while not stop:
        invoices = Invoice.objects.filter(
            contract=contract,
            year=year,
            month=month,
            invoice_type="Invoice",
            is_additional_invoice=False,
        )
        if download_only:
            ## Only generate one bill
            stop = True
        elif invoices:
            stop = True
            # messages.append('Last invoice found: %s' % invoices.first())
            break

        ## Add invoice (if needed)
        factor = Decimal(1.0)
        invoice_date = datetime.date(year, month, 1)

        if start_date > invoice_date:
            stop = True
            invoice_date = datetime.date(year, month, 15)
            if start_date <= invoice_date:
                ## Mid-month start
                factor = Decimal(0.5)
            else:
                ## Contract is in the future
                factor = Decimal(0.0)

        if end_date:
            if end_date <= datetime.date(year, month, 1):
                ## Contract has ended
                factor = Decimal(0.0)
            elif end_date <= datetime.date(year, month, 15):
                ## Mid-month end
                factor = Decimal(0.5)

        ## Use other billing contract if set (for reference number/accounting)
        if factor > 0.0 and contract.billing_contract and contract.billing_contract != contract:
            billing_contract = contract.billing_contract
            billing_contract_info = "%s (Rechnungs-Vertrag: %s)" % (contract, billing_contract)
            is_additional_invoice = True
        else:
            billing_contract = contract
            billing_contract_info = "%s" % (contract)
            is_additional_invoice = False

        ## Get rental unit information
        sum_depot = 0
        sum_rent_total = 0
        sum_rent_net = 0
        sum_nk = 0
        sum_nk_flat = 0
        sum_nk_electricity = 0
        ru_list = []
        rent_info = []
        rent_account_key = None  # Wohnungen: Get account from invoice_category (default)

        ruL = contract.rental_units.order_by("building__name", "name").all()

        by_building = defaultdict(list)
        for ru in ruL:
            by_building[ru.building].append(ru)

        for building, rental_units in by_building.items():
            ru_names = []
            for ru in rental_units:
                if ru.rental_type in ("Gewerbe", "Lager", "Hobby"):
                    rent_account_key = AccountKey.RENT_BUSINESS
                elif ru.rental_type == "Gemeinschaft":
                    rent_account_key = AccountKey.RENT_OTHER
                elif ru.rental_type == "Parkplatz":
                    rent_account_key = AccountKey.RENT_PARKING
                if not ru.rent_netto:
                    ru.rent_netto = Decimal(0.0)
                if not ru.nk:
                    ru.nk = Decimal(0.0)
                if not ru.nk_flat:
                    ru.nk_flat = Decimal(0.0)
                if not ru.nk_electricity:
                    ru.nk_electricity = Decimal(0.0)
                if not ru.depot:
                    ru.depot = Decimal(0.0)
                sum_depot += ru.depot
                sum_rent_total += ru.rent_total if ru.rent_total else Decimal(0.0)
                sum_nk += ru.nk
                sum_nk_flat += ru.nk_flat
                sum_nk_electricity += ru.nk_electricity
                sum_rent_net += ru.rent_netto
                if ru.rent_netto or ru.nk or ru.nk_flat:
                    rent_info.append(
                        {
                            "text": ru.str_short(),
                            "net": ru.rent_netto,
                            "nk": ru.nk + ru.nk_flat,
                            "total": ru.rent_netto + ru.nk + ru.nk_flat,
                        }
                    )
                if ru.nk_electricity:
                    rent_info.append(
                        {
                            "text": "Strompauschale %s" % str(ru.name),
                            "net": "",
                            "nk": "",
                            "total": ru.nk_electricity,
                        }
                    )
                ru_names.append(ru.name)
            ru_list.append(",".join(ru_names) + "; " + building.name)

        if factor > 0.0:
            if factor != 1.0:
                factor_txt = " (Faktor %.2f)" % factor
            else:
                factor_txt = ""

            if (
                sum_rent_net
                or sum_nk
                or sum_nk_flat
                or sum_nk_electricity
                or contract.rent_reduction
                or contract.rent_reservation
            ):
                if not contract.main_contract and not contract.contractors.first():
                    raise InvoiceCreationError("Vertrag hat keine Vertragspartner/Adresse.")
                billed_months_count += 1
                if is_additional_invoice:
                    # Add a placeholder invoice for the contract that is billed through
                    # `billing_contract`, to prevent creation of further invoices
                    invoice = Invoice(
                        name=f"Platzhalter: Inkasso läuft über Vertrag {billing_contract}",
                        invoice_type="Invoice",
                        invoice_category=invoice_category,
                        year=year,
                        month=month,
                        contract=contract,
                        date=invoice_date,
                        amount=Decimal(0.0),
                    )
                    if not dry_run:
                        invoice.save()
                    placeholder_invoices.append(
                        str(_("%(month)d.%(year)d: %(contract)s"))
                        % {"month": month, "year": year, "contract": billing_contract_info}
                    )

            if sum_rent_net > 0.0:
                description = "Nettomiete %02d.%d für %s%s" % (
                    month,
                    year,
                    " / ".join(ru_list),
                    factor_txt,
                )
                invoice_value = sum_rent_net * factor
                add_invoice(
                    rent_account_key,
                    invoice_category,
                    description,
                    invoice_date,
                    invoice_value,
                    book=book,
                    contract=billing_contract,
                    year=year,
                    month=month,
                    is_additional=is_additional_invoice,
                    dry_run=dry_run,
                )
                regular_invoices.append(
                    str(_("%(description)s für %(contract)s"))
                    % {"description": description, "contract": billing_contract_info}
                )

            if sum_nk > 0.0:
                description = "Nebenkosten %02d.%d für %s%s" % (
                    month,
                    year,
                    "/".join(ru_list),
                    factor_txt,
                )
                invoice_value = sum_nk * factor
                add_invoice(
                    AccountKey.NK,
                    invoice_category,
                    description,
                    invoice_date,
                    invoice_value,
                    book=book,
                    contract=billing_contract,
                    year=year,
                    month=month,
                    is_additional=is_additional_invoice,
                    dry_run=dry_run,
                )
                regular_invoices.append(
                    str(_("%(description)s für %(contract)s"))
                    % {"description": description, "contract": billing_contract_info}
                )

            if sum_nk_flat > 0.0:
                description = "Nebenkosten pauschal %02d.%d für %s%s" % (
                    month,
                    year,
                    "/".join(ru_list),
                    factor_txt,
                )
                invoice_value = sum_nk_flat * factor
                add_invoice(
                    AccountKey.NK_FLAT,
                    invoice_category,
                    description,
                    invoice_date,
                    invoice_value,
                    book=book,
                    contract=billing_contract,
                    year=year,
                    month=month,
                    is_additional=is_additional_invoice,
                    dry_run=dry_run,
                )
                regular_invoices.append(
                    str(_("%(description)s für %(contract)s"))
                    % {"description": description, "contract": billing_contract_info}
                )

            if sum_nk_electricity > 0.0:
                description = "Strompauschale %02d.%d für %s%s" % (
                    month,
                    year,
                    "/".join(ru_list),
                    factor_txt,
                )
                invoice_value = sum_nk_electricity * factor
                add_invoice(
                    AccountKey.STROM,
                    invoice_category,
                    description,
                    invoice_date,
                    invoice_value,
                    book=book,
                    contract=billing_contract,
                    year=year,
                    month=month,
                    is_additional=is_additional_invoice,
                    dry_run=dry_run,
                )
                regular_invoices.append(
                    str(_("%(description)s für %(contract)s"))
                    % {"description": description, "contract": billing_contract_info}
                )

            ## Rent reduction
            if contract.rent_reduction:
                description = "Nettomietzinsreduktion %02d.%d für %s%s" % (
                    month,
                    year,
                    "/".join(ru_list),
                    factor_txt,
                )
                invoice_value = -1 * contract.rent_reduction * factor
                add_invoice(
                    AccountKey.RENT_REDUCTION,
                    invoice_category,
                    description,
                    invoice_date,
                    invoice_value,
                    book=book,
                    contract=billing_contract,
                    year=year,
                    month=month,
                    is_additional=is_additional_invoice,
                    dry_run=dry_run,
                )
                regular_invoices.append(
                    str(_("%(description)s für %(contract)s"))
                    % {"description": description, "contract": billing_contract_info}
                )
                rent_info.append(
                    {
                        "text": "Mietzinsreduktion",
                        "net": -1 * contract.rent_reduction,
                        "nk": "",
                        "total": -1 * contract.rent_reduction,
                    }
                )
                sum_rent_net -= contract.rent_reduction
                sum_rent_total -= contract.rent_reduction

            ## Rent reservation
            if contract.rent_reservation:
                description = "Mietzinsvorbehalt %02d.%d für %s%s" % (
                    month,
                    year,
                    "/".join(ru_list),
                    factor_txt,
                )
                invoice_value = -1 * contract.rent_reservation * factor
                add_invoice(
                    AccountKey.RENT_RESERVATION,
                    invoice_category,
                    description,
                    invoice_date,
                    invoice_value,
                    book=book,
                    contract=billing_contract,
                    year=year,
                    month=month,
                    is_additional=is_additional_invoice,
                    dry_run=dry_run,
                )
                regular_invoices.append(
                    str(_("%(description)s für %(contract)s"))
                    % {"description": description, "contract": billing_contract_info}
                )
                rent_info.append(
                    {
                        "text": "Mietzinsvorbehalt",
                        "net": -1 * contract.rent_reservation,
                        "nk": "",
                        "total": -1 * contract.rent_reservation,
                    }
                )
                sum_rent_net -= contract.rent_reservation
                sum_rent_total -= contract.rent_reservation

        invoice_title = "Mietzinsrechnung %02d.%d" % (month, year)
        if download_only:
            (ret, output_filename) = create_qrbill_rent(
                invoice_title,
                invoice_category,
                contract,
                rent_info,
                invoice_date,
                sum_rent_net,
                sum_nk,
                sum_rent_total,
                factor,
                dry_run=False,
                render=True,
                email_template=None,
                billing_contract=billing_contract,
            )
            if not output_filename:
                raise Http404(f"Konnte Rechnung nicht erzeugen: {invoice_title}: {' '.join(ret)}")
            return output_filename, messages
        elif (
            factor > 0 and sum_rent_total > 0.0 and contract.send_qrbill in ("only_next", "always")
        ):
            if dry_run and not single_contract:
                render = False
            else:
                render = True
            (ret, output_filename) = create_qrbill_rent(
                invoice_title,
                invoice_category,
                contract,
                rent_info,
                invoice_date,
                sum_rent_net,
                sum_nk,
                sum_rent_total,
                factor,
                dry_run=dry_run,
                render=render,
                email_template=invoice_category.email_template,
                billing_contract=billing_contract,
            )
            messages.extend(ret)
            if dry_run and single_contract:
                if not output_filename:
                    raise Http404(
                        f"Konnte Rechnung nicht erzeugen: {invoice_title}: {' '.join(ret)}"
                    )
                return output_filename, messages

        ## Continue with previous month
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
    return billed_months_count, regular_invoices, placeholder_invoices, messages


def pay_invoice(invoice, date, amount):
    return add_payment(date, amount, invoice.person, invoice=invoice)


def add_payment(date, amount, person, invoice=None, note=None, cash=False):
    if not invoice:
        return "Kein Rechnungstyp für diese Zahlung definiert."

    receivables = Account.from_settings(AccountKey.DEFAULT_RECEIVABLES)  ## Debitoren
    if cash:
        payment_account = Account.from_settings(AccountKey.CASH)
    else:
        payment_account = Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL)
    if note:
        description = f"Zahlung: {note} {invoice.invoice_category} {invoice.id}"
    else:
        description = f"Zahlung {invoice.invoice_category} {invoice.id}"
    try:
        with AccountingManager() as book:
            add_invoice_obj(
                book,
                "Payment",
                invoice.invoice_category,
                description,
                person,
                payment_account,
                receivables,
                date,
                amount,
                invoice.contract,
                invoice.year,
                invoice.month,
            )
    except Exception as e:
        return f"Konnte Rechnung nicht erstellen: {e}"


def get_income_account(invoice_category, account_key, contract=None):
    if account_key in settings.FINANCIAL_ACCOUNTS:
        account = Account.from_settings(account_key)
    else:
        account = Account(
            name="Ertrag aus Rechnung",
            prefix=invoice_category.income_account,
            building_based=invoice_category.income_account_building_based,
        )
    return setup_account(account, contract)


def get_receivables_account(invoice_category, contract=None):
    account = Account(
        name="Forderungen aus Rechnung",
        prefix=invoice_category.receivables_account,
        building_based=invoice_category.receivables_account_building_based,
    )
    return setup_account(account, contract)


def setup_account(account, contract):
    if account.building_based and contract and contract.rental_units.exists():
        ## Use first rental unit's building accounting postfix
        ru = contract.rental_units.all().first()
        if ru.building:
            account.set_code(building=ru.building)
        else:
            logger.error(
                f"Could not find building for contract id {contract.pk}, "
                f" using default account with no postfix {account.prefix}."
            )
            send_error_mail(
                "get_income_account_code()",
                f"Could not find building for contract id {contract.pk}, "
                f"using default account with no postfix {account.prefix}.",
            )
    return account


def add_invoice(
    account_key,
    invoice_category,
    description,
    date,
    amount,
    book=None,
    address=None,
    contract=None,
    year=None,
    month=None,
    is_additional=False,
    dry_run=False,
    comment="",
):
    if contract:
        if address:
            raise InvoiceCreationError("Can't specify address AND contract.")
        address = contract.get_contact_address()

    income_account = get_income_account(invoice_category, account_key, contract)
    receivables = get_receivables_account(invoice_category, contract)

    if not book:
        messages = []
        with AccountingManager(messages) as book:
            if not book:
                raise InvoiceCreationError(f"Can't open accounting book: {messages[-1]}")

        return add_invoice_obj(
            book,
            "Invoice",
            invoice_category,
            description,
            address,
            income_account,
            receivables,
            date,
            amount,
            contract=contract,
            year=year,
            month=month,
            is_additional=is_additional,
            dry_run=dry_run,
            comment=comment,
        )
    return add_invoice_obj(
        book,
        "Invoice",
        invoice_category,
        description,
        address,
        income_account,
        receivables,
        date,
        amount,
        contract=contract,
        year=year,
        month=month,
        is_additional=is_additional,
        dry_run=dry_run,
        comment=comment,
    )


## Convention for invoice types:
## - Invoice:
#      - acc_debit = receivables account (Debitoren)
#      - acc_credit = revenue account (e.g. Mieteinnamhen)
## - Payment:
#      - acc_debit = payment account (e.g. Bank)
#      - acc_credit = receivables (Debitoren)
def add_invoice_obj(
    book: AccountingBook,
    invoice_type,
    invoice_category,
    description,
    person,
    account: Account,
    receivables_account: Account,
    date,
    amount,
    contract=None,
    year=None,
    month=None,
    is_additional=False,
    transaction_id="",
    reference_nr="",
    additional_info="",
    dry_run=False,
    comment="",
):
    """Add Invoice object and transaction to the accounting book.

    :param account: Revenue account for invoices (credit) or bank account for payments (debit).
    :param receivables_account: Receivables account for invoices (debit) or payments (credit).
    """
    amount_dec = Decimal(str(amount))
    if invoice_type == "Invoice":
        acc_debit = receivables_account
        acc_credit = account  # revenue account
    elif invoice_type == "Payment":
        acc_debit = account  # bank account
        acc_credit = receivables_account
    else:
        raise InvoiceCreationError(f"Invoice type {invoice_type} is not implemented.")

    if dry_run:
        return None

    if transaction_id:
        ## Check if invoice exists already
        if Invoice.objects.filter(transaction_id=transaction_id).count():
            raise DuplicateInvoiceError(
                f"Invoice with transaction ID {transaction_id} exists already."
            )

    if contract:
        txn_description = "%s [%s]" % (description, contract.get_contract_label())
        person = None
    elif person:
        txn_description = "%s [%s]" % (description, person)
    else:
        raise InvoiceCreationError("add_invoice_obj: need contract OR person.")

    if comment:
        txn_description = "%s: %s" % (txn_description, comment)

    try:
        invoice = Invoice(
            name=description,
            invoice_type=invoice_type,
            invoice_category=invoice_category,
            year=year,
            month=month,
            is_additional_invoice=is_additional,
            contract=contract,
            person=person,
            date=date,
            amount=amount_dec,
            transaction_id=transaction_id,
            reference_nr=reference_nr,
            additional_info=additional_info,
            comment=comment,
        )
        fin_transaction_ref = book.add_transaction(
            amount_dec, acc_debit, acc_credit, date, txn_description, autosave=False
        )
        invoice.fin_transaction_ref = fin_transaction_ref
        invoice.fin_account = account.code
        invoice.fin_account_receivables = receivables_account.code
    except Exception as e:
        raise InvoiceCreationError(f"Could not create invoice or transaction: {e}")

    try:
        invoice.save()
    except Exception as e:
        raise InvoiceCreationError(f"Could not save the invoice: {e}")
    try:
        book.save()
    except Exception as e:
        ## Roll back the invoice creation
        try:
            invoice.delete()
        except Exception as rollback_exception:
            raise InvoiceCreationError(
                f"Could not save the transaction: {e} "
                f"AND THE ROLLBACK FAILED: {rollback_exception}"
            )
        raise InvoiceCreationError(f"Could not save the transaction: {e}")
    return invoice


def delete_invoice_transaction(invoice):
    if not invoice.fin_transaction_ref:
        logger.warning(f"Trying to delete an invoice without a fin_transaction_ref: {invoice.pk}")
        return None
    try:
        book_type_id, db_id, _ = AccountingBook.decode_transaction_id(invoice.fin_transaction_ref)
        with AccountingManager(book_type_id=book_type_id, db_id=db_id) as book:
            book.delete_transaction(invoice.fin_transaction_ref)
    except Exception:
        logger.error(
            f"Could not delete transaction {invoice.fin_transaction_ref} "
            f"linked to invoice {invoice.pk}."
        )
        send_error_mail(
            "delete_invoice_transaction()",
            f"Could not delete transaction {invoice.fin_transaction_ref} "
            f"linked to invoice {invoice.pk}.",
        )
        return None
    logger.info(
        f"Deleted fin_transaction_ref {invoice.fin_transaction_ref} for invoice {invoice.pk}."
    )
    return None


def invoice_overview(filters=None):
    if filters is None:
        filters = {"category_filter": "_all"}
    data = []
    row = {}
    query = Invoice.objects.filter(active=True)

    ## Consolidated filter
    if "show_consolidated" not in filters or not filters["show_consolidated"]:
        query = query.filter(consolidated=False)

    ## Date filter
    if "date_from" in filters and filters["date_from"] != "":
        query = query.filter(
            date__gte=datetime.datetime.strptime(filters["date_from"], "%d.%m.%Y").date()
        )
    if "date_to" in filters and filters["date_to"] != "":
        query = query.filter(
            date__lte=datetime.datetime.strptime(filters["date_to"], "%d.%m.%Y").date()
        )

    ## InvoiceCategory filter
    contract_query = ()
    person_query = ()
    if "category_filter" in filters:
        if filters["category_filter"] in ("_all", "_contract"):
            contract_query = query.filter(contract__isnull=False)
        if filters["category_filter"] in ("_all", "_person"):
            person_query = query.filter(person__isnull=False)
        if filters["category_filter"][0] != "_":
            ic = InvoiceCategory.objects.filter(id=filters["category_filter"]).first()
            if ic:
                if ic.linked_object_type == "Contract":
                    contract_query = query.filter(invoice_category=ic)
                else:
                    person_query = query.filter(invoice_category=ic)

    ## Text search
    if "search" in filters:
        search = filters["search"]
        if contract_query:
            contract_query = contract_query.filter(
                Q(contract__contractors__organization__icontains=search)
                | Q(contract__contractors__name__icontains=search)
                | Q(contract__contractors__first_name__icontains=search)
                | Q(contract__rental_units__name__icontains=search)
            )
        if person_query:
            person_query = person_query.filter(
                Q(person__organization__icontains=search)
                | Q(person__name__icontains=search)
                | Q(person__first_name__icontains=search)
            )
    ## Order and distinct for many-to-many joins
    if contract_query:
        # contract_query = contract_query.order_by('contract__rental_units__name','contract__id', 'date').distinct()
        contract_query = contract_query.order_by("contract__id", "date").distinct()
    if person_query:
        person_query = person_query.order_by("person__id", "date").distinct()

    ## Contract-invoices
    last_contract = None
    for invoice in contract_query:
        if invoice.contract != last_contract:
            if last_contract is not None:
                data.append(row)
            name = str(invoice.contract)
            row = {
                "obj": invoice.contract,
                "name": name,
                "total_billed": 0,
                "total_paid": 0,
                "total": 0,
                "open_bill_date": None,
                "last_payment_date": None,
            }
            last_contract = invoice.contract
        if invoice.invoice_type == "Invoice":
            row["total_billed"] += invoice.amount
            row["total"] += invoice.amount
            if not row["open_bill_date"] and not invoice.consolidated:
                row["open_bill_date"] = invoice.date
        elif invoice.invoice_type == "Payment":
            row["total_paid"] += invoice.amount
            row["total"] -= invoice.amount
            row["last_payment_date"] = invoice.date
        else:
            raise RuntimeError("Unknown invoice_type: %s" % invoice.invoice_type)
    if last_contract is not None:
        data.append(row)

    ## Person invoices
    last_person = None
    for invoice in person_query:
        if invoice.person != last_person:
            if last_person is not None:
                data.append(row)
            name = str(invoice.person)
            row = {
                "obj": invoice.person,
                "name": name,
                "total_billed": 0,
                "total_paid": 0,
                "total": 0,
                "open_bill_date": None,
                "last_payment_date": None,
            }
            last_person = invoice.person
        if invoice.invoice_type == "Invoice":
            row["total_billed"] += invoice.amount
            row["total"] += invoice.amount
            if not row["open_bill_date"] and not invoice.consolidated:
                row["open_bill_date"] = invoice.date
        elif invoice.invoice_type == "Payment":
            row["total_paid"] += invoice.amount
            row["total"] -= invoice.amount
            row["last_payment_date"] = invoice.date
        else:
            raise RuntimeError("Unknown invoice_type: %s" % invoice.invoice_type)
    if last_person is not None:
        data.append(row)
    return data


def invoice_detail(obj, filters=None):
    if filters is None:
        filters = {"category_filter": "_all"}
    data = []
    balance = 0
    query = Invoice.objects.filter(active=True)
    if type(obj) is Contract:
        query = query.filter(contract=obj)
    else:
        query = query.filter(person=obj)

    if "search_detail" in filters:
        search = filters["search_detail"]
        query = query.filter(
            Q(name__icontains=search)
            | Q(reference_nr__icontains=search)
            | Q(additional_info__icontains=search)
            # Q(id=search)
            # Q(amount=Decimal(search)) |
            # Q(date=datetime.datetime.strptime(search, "%d-%m-%Y").date())
        )
    if "show_consolidated" not in filters or not filters["show_consolidated"]:
        query = query.filter(consolidated=False)

    if "date_from" in filters and filters["date_from"] != "":
        query = query.filter(
            date__gte=datetime.datetime.strptime(filters["date_from"], "%d.%m.%Y").date()
        )
    if "date_to" in filters and filters["date_to"] != "":
        query = query.filter(
            date__lte=datetime.datetime.strptime(filters["date_to"], "%d.%m.%Y").date()
        )

    if "category_filter" in filters and filters["category_filter"][0] != "_":
        ic = InvoiceCategory.objects.filter(id=filters["category_filter"]).first()
        if ic:
            query = query.filter(invoice_category=ic)

    for invoice in query.order_by("date"):
        billed = ""
        paid = ""
        if invoice.invoice_type == "Invoice":
            billed = invoice.amount
            balance += invoice.amount
        elif invoice.invoice_type == "Payment":
            paid = invoice.amount
            balance -= invoice.amount
        else:
            raise RuntimeError("Unknown invoice_type: %s" % invoice.invoice_type)
        if invoice.consolidated:
            txt_consolidated = "✓"
        else:
            txt_consolidated = " "
        row = {
            "obj": invoice,
            "date": invoice.date,
            "number": invoice.id,
            "note": invoice.name,
            "billed": billed,
            "paid": paid,
            "balance": balance,
            "consolidated": txt_consolidated,
            "extra_info": invoice.additional_info,
        }
        data.insert(0, row)
    return data


## TODO: Reset consolidated flags when a consolidated entry is deleted/changed!
## TODO: Add filter to consolidate only part of invoices (really needed?)
def consolidate_invoices(obj=None):
    ## Consolidate by invoice_category and person/contract (TODO: also by reference_nr?)

    ## If called for an object (person or contract): invalidate all invoices an re-consolidate
    if obj:
        if type(obj) is Contract:
            invoice_categories = InvoiceCategory.objects.filter(linked_object_type="Contract")
            Invoice.objects.filter(consolidated=True).filter(contract=obj).update(
                consolidated=False
            )
            invoice_base = Invoice.objects.filter(contract=obj)
        else:
            invoice_categories = InvoiceCategory.objects.filter(linked_object_type="Address")
            Invoice.objects.filter(consolidated=True).filter(person=obj).update(consolidated=False)
            invoice_base = Invoice.objects.filter(person=obj)
    else:
        invoice_categories = InvoiceCategory.objects.all()
        invoice_base = Invoice.objects.all()

    for category in invoice_categories:
        if category.linked_object_type == "Contract":
            obj_order = "contract__id"
        else:
            obj_order = "person__id"

        last_obj = None
        to_consolidate_invoice = []
        to_consolidate_payment = []
        for invoice in (
            invoice_base.filter(consolidated=False)
            .filter(invoice_category=category)
            .order_by(obj_order, "date")
        ):
            if category.linked_object_type == "Contract" and invoice.contract != last_obj:
                consolidate_invoice_lists(to_consolidate_invoice, to_consolidate_payment)
                last_obj = invoice.contract
                # print("New contract: %s" % last_obj)
                to_consolidate_invoice = []
                to_consolidate_payment = []
            elif category.linked_object_type == "Address" and invoice.person != last_obj:
                consolidate_invoice_lists(to_consolidate_invoice, to_consolidate_payment)
                last_obj = invoice.person
                # print("New person: %s" % last_obj)
                to_consolidate_invoice = []
                to_consolidate_payment = []
            if invoice.invoice_type == "Payment":
                to_consolidate_payment.append(invoice)
            else:
                to_consolidate_invoice.append(invoice)
        consolidate_invoice_lists(to_consolidate_invoice, to_consolidate_payment)


def consolidate_invoice_lists(invoices, payments):
    total_invoice = 0
    total_payment = 0
    to_consolidate = []
    while len(invoices) or len(payments):
        if (len(invoices) and total_invoice < total_payment) or not len(payments):
            current = invoices.pop(0)
            total_invoice += current.amount
            # print("  total_invoice = %s" % total_invoice)
        else:
            current = payments.pop(0)
            total_payment += current.amount
            # print("  total_payment = %s" % total_payment)
        to_consolidate.append(current)

        if total_invoice == total_payment:
            ## Consolidate
            # print("  total_invoice == total_payment => CONSOLIDATE")
            for ic in to_consolidate:
                # print("     - %s: %s %s" % (ic.name,ic.invoice_type,ic.amount))
                ic.consolidated = True
                ic.save()
            total_invoice = 0
            total_payment = 0
            to_consolidate = []


def guess_transaction(transaction):
    initial = {
        "date": transaction["date"],
        "process": False,
        "name": None,
        "save_sender": "IGNORE",
        "note": transaction["note"],
        "amount": float(transaction["amount"]),
        "guess_sender_state": 0,
    }

    if transaction["person"] and transaction["person"].startswith("TWINT"):
        ## TWINT payment -> Kiosk
        initial["transaction"] = "kiosk_payment"
        initial["process"] = True
        return initial

    ## Try to get name from lookup table (from more specific to less specific combos)
    lookups = [
        "%s__CHF%s__N:%s" % (transaction["person"], transaction["amount"], transaction["note"]),
        "%s__N:%s" % (transaction["person"], transaction["note"]),
        "%s__CHF%s" % (transaction["person"], transaction["amount"]),
        "%s" % (transaction["person"]),
    ]
    lu = None
    for key in lookups:
        lu = LookupTable.objects.filter(name=key, lookup_type="payment_sender").first()
        if lu:
            try:
                initial["name"] = Address.objects.get(pk=lu.value)
                initial["guess_sender_state"] = 1
                break
            except Address.DoesNotExist:
                lu.delete()

    if settings.GENO_ID == "Warmbaechli":
        if transaction["amount"] == 80.00:
            initial["transaction"] = "memberfee"
            initial["process"] = True
        elif (
            transaction["amount"] >= 400.00
            and transaction["amount"] <= 3000.00
            and (transaction["amount"] % 200.00 == 0.0)
        ):
            ## Eintrittsgebühr 200.- + n x 200.- Anteilscheine
            initial["transaction"] = "entry_as"
            initial["process"] = True
        elif transaction["amount"] > 3000.00 and (transaction["amount"] % 200.00 == 0.0):
            initial["transaction"] = "share_as"
            initial["process"] = True
        elif transaction["amount"] > 0.00:
            initial["process"] = True
        if not initial["name"]:
            initial["name"] = guess_name_fuzzy(transaction)
            initial["guess_sender_state"] = 2
    elif transaction["amount"] > 0.00 and transaction["type"]:
        initial["transaction"] = "invoice_payment"
        initial["process"] = True
        if not initial["name"]:
            initial["name"] = guess_name_strict(transaction)
            initial["guess_sender_state"] = 2

    if not initial["name"]:
        initial["guess_sender_state"] = 0

    if initial["guess_sender_state"] != 1:
        initial["save_sender"] = transaction["person"]

    return initial


def guess_name_strict(transaction):
    if not transaction["person"]:
        return None

    ## Try to get exact match on name
    parts = re.split(" ", transaction["person"])
    c = Address.objects.filter(first_name__iexact=parts[0]).filter(name__iexact=parts[1])
    if c.count() == 1:
        return c.first()
    c = Address.objects.filter(first_name__iexact=parts[1]).filter(name__iexact=parts[0])
    if c.count() == 1:
        return c.first()

    parts = re.split(
        " ", transaction["person"].replace("ae", "ä").replace("ue", "ü").replace("oe", "ö")
    )
    c = Address.objects.filter(first_name__iexact=parts[0]).filter(name__iexact=parts[1])
    if c.count() == 1:
        return c.first()
    c = Address.objects.filter(first_name__iexact=parts[1]).filter(name__iexact=parts[0])
    if c.count() == 1:
        return c.first()

    ## Try more complex name matching
    for a in Address.objects.all():
        if a.name and a.first_name:
            s = "%s %s" % (a.first_name, a.name)
            p = re.compile("^%s" % re.escape(s), re.IGNORECASE)
            if p.match(transaction["person"]):
                return a
        if a.organization:
            p = re.compile("^%s" % re.escape(a.organization), re.IGNORECASE)
            if p.match(transaction["person"]):
                return a


def guess_name_fuzzy(transaction):
    if not transaction["person"]:
        return None

    ## Try to guess name
    ignore_words = re.compile("^(?:und|der|die|das|von|vom|für)$", re.IGNORECASE)
    search_words = ""
    if transaction["note"] and transaction["person"]:
        search_words = "%s %s" % (transaction["note"], transaction["person"])
    elif transaction["person"]:
        search_words = transaction["person"]
    parts = re.split(r" |\+|\*|,|:|\.|;|-|_|/|\\\\", search_words)  # search_words.split(' ')
    c = Address.objects
    for part in parts:
        part = part.strip()
        if len(part) < 3 or ignore_words.match(part):
            # print("Ignoring part: %s" % part)
            continue
        c_old = c
        if len(part) > 5:
            c = c_old.filter(
                Q(name__icontains=part) | Q(first_name__icontains=part) | Q(street__icontains=part)
            )
        else:
            c = c_old.filter(Q(name__iexact=part) | Q(first_name__iexact=part))
        n = c.count()
        # print("Search '%s' -> %d matches" % (part, n))
        if n == 1:
            return c.first()
        elif n == 0:
            ## Backtrack
            c = c_old
    return None


def process_transaction(transaction_type, date, address, amount, save_sender=None, note=None):
    if save_sender and save_sender != "IGNORE" and len(save_sender) > 5 and address and address.pk:
        try:
            lu = LookupTable.objects.get(name=save_sender, lookup_type="payment_sender")
        except LookupTable.DoesNotExist:
            lu = LookupTable(name=save_sender, lookup_type="payment_sender")
        lu.value = address.pk
        lu.save()

    if transaction_type == "invoice_payment":
        return add_payment(date, amount, address, invoice=None, note=note)
    if transaction_type == "cash_payment":
        return add_payment(date, amount, address, invoice=None, note=note, cash=True)

    try:
        with AccountingManager() as book:
            if transaction_type == "share_as":
                add_transaction_shares(book, date, amount, address)
            elif transaction_type == "share_as_inv":
                add_transaction_shares(book, date, amount, address, use_clearing=True)
            elif transaction_type == "entry_as":
                add_transaction_shares_entry(book, date, amount, address)
            elif transaction_type == "entry_as_inv":
                add_transaction_shares_entry(book, date, amount, address, use_clearing=True)
            elif transaction_type == "loan_interest_todeposit":
                add_transaction_interest(book, date, amount, address, book_to="deposit")
            elif transaction_type == "loan_interest_toloan":
                add_transaction_interest(book, date, amount, address, book_to="loan")
            elif transaction_type == "memberfee":
                add_transaction_memberfee(book, date, amount, address)
            elif transaction_type == "kiosk_payment":
                add_transaction_kiosk(book, date, amount, note)
            else:
                raise ValueError(f"Transaktionstyp '{transaction_type}' nicht implementiert.")
            book.save()
    except Exception as e:
        return f"Konnte Transaktion nicht erstellen: {e}"


def add_transaction_shares(book: AccountingBook, date, amount, address, use_clearing=False):
    ## Genossenschaftsanteile Mitglieder
    share_as_account = Account.from_settings(AccountKey.SHARES_MEMBERS)
    if use_clearing:
        ## Hilfskonto für Beteiligungs-Rechnungen, die erst bei Zahlung auf das definitive
        ## Konto gebucht werden.
        payment_account = Account.from_settings(AccountKey.SHARES_CLEARING)
    else:
        payment_account = Account.from_settings(AccountKey.SHARES_DEBTOR_MANUAL)

    if float(amount) % 200.00 != 0.0:
        raise ValueError("Share is not a multiple of 200.-!")
    count = int(amount / 200)
    if count == 1:
        text_as = "1 Anteilschein"
    else:
        text_as = "%d Anteilscheine" % count
    share = Share(
        name=address,
        share_type=ShareType.objects.get(name="Anteilschein"),
        state="bezahlt",
        date=date,
        quantity=count,
        value=200,
    )
    description = f"{text_as} {address}"
    book.add_transaction(
        amount, payment_account, share_as_account, date, description, autosave=False
    )
    share.save()


def add_transaction_shares_entry(book: AccountingBook, date, amount, address, use_clearing=False):
    ## Genossenschaftsanteile Mitglieder
    share_as_account = Account.from_settings(AccountKey.SHARES_MEMBERS)
    ## Beitrittsgebühren
    entryfee_account = Account.from_settings(AccountKey.MEMBER_FEE_ONETIME)
    if use_clearing:
        ## Hilfskonto für Beteiligungs-Rechnungen, die erst bei Zahlung auf das definitive
        ## Konto gebucht werden.
        payment_account = Account.from_settings(AccountKey.SHARES_CLEARING)
    else:
        payment_account = Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL)

    split1 = 200
    split2 = amount - split1
    count = int(split2 / 200)
    if split2 != count * 200:
        raise ValueError(f"Betrag ist kein Vielfaches von 200: {amount}")
    if count == 1:
        text_as = "1 Anteilschein"
    else:
        text_as = "%d Anteilscheine" % count
    if count != 0:
        share = Share(
            name=address,
            share_type=ShareType.objects.get(name="Anteilschein"),
            state="bezahlt",
            date=date,
            quantity=count,
            value=200,
        )

    att = MemberAttribute(
        member=Member.objects.get(name=address),
        date=date,
        attribute_type=MemberAttributeType.objects.get(name="Mitgliederbeitrag %s" % date.year),
        value="Bezahlt (mit Eintritt)",
    )

    splits = [
        Split(account=entryfee_account, amount=-split1),
        Split(account=payment_account, amount=amount),
    ]
    if split2:
        splits.append(Split(account=share_as_account, amount=-split2))
    description = f"{text_as} und Beitrittsgebühr, {address}"
    book.add_split_transaction(
        Transaction(splits=splits, date=date, description=description), autosave=False
    )

    if count != 0:
        share.save()
    att.save()


def add_transaction_interest(book: AccountingBook, date, amount, address, book_to):
    ## Verbindlichkeiten aus Finanzierung
    interest_account = Account.from_settings(AccountKey.SHARES_INTEREST)

    if book_to == "loan":
        text = "Anrechnung Darlehenszins an Darlehen"
        stype = ShareType.objects.get(name="Darlehen verzinst")
        shares_account = Account.from_settings(AccountKey.SHARES_LOAN_INTEREST)
    elif book_to == "deposit":
        text = "Anrechnung Darlehenszins an Depositenkasse"
        stype = ShareType.objects.get(name="Depositenkasse")
        shares_account = Account.from_settings(AccountKey.SHARES_DEPOSIT)
    else:
        raise ValueError(f"Invalid value for book_to: {book_to}")
    share = Share(
        name=address,
        share_type=stype,
        state="bezahlt",
        date=date,
        quantity=1,
        value=amount,
        is_interest_credit=True,
        note=text,
    )
    description = f"{text}, {address}"
    book.add_transaction(
        amount, interest_account, shares_account, date, description, autosave=False
    )
    share.save()


def add_transaction_memberfee(book: AccountingBook, date, amount, address):
    payment_account = Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL)
    fee_year = datetime.datetime.today().year
    memberfee_account = Account.from_settings(AccountKey.MEMBER_FEE)
    member_attribute_name = f"Mitgliederbeitrag {fee_year}"
    try:
        att_type = MemberAttributeType.objects.get(name=member_attribute_name)
    except MemberAttributeType.DoesNotExist:
        raise ValueError(f"Mitglieder Attribut '{member_attribute_name}' existiert nicht.")

    member = Member.objects.get(name=address)
    att = MemberAttribute.objects.filter(member=member, attribute_type=att_type)
    if len(att) == 0:
        att = MemberAttribute(member=member, attribute_type=att_type)
    elif len(att) == 1:
        att = att[0]
        if att.value.startswith("Bezahlt"):
            raise ValueError("Ist bereits als bezahlt markiert")
        elif (
            att.value != "Mail-Rechnung geschickt"
            and att.value != "Mail-Reminder geschickt"
            and att.value != "Brief-Rechnung geschickt"
            and att.value != "Brief-Reminder geschickt"
            and att.value != "Brief-Mahnung geschickt"
            and att.value != "Brief-Mahnung2 geschickt"
        ):
            raise ValueError(f"Unbekannter Wert für Attribut '{member_attribute_name}'")
    else:
        raise ValueError(f"Mehr als ein Attribut '{member_attribute_name}' gefunden.")

    description = f"Mitgliederbeitrag {fee_year}, {address}"
    book.add_transaction(
        amount, payment_account, memberfee_account, date, description, autosave=False
    )
    att.value = "Bezahlt"
    att.date = date
    att.save()


def add_transaction_kiosk(book: AccountingBook, date, amount, note=None):
    payment_account = Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL)
    income_account = Account.from_settings(AccountKey.KIOSK)
    desc = "Kiosk/Twint"
    if note:
        desc = "%s: %s" % (desc, note)
    book.add_transaction(amount, payment_account, income_account, date, desc, autosave=False)


def process_sepa_transactions(data):
    errors = []
    skipped = []
    success = []
    for item in data["log"]:
        logger.info("%s: %s" % (item["info"], "/".join(item["objects"])))

    with AccountingManager(data["log"]) as book:
        if book:
            for tx in data["transactions"]:
                add_sepa_transaction(book, tx, errors, skipped, success)
        else:
            errors.append("Kann Buchhaltung nicht öffnen!")

    return {"errors": errors, "skipped": skipped, "success": success, "log": data["log"]}


def add_sepa_transaction(book, tx, errors, skipped, success):
    # tx: 'id': tx_id, 'date': date, 'amount': amount, 'reference': reference_nr,
    #     'debtor': debtor, 'extra_info': additional_info, 'charges': charges
    addtl_info = []
    if tx.get("extra_info"):
        addtl_info.append(tx["extra_info"])
    if tx.get("debtor"):
        addtl_info.append(tx["debtor"])
    if tx.get("charges"):
        addtl_info.append("Charges: %s" % tx["charges"])
    bill_info = parse_reference_nr(tx["reference_nr"])
    if "error" in bill_info:
        errors.append(
            "Ungültige Referenznummer: %s für Buchung %s - CHF %s (Referenznr. %s, %s)"
            % (
                bill_info["error"],
                tx["date"],
                tx["amount"],
                tx["reference_nr"],
                "/".join(addtl_info),
            )
        )
        return
    if bill_info["person"]:
        bill_info_name = bill_info["person"]
    else:
        bill_info_name = bill_info["contract"]
    transaction_info_txt = "%s - CHF %s: %s [%s] (%s)" % (
        tx["date"],
        tx["amount"],
        bill_info["description"],
        bill_info_name,
        "/".join(addtl_info),
    )
    payment_account = None
    receivables_account = None
    try:
        for account in settings.FINANCIAL_ACCOUNTS.values():
            if account.get(
                "role", AccountRole.DEFAULT
            ) == AccountRole.QR_DEBTOR and normalize_iban(tx["account"]) in (
                normalize_iban(account.get("iban", "-")),
                normalize_iban(account.get("account_iban", "-")),
            ):
                payment_account = Account.from_settings_dict(account)
                break
        if not payment_account:
            raise Exception(f"IBAN {tx['account']} nicht gefunden in settings.FINANCIAL_ACCOUNTS")
        receivables_account = Account(
            name="Debitoren von Rechnung",
            prefix=bill_info["receivables_account"],
        )
    except Exception as e:
        errors.append(
            "Buchhaltungs-Konten nicht gefunden: %s/%s (%s) [%s]"
            % (tx["account"], bill_info["receivables_account"], e, transaction_info_txt)
        )
        return

    try:
        add_invoice_obj(
            book,
            "Payment",  # invoice_type,
            bill_info["invoice_category"],
            bill_info["description"],
            bill_info["person"],
            payment_account,
            receivables_account,
            tx["date"],
            tx["amount"],
            contract=bill_info["contract"],
            year=None,
            month=None,
            transaction_id=tx["id"],
            reference_nr=tx["reference_nr"],
            additional_info="/".join(addtl_info),
            dry_run=False,
        )
    except DuplicateInvoiceError:
        skipped.append(
            f"Buchung mit Transaktions-ID {tx['id']} existiert bereits ({transaction_info_txt})"
        )
    except Exception as e:
        errors.append(f"Buchung konnte nicht ausgeführt werden: {e} {transaction_info_txt}")
    else:
        success.append(transaction_info_txt)


## Get invoice/bill info based on reference number
## Reference number structure:
## NN          - Invoice category object ID (1-89) OR reserved/hard-coded invoice categories (90-98) OR test/dummy (99)
## NNNNN NNNNN - ID1
## NNNNN NNNNN - Object ID
## NNNN        - ID2
def parse_reference_nr(refnr):
    if not esr.is_valid(refnr):
        return {"error": "Ungültige Prüfziffer"}
    refnr = esr.compact(refnr)
    invoice_category_id = refnr[0:2]
    refnr_rest = refnr[2:]

    id1 = refnr_rest[0:10]
    object_id = refnr_rest[10:20]
    id2 = refnr_rest[20:24]

    extra_description = ""
    if id1 != "0000000000":
        extra_description = "%s/%s" % (extra_description, id1)
    if id2 != "0000":
        extra_description = "%s/%s" % (extra_description, id2)

    ## Hard-coded invoice categories
    if int(invoice_category_id) >= 90:
        if int(invoice_category_id) == 90:
            ## App specific reference number: ID2=application ID; ID1 and object_id are app specific
            if int(id2) in geno_settings.REFERENCE_NR_APPS:
                bill_info = {
                    "ref_type": "app",
                    "invoice_category": None,
                    "app_id": int(id2),
                    "app_name": geno_settings.REFERENCE_NR_APPS[int(id2)],
                    "id1": id1,
                    "object_id": object_id,
                }
                return bill_info
            else:
                return {"error": "Ungültige app_id: %s" % id2}
        return {"error": "Ungültige invoice_category_id: %s" % invoice_category_id}

    ## "Dynamic" invoice categories
    try:
        invoice_category = InvoiceCategory.objects.get(reference_id=int(invoice_category_id))
    except Exception as e:
        return {"error": "Ungültiger Rechnungstyp: %s (%s)" % (invoice_category_id, e)}

    bill_info = {
        "ref_type": "invoice",
        "invoice_category": invoice_category,
        "description": "Einzahlung %s%s" % (invoice_category.name, extra_description),
        "contract": None,
        "person": None,
        "receivables_account": invoice_category.receivables_account,
    }

    if invoice_category.linked_object_type == "Address":
        try:
            bill_info["person"] = Address.objects.get(id=int(object_id))
        except Address.DoesNotExist:
            return {"error": "Ungültige Adressen-ID"}
    elif invoice_category.linked_object_type == "Contract":
        try:
            bill_info["contract"] = Contract.objects.get(id=int(object_id))
        except Contract.DoesNotExist:
            return {"error": "Ungültige Vertrags-ID"}
        bill_info["description"] = "%s %s" % (
            bill_info["description"],
            bill_info["contract"].list_rental_units(short=True),
        )
    else:
        return {
            "error": "Rechnung mit unbekanntem Objekt verknüpft: %s"
            % invoice_category.linked_object_type
        }

    return bill_info


## Get reference number based on InvoiceCategory and Object
def get_reference_nr(invoice_category, object_id, extra_id1=0, extra_id2=0, app_name=""):
    reference_id = 99  ## Test/Dummy ID
    if isinstance(invoice_category, str):
        if invoice_category == "app":
            reference_id = 90
            if extra_id2 != 0:
                raise RuntimeError(
                    "get_reference_nr(): extra_id2 cannot be used for app specific reference numbers."
                )
            for key in geno_settings.REFERENCE_NR_APPS:
                if app_name == geno_settings.REFERENCE_NR_APPS[key]:
                    extra_id2 = key
                    break
            if not extra_id2:
                raise RuntimeError("get_reference_nr(): id2 for app %s not found." % app_name)
        else:
            raise RuntimeError(
                "get_reference_nr(): unknown invoice_category: %s" % invoice_category
            )
    elif invoice_category:
        ## "Dynamic" invoices
        reference_id = invoice_category.reference_id

    id1 = int(extra_id1)
    if id1 < 0 or id1 > 9999999999:
        raise RuntimeError("get_reference_nr(): extra_id1 must be between 0 and 9'999'999'999")
    id2 = int(extra_id2)
    if id2 < 0 or id2 > 9999:
        raise RuntimeError("get_reference_nr(): extra_id2 must be between 0 and 9999")
    ref_number = "%02d %010d %010d %04d" % (reference_id, id1, object_id, id2)
    ref_number = esr.format("%s%s" % (ref_number, esr.calc_check_digit(ref_number)))
    return ref_number


def create_qrbill(
    ref_number,
    address,
    context,
    output_filename,
    render=False,
    email_template=None,
    email_subject=None,
    dry_run=True,
):
    if render:
        context["qr_account"] = settings.FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["iban"]
        context["qr_ref_number"] = ref_number
        context["qr_debtor"] = address
        try:
            invoice_doctype = DocumentType.objects.get(name="invoice")
            render_qrbill(invoice_doctype.template, context, output_filename)
        except Exception as e:
            logger.error(f"Could not render QR bill: {e}")
            return (
                [
                    "Konnte QR-Rechnung nicht erstellen: %s" % e,
                ],
                0,
                None,
            )

    messages = []
    mails_sent = 0
    mail_recipient = None
    if email_template:
        if settings.DEBUG or settings.DEMO:
            email_copy = None
        else:
            email_copy = settings.GENO_DEFAULT_EMAIL
        mail_recipient = address.get_mail_recipient()
        if not address.email:
            messages.append("KEIN EMAIL GESENDET! Grund: Keine Email-Adresse für %s" % (address))
        else:
            if render:
                if isinstance(email_template, str):
                    mail_template = loader.get_template("geno/%s" % email_template)
                    mail_text_html = mail_template.render(context)
                elif isinstance(email_template, ContentTemplate):
                    mail_template = email_template.get_template()
                    mail_text_html = mail_template.render(Context(context))
                else:
                    raise TypeError(f"Invalid type for email template: {type(email_template)}")
                mail_text = html2text(mail_text_html)
                email_sender = f'"{settings.GENO_NAME}" <{settings.SERVER_EMAIL}>'
                if email_copy:
                    bcc = [
                        email_copy,
                    ]
                else:
                    bcc = None
                try:
                    mail = EmailMultiAlternatives(
                        email_subject, mail_text, email_sender, [mail_recipient], bcc
                    )
                    attfile = open("/tmp/%s" % output_filename, "rb")
                    mail.attach(output_filename, attfile.read())  # , 'application/pdf')
                    attfile.close()
                    mail.attach_alternative(mail_text_html, "text/html")
                    # mail.content_subtype = "html"  # Main content is now text/html
                    if dry_run:
                        mails_sent = 1
                    else:
                        mails_sent = mail.send()

                except SMTPException as e:
                    messages.append(
                        "Konnte mail an %s nicht schicken!!! SMTP-Fehler: %s"
                        % (escape(mail_recipient), e)
                    )
                    mails_sent = 0
                except Exception as e:
                    messages.append(
                        "Konnte mail an %s nicht schicken!!! Allgemeiner Fehler: %s"
                        % (escape(mail_recipient), e)
                    )
                    mails_sent = 0
            else:
                mails_sent = 1

    return (messages, mails_sent, mail_recipient)


def create_qrbill_rent(
    title,
    invoice_category,
    contract,
    bill_info,
    invoice_date,
    sum_rent_net,
    sum_nk,
    sum_rent_total,
    factor,
    dry_run=False,
    render=False,
    email_template=None,
    billing_contract=None,
):
    if not billing_contract:
        billing_contract = contract

    if not dry_run:
        ## We need rendering if not doing a dry run
        render = True

    address = contract.get_contact_address()

    context = address.get_context()
    context["betreff"] = title
    context["contract_info"] = contract.get_contract_label()
    rent_info = []
    for item in bill_info:
        item["date"] = invoice_date.strftime("%d.%m.%Y")
        if item["net"]:
            item["net"] = nformat(item["net"] * factor)
        if item["nk"]:
            item["nk"] = nformat(item["nk"] * factor)
        if item["total"]:
            item["total"] = nformat(item["total"] * factor)
        rent_info.append(item)
    context["rent_info"] = rent_info
    context["s_rent_net"] = nformat(sum_rent_net * factor)
    context["s_rent_nk"] = nformat(sum_nk * factor)
    context["s_rent_total"] = nformat(sum_rent_total * factor)
    context["sect_rent"] = True

    context["extra_text"] = None
    context["invoice_date"] = invoice_date.strftime("%d.%m.%Y")
    context["invoice_duedate"] = None
    context["invoice_nr"] = None
    context["liegenschaft"] = contract.get_building_label()
    context["show_liegenschaft"] = bool(context["liegenschaft"])
    context["sect_generic"] = False
    context["generic_info"] = None
    context["s_generic_total"] = None

    ## Reoccuring rent bill, referenced to contract
    ref_number = get_reference_nr(invoice_category, billing_contract.id)
    output_filename = "Rechnung_Miete_%s_%s.pdf" % (
        invoice_date.strftime("%Y%m%d"),
        esr.compact(ref_number),
    )

    context["qr_amount"] = context["s_rent_total"]  # sum_rent_total*factor
    context["qr_extra_info"] = "Miete: %s" % invoice_date.strftime("%m.%Y")

    email_subject = "Mietzinsrechnung %s" % (invoice_date.strftime("%m.%Y"))
    (messages, mails_sent, mail_recipient) = create_qrbill(
        ref_number,
        address,
        context,
        output_filename,
        render,
        email_template,
        email_subject,
        dry_run,
    )
    if render and not os.path.isfile(f"/tmp/{output_filename}"):
        output_filename = None
        return messages, output_filename

    if email_template:
        if mails_sent == 1:
            if dry_run:
                preview_email_url = (
                    f'<a href="/geno/preview/?contract={contract.id}'
                    f'&invoice_category={invoice_category.id}" target="_blank" '
                    'class="text-primary-600 dark:text-primary-500"'
                    ">Mail-Text</a>"
                )
                preview_pdf_url = (
                    f'<a href="?single_contract={contract.id}'
                    f'&date={invoice_date.strftime("%Y-%m-%d")}" target="_blank" '
                    'class="text-primary-600 dark:text-primary-500"'
                    f">{output_filename}</a>"
                )
                messages.append(
                    f"{escape(mail_recipient)} - "
                    f"Vorschau: {preview_email_url} und Anhang {preview_pdf_url}"
                )
            else:
                messages.append("%s - %s" % (escape(mail_recipient), output_filename))
                if contract.send_qrbill == "only_next":
                    ## Disable sending for next bill
                    contract.send_qrbill = "none"
                    contract.save()
        else:
            output_filename = None
            messages.append("FEHLER beim Versenden des Emails.")

    return messages, output_filename


## Takes either a POD template or a base_pdf_file, output goes to /tmp/<output_pdf_file>
def render_qrbill(
    template, context, output_pdf_file, base_pdf_file=None, append_pdf_file=None, output_dir="/tmp"
):
    temp_files = []
    if template and not base_pdf_file:
        filename = fill_template_pod(template.file.path, context, output_format="odt")
        if not filename:
            raise RuntimeError("Could not fill template")
        base_pdf_file = odt2pdf(filename, "render_qrbill")
        temp_files.extend([filename, base_pdf_file])
    if not base_pdf_file:
        # raise RuntimeError("render_qrbill(): template or base_pdf_file needed!")
        base_pdf_file = f"{settings.BASE_DIR}/geno/assets/blank_page_A4.pdf"

    ensure_dir_exists(output_dir)

    if "qr_account" not in context:
        raise RuntimeError("render_qrbill(): 'qr_account' not found in context.")
    if "qr_ref_number" not in context:
        raise RuntimeError("render_qrbill(): 'qr_ref_number' not found in context.")
    if "qr_amount" not in context:
        raise RuntimeError("render_qrbill(): 'qr_amount' not found in context.")
    if "qr_extra_info" not in context:
        raise RuntimeError("render_qrbill(): 'qr_extra_info' not found in context.")
    if "qr_debtor" not in context:
        raise RuntimeError("render_qrbill(): 'qr_debtor' not found in context.")
    if "qr_creditor" not in context:
        context["qr_creditor"] = geno_settings.QRBILL_CREDITOR

    if "qr_amount" in context and context["qr_amount"] is not None:
        with contextlib.suppress(InvalidOperation):
            context["qr_amount"] = Decimal(context["qr_amount"]).quantize(
                Decimal(".01"), rounding=ROUND_HALF_UP
            )
    else:
        context["qr_amount"] = None

    if context["qr_extra_info"] is None:
        context["qr_extra_info"] = ""

    bill = QRBill(
        account=context["qr_account"],
        reference_number=context["qr_ref_number"],
        creditor=build_structured_qrbill_address(context["qr_creditor"]),
        debtor=build_structured_qrbill_address(context["qr_debtor"]),
        amount=context["qr_amount"],
        # due_date=YYYY-MM-DD,
        additional_information=context["qr_extra_info"],
        language="de",
        top_line=True,
        payment_line=True,
        font_factor=1,
    )

    with tempfile.TemporaryFile(encoding="utf-8", mode="r+") as temp:
        bill.as_svg(temp)
        temp.seek(0)
        drawing = svg2rlg(temp)

    qr_data = io.BytesIO()
    renderPDF.drawToFile(drawing, qr_data)
    qr_data.seek(0)

    ## Merge QR-Code PDF with last page of base PDF and append append_pdf_file (if any)
    pdfgen = PdfGenerator()
    pdfgen.append_pdf_file(base_pdf_file, qr_data)
    if append_pdf_file:
        pdfgen.append_pdf_file(append_pdf_file)
    pdfgen.write_file(f"{output_dir}/{output_pdf_file}")

    ## Cleanup
    remove_temp_files(temp_files)


def build_structured_qrbill_address(adr):
    if isinstance(adr, dict):
        ## Assume it's already built
        return adr
    if not isinstance(adr, Address):
        raise TypeError("Expecting an Address")
    if adr.organization:
        name = adr.organization
    elif adr.first_name:
        name = f"{adr.first_name} {adr.name}"
    else:
        name = adr.name
    country = transform_qrbill_country(adr.country)
    return {
        "name": name,
        "street": adr.street_name,
        "house_num": adr.house_number,
        "pcode": adr.city_zipcode,
        "city": adr.city_name,
        "country": country,
    }


def transform_qrbill_country(country):
    country = (country or "").strip()
    if country.lower() in ("schweiz", "suisse", "svizzera", "svizra", "switzerland"):
        return "CH"
    if country.lower() in (
        "fürstentum liechtenstein",
        "fuerstentum liechtenstein",
        "liechtenstein",
    ):
        return "LI"
    if country.lower() in ("deutschland", "germany"):
        return "DE"
    if country.lower() in ("österreich", "oesterreich", "austria"):
        return "AT"
    if country.lower() in ("frankreich", "france"):
        return "FR"
    if country.lower() in ("italien", "italia", "italy"):
        return "IT"
    if country.lower() in ("spanien", "españa", "espana", "spain"):
        return "ES"
    return country


def get_duplicate_invoices():
    ret = []
    duplicates = []
    for invoice in Invoice.objects.exclude(transaction_id__exact=""):
        if invoice.transaction_id in duplicates:
            ret.append(
                f"id: {invoice.id}, name: {invoice.name}, transaction_id: {invoice.transaction_id}, address: {invoice.person}"
            )
        else:
            duplicates.append(invoice.transaction_id)
    return ret


def normalize_iban(iban):
    if isinstance(iban, str):
        return iban.replace(" ", "")
    else:
        return None
