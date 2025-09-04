import datetime
import logging
from calendar import month_name
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Max, Min, Q, Sum, Window
from django.shortcuts import redirect
from django.utils import timezone

import credit_accounting.settings as app_settings
from geno.gnucash import parse_reference_nr
from geno.models import Address, Contract
from geno.utils import send_error_mail

from .models import Account, AccountOwner, Transaction, Vendor, VendorAdmin

logger = logging.getLogger("credit_accounting")


def get_accounts_for_user(user, vendor, include_all_for_admins=True):
    ## Get credit_accounting accounts from these relationships:
    ## (1) username > Address
    ## (2) username > Address > Contract
    ## (3) Accounts the user is admin for
    accounts = []
    if not hasattr(user, "address") or not user.address.active or not vendor.active:
        return accounts

    ## (1) Get accounts linked to active address
    for owner in AccountOwner.objects.filter(
        owner_id=user.address.id,
        owner_type=ContentType.objects.get_for_model(user.address),
        name__vendor=vendor,
    ):
        accounts.append(owner.name)

    ## (2) Get accounts linked to active contracts
    for contract in user.address.get_contracts():
        for owner in AccountOwner.objects.filter(
            owner_id=contract.id,
            owner_type=ContentType.objects.get_for_model(contract),
            name__vendor=vendor,
        ):
            if owner.name not in accounts:
                accounts.append(owner.name)

    ## (3) Add accounts of vendor if user is a VendorAdmin (and include_others_for_admin is True)
    if include_all_for_admins:
        for vendoradmin in VendorAdmin.objects.filter(
            name=user.address, role="admin", vendor=vendor, active=True
        ):
            for account in Account.objects.filter(vendor=vendoradmin.vendor):
                if account not in accounts:
                    accounts.append(account)

    return accounts


def get_transaction_time_filter_options():
    time_options = [("days_90", "Letzte 90 Tage"), ("days_180", "Letzte 180 Tage")]
    cur_year = datetime.datetime.now().year
    cur_month = datetime.datetime.now().month
    for dm in range(12):
        m = cur_month - dm
        y = cur_year
        if m < 1:
            m += 12
            y -= 1
        time_options.append(("month_%d_%d" % (y, m), "%s %d" % (month_name[m], y)))
    for year in range(cur_year, 2021, -1):
        time_options.append(("year_%d" % year, "Ganzes Jahr %d" % year))
    time_options.append(("all", "Alle Buchungen"))
    return time_options


def get_transactions_queryset_and_balance(query_object):
    account = None
    query_object.balance = {}
    if not query_object.filter["account"]:
        return Transaction.objects.none()
    if query_object.filter["account"] == "_all_":
        qs = Transaction.objects.all()
    else:
        account_id = int(query_object.filter["account"])
        for a in query_object.accounts:
            if a.id == account_id:
                account = a
                break
        qs = Transaction.objects.filter(account=account)
    time_filter = query_object.filter["time"].split("_")
    if time_filter[0] == "days":
        qs = qs.filter(date__gte=timezone.now() - datetime.timedelta(days=int(time_filter[1])))
    elif time_filter[0] == "month":
        qs = qs.filter(date__year=int(time_filter[1]), date__month=int(time_filter[2]))
    elif time_filter[0] == "year":
        qs = qs.filter(date__year=int(time_filter[1]))
    elif query_object.filter["time"] and time_filter[0] != "all":
        raise RuntimeError(f"Unknown time filter: {query_object.filter['time']}")
    if query_object.filter["sign"] == "plus":
        qs = qs.filter(amount__gte=0.0)
    elif query_object.filter["sign"] == "minus":
        qs = qs.filter(amount__lt=0.0)
    elif query_object.filter["sign"] and query_object.filter["sign"] != "all":
        raise RuntimeError(f"Unknown sign filter: {query_object.filter['sign']}")
    if "amount_min" in query_object.filter and query_object.filter["amount_min"] not in ("", None):
        qs = qs.filter(amount__gte=query_object.filter["amount_min"])
    if "amount_max" in query_object.filter and query_object.filter["amount_max"] not in ("", None):
        qs = qs.filter(amount__lte=query_object.filter["amount_max"])
    if query_object.filter["search"]:
        qs = qs.filter(
            Q(name__icontains=query_object.filter["search"])
            | Q(description__icontains=query_object.filter["search"])
            | Q(account__name__icontains=query_object.filter["search"])
        )

    if query_object.filter["account"] != "_all_":
        ## Get balance for each transaction in the time frame
        earliest_transaction = qs.aggregate(min_=Min("date")).get("min_")
        latest_transaction = qs.aggregate(max_=Max("date")).get("max_")
        # print("Balance date range: %s - %s" % (earliest_transaction, latest_transaction))
        sum_transactions_after = 0
        if latest_transaction:
            sum_transactions_after = (
                Transaction.objects.filter(account__id=account_id)
                .filter(date__gt=latest_transaction)
                .aggregate(sum_=Sum("amount"))
                .get("sum_")
            )
            if sum_transactions_after is None:
                sum_transactions_after = 0
        if earliest_transaction:
            balance_offset = Account.objects.get(id=account_id).balance - sum_transactions_after
            for t in (
                Transaction.objects.filter(account__id=account_id)
                .filter(date__gte=earliest_transaction)
                .filter(date__lte=latest_transaction)
                .annotate(cumsum=Window(Sum("amount"), order_by=F("date").desc()))
            ):
                query_object.balance[t.pk] = balance_offset - t.cumsum + t.amount
    return qs


def verify_accounts_data_integrity():
    for account in Account.objects.all():
        check_account_balance(account)


def check_account_balance(account):
    balance = Transaction.objects.filter(account=account).aggregate(total=Sum("amount"))
    if balance["total"] is None:
        balance["total"] = 0
    if balance["total"] != account.balance:
        logger.warning(
            "Corrected account balance for account %s (id=%d): %s -> %s"
            % (account, account.id, account.balance, balance["total"])
        )
        send_error_mail(
            "check_account_balance",
            "Corrected account balance for account %s (id=%d): %s -> %s"
            % (account, account.id, account.balance, balance["total"]),
        )
        account.balance = balance["total"]
        account.save()


def import_transactions(data, vendor):
    log = data["log"]
    for item in log:
        logger.info("%s: %s" % (item["info"], "/".join(item["objects"])))
    errors = []
    skipped = []
    success = []
    for tx in data["transactions"]:
        addtl_info = []
        if tx["extra_info"]:
            addtl_info.append(tx["extra_info"])
        if tx["debtor"]:
            addtl_info.append(tx["debtor"])
        # if tx['charges']:
        #    addtl_info.append("Charges: %s" % tx['charges'])
        transaction_info_txt = "%s - CHF %s (%s)" % (
            tx["date"],
            tx["amount"],
            "/".join(addtl_info),
        )

        bill_info = parse_reference_nr(tx["reference_nr"])
        if "error" in bill_info:
            errors.append(
                "Ungültige Referenznummer: %s: %s [%s]"
                % (bill_info["error"], tx["reference_nr"], transaction_info_txt)
            )
            continue
        if bill_info["ref_type"] != "app":
            errors.append(
                "Ungültige Referenznummer: Falscher Typ: %s [%s]"
                % (bill_info["ref_type"], transaction_info_txt)
            )
            continue
        if bill_info["app_name"] != "credit_accounting" or int(bill_info["id1"]) != 1:
            errors.append(
                "Ungültige Referenznummer: Falsche App/ID1: %s/%s [%s]"
                % (bill_info["app_name"], bill_info["id1"], transaction_info_txt)
            )
            continue
        try:
            bill_info["account"] = Account.objects.get(id=int(bill_info["object_id"]))
            transaction_info_txt = "%s - CHF %s für Konto %s (%s)" % (
                tx["date"],
                tx["amount"],
                bill_info["account"],
                "/".join(addtl_info),
            )
        except Account.DoesNotExist:
            errors.append(
                "Ungültige Referenznummer: Konto mit ID %s nicht gefunden. [%s]"
                % (bill_info["object_id"], transaction_info_txt)
            )
            continue

        if Transaction.objects.filter(transaction_id=tx["id"]).count():
            skipped.append(
                "Buchung mit Transaktions-ID %s existiert bereits [%s]"
                % (tx["id"], transaction_info_txt)
            )
            continue

        try:
            amount_dec = Decimal(tx["amount"])
        except Exception as e:
            errors.append(
                "Ungültiger Betrag %s: %s [%s]" % (tx["amount"], e, transaction_info_txt)
            )
            continue

        try:
            date = datetime.datetime.combine(tx["date"], datetime.datetime.min.time())
            if not date.tzinfo:
                date = date.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
        except Exception as e:
            errors.append("Ungültiges Datum %s: %s [%s]" % (tx["date"], e, transaction_info_txt))
            continue

        try:
            new = Transaction(
                name="Einzahlung %s" % vendor,
                account=bill_info["account"],
                amount=amount_dec,
                date=date,
                description="/".join(addtl_info),
                transaction_id=tx["id"],
            )
            new.save()
            success.append(transaction_info_txt)
        except Exception as e:
            errors.append("Konnte Buchung nicht hinzufügen: %s [%s]" % (e, transaction_info_txt))
    return {"errors": errors, "skipped": skipped, "success": success, "log": log}


class AccountInformationMixin:
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        ## TODO: Implement multiple vendors.
        try:
            self.vendor = Vendor.objects.get(name=app_settings.DEFAULT_VENDOR)
        except Vendor.DoesNotExist:
            self.vendor = Vendor.objects.first()
        if request.user.is_anonymous:
            return redirect("/portal/login/?next=%s" % request.get_full_path())
        elif hasattr(self.user, "address") and self.user.address.active:
            if VendorAdmin.objects.filter(
                name=self.user.address, role="admin", vendor=self.vendor, active=True
            ).count():
                self.is_admin = True
            else:
                self.is_admin = False
        else:
            return redirect("login-required")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = self.is_admin
        context["base_url"] = "/credit_accounting"
        return context

    def get_account_owner(self, owner_id):
        if owner_id[0:2] == "c_":
            try:
                owner_obj = Contract.objects.get(id=int(owner_id[2:]))
            except Contract.DoesNotExist:
                raise RuntimeError("Invalid owner contract id: %s" % owner_id)
        elif owner_id[0:2] == "a_":
            try:
                owner_obj = Address.objects.get(id=int(owner_id[2:]))
            except Address.DoesNotExist:
                raise RuntimeError("Invalid owner address id: %s" % owner_id)
        else:
            raise RuntimeError("Invalid owner prefix: %s" % owner_id)

        return owner_obj

    def get_account_owner_id(self, owner_obj):
        if isinstance(owner_obj, Contract):
            return "c_%s" % owner_obj.id
        if isinstance(owner_obj, Address):
            return "a_%s" % owner_obj.id
        raise RuntimeError("Invalid owner object: %s" % owner_obj)
