import contextlib
import datetime
import io
import logging
import re
import tempfile
import warnings
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template import Context, loader
from django.utils.html import escape
from html2text import html2text

## For GnuCash and interest calc.
from piecash import Split, Transaction, open_book

## For QR bill and svg -> pdf
from qrbill import QRBill
from reportlab.graphics import renderPDF
from sqlalchemy import exc as sa_exc
from stdnum.ch import esr
from svglib.svglib import svg2rlg

import geno.settings as geno_settings

## For PDF merging
from cohiva.utils.pdf import PdfGenerator

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


class DummyAccount:
    pass


class DummyBook:
    """Dummy book object to use if GnuCash is not enabled, i.e. settings.GNUCASH = False"""

    def open(self):
        pass

    def close(self):
        pass

    def save(self):
        pass

    def flush(self):
        pass

    def accounts(self, *args, **kwargs):
        return DummyAccount()


def create_invoices(dry_run=True, reference_date=None, single_contract=None, building_ids=None, download_only=None):
    messages = []
    book = get_book(messages)
    if not book:
        return messages

    if not reference_date:
        reference_date = datetime.datetime.today()
    count = 0

    if single_contract:
        contracts = Contract.objects.filter(id=single_contract)
    elif download_only:
        contracts = Contract.objects.filter(id=download_only)
    else:
        contracts = Contract.objects.filter(state="unterzeichnet")

    if building_ids:
        contracts = contracts.filter(rental_units__building__in=building_ids).distinct()

    invoice_category = InvoiceCategory.objects.get(
        reference_id=10
    )  # name="Mietzins wiederkehrend")

    for contract in contracts:
        ## Create monthly invoices starting from reference date
        month = reference_date.month
        year = reference_date.year
        stop = False
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

            if contract.date > invoice_date:
                stop = True
                invoice_date = datetime.date(year, month, 15)
                if contract.date <= invoice_date:
                    ## Mid-month start
                    factor = Decimal(0.5)
                else:
                    ## Contract is in future
                    factor = Decimal(0.0)

            if contract.date_end:
                if contract.date_end <= datetime.date(year, month, 1):
                    ## Contract has ended
                    factor = Decimal(0.0)
                elif contract.date_end <= datetime.date(year, month, 15):
                    ## Mid-month end
                    factor = Decimal(0.5)

            ## Use other billing contract if set (for reference number/accounting)
            if (
                factor > 0.0
                and contract.billing_contract
                and contract.billing_contract != contract
            ):
                billing_contract = contract.billing_contract
                billing_contract_info = "%s (Rechnungs-Vertrag: %s)" % (contract, billing_contract)
                is_additional_invoice = True
                ## Add dummy invoice to prevent creation of further invoices
                invoice = Invoice(
                    name="Platzhalter: Inkasso läuft über Vertrag %s" % (billing_contract),
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
                messages.append(
                    "Platzhalter-Montasrechnung %d.%d hinzugefügt: %s."
                    % (month, year, billing_contract_info)
                )
            else:
                billing_contract = contract
                billing_contract_info = "%s" % (contract)
                is_additional_invoice = False

            ## Get rental unit information
            sum_depot = 0
            sum_rent_total = 0
            sum_rent_net = 0
            sum_nk = 0
            sum_nk_electricity = 0
            ru_list = []
            rent_info = []
            rent_type = "rent"  # Wohnungen
            for ru in contract.rental_units.all():
                if ru.rental_type in ("Gewerbe", "Lager", "Hobby"):
                    rent_type = "rent_business"
                elif ru.rental_type == "Gemeinschaft":
                    rent_type = "rent_other"
                elif ru.rental_type == "Parkplatz":
                    rent_type = "rent_parking"
                if not ru.rent_netto:
                    ru.rent_netto = Decimal(0.0)
                if not ru.nk:
                    ru.nk = Decimal(0.0)
                if not ru.nk_electricity:
                    ru.nk_electricity = Decimal(0.0)
                if not ru.depot:
                    ru.depot = Decimal(0.0)
                sum_depot += ru.depot
                sum_rent_total += ru.rent_total if ru.rent_total else Decimal(0.0)
                sum_nk += ru.nk
                sum_nk_electricity += ru.nk_electricity
                sum_rent_net += ru.rent_netto
                if ru.rent_netto or ru.nk:
                    rent_info.append(
                        {
                            "text": ru.str_short(),
                            "net": ru.rent_netto,
                            "nk": ru.nk,
                            "total": ru.rent_netto + ru.nk,
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
                ru_list.append(ru.name)

            if factor > 0.0:
                count += 1
                if factor != 1.0:
                    factor_txt = " (Faktor %.2f)" % factor
                else:
                    factor_txt = ""

                if sum_rent_net > 0.0:
                    description = "Nettomiete %02d.%d für %s%s" % (
                        month,
                        year,
                        "/".join(ru_list),
                        factor_txt,
                    )
                    invoice_value = sum_rent_net * factor
                    r = add_invoice(
                        rent_type,
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
                    if not isinstance(r, str):
                        messages.append(
                            "Montasrechnung hinzugefügt: %s für %s."
                            % (description, billing_contract_info)
                        )

                if sum_nk > 0.0:
                    description = "Nebenkosten %02d.%d für %s%s" % (
                        month,
                        year,
                        "/".join(ru_list),
                        factor_txt,
                    )
                    invoice_value = sum_nk * factor
                    r = add_invoice(
                        "nk",
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
                    if not isinstance(r, str):
                        messages.append(
                            "Montasrechnung hinzugefügt: %s für %s."
                            % (description, billing_contract_info)
                        )

                if sum_nk_electricity > 0.0:
                    description = "Strompauschale %02d.%d für %s%s" % (
                        month,
                        year,
                        "/".join(ru_list),
                        factor_txt,
                    )
                    invoice_value = sum_nk_electricity * factor
                    r = add_invoice(
                        "strom",
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
                    if not isinstance(r, str):
                        messages.append(
                            "Montasrechnung hinzugefügt: %s für %s."
                            % (description, billing_contract_info)
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
                    r = add_invoice(
                        "rent_reduction",
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
                    if not isinstance(r, str):
                        messages.append(
                            "Montasrechnung hinzugefügt: %s für %s."
                            % (description, billing_contract_info)
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
                book.close()
                return output_filename
            elif (
                factor > 0
                and sum_rent_total > 0.0
                and contract.send_qrbill in ("only_next", "always")
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
                messages = messages + ret
                if dry_run and single_contract:
                    book.close()
                    return output_filename

            ## Continue with previous month
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1

    book.close()
    messages.append("%s Rechnungen" % count)
    return messages


def get_book(messages):
    if not settings.GNUCASH:
        return DummyBook()
    try:
        if settings.GNUCASH_IGNORE_SQLALCHEMY_WARNINGS:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=sa_exc.SAWarning)
                book = open_book(
                    uri_conn=settings.GNUCASH_DB_SECRET,
                    readonly=settings.GNUCASH_READONLY,
                    do_backup=False,
                )
        else:
            book = open_book(
                uri_conn=settings.GNUCASH_DB_SECRET,
                readonly=settings.GNUCASH_READONLY,
                do_backup=False,
            )
    except Exception as e:
        messages.append("ERROR: Could not open Gnucash book: %s" % e)
        return None
    return book


def pay_invoice(invoice, date, amount):
    return add_payment(date, amount, invoice.person, invoice=invoice)


def add_payment(date, amount, person, invoice=None, note=None, cash=False):
    messages = []

    book = get_book(messages)
    if not book:
        return messages[-1]

    receivables = book.accounts(
        code=geno_settings.GNUCASH_ACC_INVOICE_RECEIVABLE
    )  ## Debitoren Miete
    if cash:
        payment_account = book.accounts(code=geno_settings.GNUCASH_ACC_KASSA)  ## Kasse
    else:
        payment_account = book.accounts(code=geno_settings.GNUCASH_ACC_POST)  ## Postkonto

    description = "Zahlung"
    if note:
        description = "Zahlung: %s" % note

    if invoice:
        description = "%s %s %s" % (description, invoice.invoice_category, invoice.id)
        r = add_invoice_obj(
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
    else:
        return "Kein Rechnungstyp für diese Zahlung definiert (TODO)."
    if isinstance(r, str):
        return r
    else:
        ## No error
        return 0


def get_income_account(book, invoice_category, kind):
    ## Special income accounts
    if kind == "rent_business":
        return book.accounts(code=geno_settings.GNUCASH_ACC_INVOICE_INCOME_BUSINESS)
    elif kind == "rent_other":
        return book.accounts(code=geno_settings.GNUCASH_ACC_INVOICE_INCOME_OTHER)
    elif kind == "rent_parking":
        return book.accounts(code=geno_settings.GNUCASH_ACC_INVOICE_INCOME_PARKING)
    elif kind == "nk":
        return book.accounts(code=geno_settings.GNUCASH_ACC_NK)
    elif kind == "rent_reduction":
        return book.accounts(code=geno_settings.GNUCASH_ACC_RENTREDUCTION)
    elif kind == "mietdepot":
        return book.accounts(code=geno_settings.GNUCASH_ACC_MIETDEPOT)
    elif kind == "schluesseldepot":
        return book.accounts(code=geno_settings.GNUCASH_ACC_SCHLUESSELDEPOT)
    elif kind == "strom":
        return book.accounts(code=geno_settings.GNUCASH_ACC_STROM)
    elif kind == "kiosk":
        return book.accounts(code=geno_settings.GNUCASH_ACC_KIOSK)
    elif kind == "spende":
        return book.accounts(code=geno_settings.GNUCASH_ACC_SPENDE)
    elif kind == "other":
        return book.accounts(code=geno_settings.GNUCASH_ACC_OTHER)
    ## Default
    return book.accounts(code=invoice_category.income_account)  ## z.B. Mietertag Wohnungen


def get_receivables_account(book, invoice_category):
    return book.accounts(code=invoice_category.receivables_account)  ## z.B. Debitoren Miete


def add_invoice(
    kind,
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
            raise RuntimeError("Can't specify address AND contract.")
        address = contract.get_contact_address()

    if not book:
        messages = []
        book = get_book(messages)
        if not book:
            return messages[-1]
    income_account = get_income_account(book, invoice_category, kind)
    receivables = get_receivables_account(book, invoice_category)

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


def add_invoice_obj(
    book,
    invoice_type,
    invoice_category,
    description,
    person,
    account,
    receivables_account,
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
    amount_dec = Decimal(str(amount))
    if invoice_type == "Invoice":
        acc_to = receivables_account
        acc_from = account
    elif invoice_type == "Payment":
        acc_to = account
        acc_from = receivables_account
    else:
        raise ValueError("Invoice type not implemented!")

    if dry_run:
        return None

    if transaction_id:
        ## Check if invoice exists already
        if Invoice.objects.filter(transaction_id=transaction_id).count():
            return "Invoice with transaction ID %s exists already!" % transaction_id

    try:
        if contract:
            txn_description = "%s [%s]" % (description, contract.get_contract_label())
            person = None
        elif person:
            txn_description = "%s [%s]" % (description, person)
        else:
            raise ValueError("add_invoice_obj: need contract OR person!")

        if comment:
            txn_description = "%s: %s" % (txn_description, comment)

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

        if settings.GNUCASH:
            txn = Transaction(
                post_date=date,  # datetime.datetime.strptime(date, "%Y-%m-%d"),
                enter_date=datetime.datetime.now(),
                # currency = book.default_currency,
                currency=book.currencies(mnemonic="CHF"),
                description=txn_description,
            )
            Split(account=acc_to, value=amount_dec, memo="", transaction=txn)
            Split(account=acc_from, value=-amount_dec, memo="", transaction=txn)

            book.flush()
            invoice.gnc_transaction = txn.guid
            invoice.gnc_account = account.code
            invoice.gnc_account_receivables = receivables_account.code
    except Exception as e:
        return "Could not create invoice: %s" % e

    invoice.save()
    book.save()
    return invoice


## TODO: Consolidate/refactor transaction creation and deletion
def add_transaction(
    date,
    description,
    account_to_code,
    account_from_code,
    amount,
    book=None,
    messages=None,
    dry_run=False,
):
    if messages is None:
        messages = []
    if not settings.GNUCASH:
        return None
    if not isinstance(amount, Decimal):
        amount_dec = Decimal(str(amount))
    else:
        amount_dec = amount

    if not book:
        book = get_book(messages)
        close_book = True
    else:
        close_book = False

    if not book:
        return None

    acc_to = book.accounts(code=account_to_code)
    acc_from = book.accounts(code=account_from_code)

    ## Post date should be datetime.date
    if isinstance(date, datetime.datetime):
        date_obj = date.date()
    elif isinstance(date, datetime.date):
        date_obj = date
        # date_obj = datetime.datetime.combine(date, datetime.datetime.min.time())
    else:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    txn = Transaction(
        post_date=date_obj,
        enter_date=datetime.datetime.now(),
        currency=book.currencies(mnemonic="CHF"),
        description=description,
    )
    Split(account=acc_to, value=amount_dec, memo="", transaction=txn)
    Split(account=acc_from, value=-amount_dec, memo="", transaction=txn)
    book.flush()

    if close_book:
        if not dry_run:
            book.save()
        book.close()

    return txn.guid


def delete_invoice_transaction(invoice):
    # print("Deleting transaction %s" % invoice.gnc_transaction)
    if not settings.GNUCASH:
        return None
    if not invoice.gnc_transaction:
        logger.warning("Trying to delete invoice withouth gnc_transaction id: %s" % invoice)
        return None
    messages = []
    book = get_book(messages)
    if not book:
        return "Could not open book"
    tr = None
    try:
        tr = book.transactions(guid=invoice.gnc_transaction)
    except KeyError:
        logger.error(
            "Could not find and delete transaction %s linked to invoice %s."
            % (invoice.gnc_transaction, invoice)
        )
        send_error_mail(
            "delete_invoice_transaction()",
            "Could not find and delete transaction %s linked to invoice %s."
            % (invoice.gnc_transaction, invoice),
        )
        return None
    if not tr or isinstance(tr, list):
        return "Could not get transaction with id %s" % (invoice.gnc_transaction)
    book.delete(tr)
    book.save()
    logger.info("Deleted gnc_transaction %s for invoice %s." % (invoice.gnc_transaction, invoice))
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
    messages = []

    if save_sender and save_sender != "IGNORE" and len(save_sender) > 5 and address and address.pk:
        try:
            lu = LookupTable.objects.get(name=save_sender, lookup_type="payment_sender")
        except LookupTable.DoesNotExist:
            lu = LookupTable(name=save_sender, lookup_type="payment_sender")
        lu.value = address.pk
        lu.save()

    book = get_book(messages)
    if not book:
        return messages[-1]

    ## Accounts
    payment_account = book.accounts(code=geno_settings.GNUCASH_ACC_POST)  ## Postkonto
    total = Decimal(amount)

    if transaction_type in ("entry_as", "entry_as_inv"):
        share_as_account = book.accounts(
            code=geno_settings.GNUCASH_ACC_SHARES_MEMBERS
        )  ## Genossenschaftsanteile Mitglieder
        book.accounts(code=geno_settings.GNUCASH_ACC_SHARES_DEPOSIT)  ## Depositenkasse

        entryfee_account = book.accounts(
            code=geno_settings.GNUCASH_ACC_MEMBER_FEE_ENTRY
        )  ## Beitrittsgebühren

        if transaction_type == "entry_as_inv":
            payment_account = book.accounts(code=geno_settings.GNUCASH_ACC_HELPER_SHARES)

        split1 = Decimal("200")
        split2 = total - split1
        count = int(split2 / 200)
        if count == 1:
            text_as = "1 Anteilschein"
        else:
            text_as = "%d Anteilscheine" % count
        try:
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
                attribute_type=MemberAttributeType.objects.get(
                    name="Mitgliederbeitrag %s" % date.year
                ),
                value="Bezahlt (mit Eintritt)",
            )

            if settings.GNUCASH:
                t = Transaction(
                    post_date=date,
                    enter_date=datetime.datetime.now(),
                    # currency = book.default_currency,
                    currency=book.currencies(mnemonic="CHF"),
                    description="%s und Beitrittsgebühr, %s" % (text_as, address),
                )
                Split(account=payment_account, value=total, memo="", transaction=t)
                Split(account=entryfee_account, value=-split1, memo="", transaction=t)
                if count != 0:
                    Split(account=share_as_account, value=-split2, memo="", transaction=t)
                book.flush()
        except Exception as e:
            return "Could not create transaction: %s" % e
        if count != 0:
            share.save()
        att.save()
        book.save()
    elif transaction_type == "kiosk_payment":
        income_account = book.accounts(code=geno_settings.GNUCASH_ACC_KIOSK)
        desc = "Kiosk/Getränke"
        if note:
            desc = "%s: %s" % (desc, note)
        total = Decimal(amount)
        if settings.GNUCASH:
            t = Transaction(
                post_date=date,
                enter_date=datetime.datetime.now(),
                currency=book.currencies(mnemonic="CHF"),
                description=desc,
            )
            Split(account=payment_account, value=total, memo="", transaction=t)
            Split(account=income_account, value=-total, memo="", transaction=t)
            book.save()
    elif transaction_type in ("share_as", "share_as_inv"):
        payment_bank_account = book.accounts(code=geno_settings.GNUCASH_ACC_BANK)  ## Bankkonto
        share_as_account = book.accounts(
            code=geno_settings.GNUCASH_ACC_SHARES_MEMBERS
        )  ## Genossenschaftsanteile Mitglieder
        if transaction_type == "share_as_inv":
            payment_bank_account = book.accounts(code=geno_settings.GNUCASH_ACC_HELPER_SHARES)
        if float(amount) % 200.00 != 0.0:
            return "Share is not a multiple of 200.-!"
        count = int(total / 200)
        if count == 1:
            text_as = "1 Anteilschein"
        else:
            text_as = "%d Anteilscheine" % count
        try:
            share = Share(
                name=address,
                share_type=ShareType.objects.get(name="Anteilschein"),
                state="bezahlt",
                date=date,
                quantity=count,
                value=200,
            )

            if settings.GNUCASH:
                t = Transaction(
                    post_date=date,
                    enter_date=datetime.datetime.now(),
                    # currency = book.default_currency,
                    currency=book.currencies(mnemonic="CHF"),
                    description="%s, %s" % (text_as, address),
                )
                Split(account=payment_bank_account, value=total, memo="", transaction=t)
                Split(account=share_as_account, value=-total, memo="", transaction=t)
                book.flush()
        except Exception as e:
            return "Could not create transaction: %s" % e

        share.save()
        book.save()
    elif (
        transaction_type == "loan_interest_toloan" or transaction_type == "loan_interest_todeposit"
    ):
        interest_account = book.accounts(
            code=geno_settings.GNUCASH_ACC_SHARES_INTEREST
        )  ## Verbindlichkeiten aus Finanzierung

        if transaction_type == "loan_interest_toloan":
            to_account = book.accounts(
                code=geno_settings.GNUCASH_ACC_SHARES_LOAN_INT
            )  ## Darlehen verzinst
            text = "Anrechnung Darlehenszins an Darlehen"
            stype = ShareType.objects.get(name="Darlehen verzinst")
        elif transaction_type == "loan_interest_todeposit":
            to_account = book.accounts(
                code=geno_settings.GNUCASH_ACC_SHARES_DEPOSIT
            )  ## Depositenkasse
            text = "Anrechnung Darlehenszins an Depositenkasse"
            stype = ShareType.objects.get(name="Depositenkasse")

        try:
            share = Share(
                name=address,
                share_type=stype,
                state="bezahlt",
                date=date,
                quantity=1,
                value=total,
                is_interest_credit=True,
                note=text,
            )

            if settings.GNUCASH:
                t = Transaction(
                    post_date=date,
                    enter_date=datetime.datetime.now(),
                    currency=book.currencies(mnemonic="CHF"),
                    description="%s, %s" % (text, address),
                )
                Split(account=interest_account, value=total, memo="", transaction=t)
                Split(account=to_account, value=-total, memo="", transaction=t)
                book.flush()
        except Exception as e:
            return "Could not create transaction: %s" % e

        share.save()
        book.save()
    elif transaction_type == "memberfee":
        fee_year = datetime.datetime.today().year
        memberfee_account = book.accounts(
            code=geno_settings.GNUCASH_ACC_MEMBER_FEE
        )  ## Mitgliederbeiträge
        try:
            att_type = MemberAttributeType.objects.get(name="Mitgliederbeitrag %s" % fee_year)
        except MemberAttributeType.DoesNotExist:
            return "Mitglieder Attribut 'Mitgliederbeitrag %s' existiert nicht." % fee_year

        member = Member.objects.get(name=address)
        att = MemberAttribute.objects.filter(member=member, attribute_type=att_type)
        # for a in att:
        #   messages.warning(request, "Attribute found: %s - %s" % (a.date,a.value))
        if len(att) == 0:
            ## Create new attribute
            att = MemberAttribute(member=member, attribute_type=att_type)
        elif len(att) == 1:
            att = att[0]
            if att.value.startswith("Bezahlt"):
                return "Schon als bezahlt markiert"
            elif (
                att.value != "Mail-Rechnung geschickt"
                and att.value != "Mail-Reminder geschickt"
                and att.value != "Brief-Rechnung geschickt"
                and att.value != "Brief-Reminder geschickt"
                and att.value != "Brief-Mahnung geschickt"
                and att.value != "Brief-Mahnung2 geschickt"
            ):
                return "Unknown attribute value"
        else:
            return "More than one attribute found"
        try:
            if settings.GNUCASH:
                t = Transaction(
                    post_date=date,
                    # enter_date = test_date, ## Default = now
                    # currency = book.default_currency,
                    currency=book.currencies(mnemonic="CHF"),
                    description="Mitgliederbeitrag %s, %s" % (fee_year, address),
                )
                Split(account=payment_account, value=total, memo="", transaction=t)
                Split(account=memberfee_account, value=-total, memo="", transaction=t)
                book.flush()
            att.value = "Bezahlt"
            att.date = date
        except Exception as e:
            return "Could not create transaction: %s" % e
        att.save()
        book.save()
    elif transaction_type == "invoice_payment":
        return add_payment(date, amount, address, invoice=None, note=note)
    elif transaction_type == "cash_payment":
        return add_payment(date, amount, address, invoice=None, note=note, cash=True)
    else:
        return "Transaction type '%s' not implemented yet." % transaction_type


def process_sepa_transactions(data):
    errors = []
    skipped = []
    success = []
    for item in data["log"]:
        logger.info("%s: %s" % (item["info"], "/".join(item["objects"])))

    book = get_book(data["log"])
    if not book:
        errors.append("Kann Buchhaltung nicht öffnen!")
        return {"errors": errors, "skipped": skipped, "success": success, "log": data["log"]}

    #'id': tx_id, 'date': date, 'amount': amount, 'reference': reference_nr, 'debtor': debtor, 'extra_info': additional_info, 'charges': charges
    for tx in data["transactions"]:
        bill_info = parse_reference_nr(tx["reference_nr"])
        if "error" in bill_info:
            errors.append(
                "Ungültige Referenznummer: %s für Buchung %s - CHF %s"
                % (bill_info["error"], tx["date"], tx["amount"])
            )
            continue
        addtl_info = []
        if tx["extra_info"]:
            addtl_info.append(tx["extra_info"])
        if tx["debtor"]:
            addtl_info.append(tx["debtor"])
        if tx["charges"]:
            addtl_info.append("Charges: %s" % tx["charges"])
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
        receivable_account = None
        try:
            for account in settings.GENO_FINANCE_ACCOUNTS.values():
                if normalize_iban(tx["account"]) in (
                    normalize_iban(account["iban"]),
                    normalize_iban(account["account_iban"]),
                ):
                    payment_account = book.accounts(code=account["account_code"])
                    break
            if not payment_account:
                raise Exception(
                    f"IBAN {tx['account']} nicht gefunden in settings.GENO_FINANCE_ACCOUNTS"
                )
            receivable_account = book.accounts(code=bill_info["receivables_account"])
        except Exception as e:
            errors.append(
                "Buchhaltungs-Konten nicht gefunden: %s/%s (%s) [%s]"
                % (tx["account"], bill_info["receivables_account"], e, transaction_info_txt)
            )
            continue

        r = add_invoice_obj(
            book,
            "Payment",  # invoice_type,
            bill_info["invoice_category"],
            bill_info["description"],
            bill_info["person"],
            payment_account,
            receivable_account,
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
        if isinstance(r, str):
            if r == f"Invoice with transaction ID {tx['id']} exists already!":
                skipped.append(
                    "Buchung mit Transaktions-ID %s existiert bereits (%s)"
                    % (tx["id"], transaction_info_txt)
                )
            else:
                errors.append(
                    "Buchung konnte nicht ausgeführt werden: %s (%s)" % (r, transaction_info_txt)
                )
        else:
            success.append(transaction_info_txt)

    return {"errors": errors, "skipped": skipped, "success": success, "log": data["log"]}


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
    if address.organization:
        bill_name = address.organization
    else:
        bill_name = "%s %s" % (address.first_name, address.name)

    if render:
        context["qr_account"] = settings.GENO_FINANCE_ACCOUNTS["default_debtor"]["iban"]
        context["qr_ref_number"] = ref_number
        context["qr_bill_name"] = bill_name
        context["qr_addr_line1"] = address.street
        context["qr_addr_line2"] = address.city
        try:
            invoice_doctype = DocumentType.objects.get(name="invoice")
            render_qrbill(invoice_doctype.template, context, output_filename)
        except Exception as e:
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
            recipient = settings.TEST_MAIL_RECIPIENT
            email_copy = None
        else:
            recipient = address.email
            email_copy = settings.GENO_DEFAULT_EMAIL
        mail_recipient = '"%s" <%s>' % (bill_name, recipient)
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
                if email_copy and recipient != email_copy:
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
    context["show_liegenschaft"] = False
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

    if email_template:
        if mails_sent == 1:
            if dry_run:
                preview_email_url = f'<a href="/geno/preview/?contract={contract.id}&invoice_category={invoice_category.id}" target="_blank">Vorschau</a>'
                preview_pdf_url = f'<a href="?single_contract={contract.id}&date={invoice_date.strftime("%Y-%m-%d")}">{output_filename}</a>'
                messages.append(
                    f"DRY-RUN: Hätte nun Email [{preview_email_url}] mit QR-Rechnung an {escape(mail_recipient)} geschickt. {preview_pdf_url}"
                )
            else:
                messages.append(
                    "Email mit QR-Rechnung an %s geschickt. %s"
                    % (escape(mail_recipient), output_filename)
                )
                if contract.send_qrbill == "only_next":
                    ## Disable sending for next bill
                    contract.send_qrbill = "none"
                    contract.save()
        else:
            messages.append("FEHLER beim Versenden des Emails.")

    return (messages, output_filename)


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
    if "qr_bill_name" not in context:
        raise RuntimeError("render_qrbill(): 'qr_bill_name' not found in context.")
    if "qr_addr_line1" not in context:
        raise RuntimeError("render_qrbill(): 'qr_addr_line1' not found in context.")
    if "qr_addr_line2" not in context:
        raise RuntimeError("render_qrbill(): 'qr_addr_line2' not found in context.")
    if "qr_amount" not in context:
        raise RuntimeError("render_qrbill(): 'qr_amount' not found in context.")
    if "qr_extra_info" not in context:
        raise RuntimeError("render_qrbill(): 'qr_extra_info' not found in context.")
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
        creditor=context["qr_creditor"],
        debtor={
            "name": context["qr_bill_name"],
            "line1": context["qr_addr_line1"],
            "line2": context["qr_addr_line2"],
        },
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
