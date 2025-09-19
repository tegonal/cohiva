import datetime
import json
import logging
from decimal import Decimal

from django.utils import timezone
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from geno.models import RentalUnit, get_active_contracts

from .accounts import (
    get_accounts_for_user,
    get_transaction_time_filter_options,
    get_transactions_queryset_and_balance,
)
from .models import Account, AccountOwner, Transaction, UserAccountSetting, Vendor

logger = logging.getLogger("credit_accounting")


class AppView(APIView):
    """
    Base class for app user API endpoints.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get_user_accounts(self, request):
        try:
            vendor_name = request.query_params.get("vendor", request.data.get("vendor", None))
            self.vendor = Vendor.objects.get(name=vendor_name)
        except Vendor.DoesNotExist:
            raise ValidationError("Invalid vendor.")
        self.accounts = get_accounts_for_user(
            request.user, self.vendor, include_all_for_admins=False
        )


class AccountListView(AppView):
    """
    API endpoint for listing account(s) owned by user.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get(self, request, format=None):
        # logger.debug(f"Getting accounts for user {request.user}.")
        self.get_user_accounts(request)
        response = []
        for account in self.accounts:
            response.append({"value": account.id, "label": account.name})
        return Response({"status": "OK", "accounts": response})


class TransactionListFilterView(AppView):
    """
    API endpoint to get transaction filter options.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get(self, request, format=None):
        time_options = []
        for o in get_transaction_time_filter_options():
            time_options.append({"value": o[0], "label": o[1]})
        return Response({"status": "OK", "time_filter": time_options})


## TODO: Add paginator?
class TransactionListView(AppView):
    """
    API endpoint for listing transactions owned by user.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users
    max_results = 500

    def get(self, request, format=None):
        self.get_user_accounts(request)
        response = []
        try:
            self.filter = json.loads(request.query_params.get("filter"))
        except json.decoder.JSONDecodeError:
            raise ValidationError("Invalid filter.")
        for t in get_transactions_queryset_and_balance(self)[0 : self.max_results]:
            response.append(
                {
                    "id": t.id,
                    "name": t.name,
                    "amount": t.amount,
                    "date": timezone.localtime(t.date).strftime("%d.%m.%Y %H:%M"),
                    "note": t.description,
                    "balance": self.balance[t.pk],
                }
            )
        return Response(
            {"status": "OK", "transactions": response, "max_results": self.max_results}
        )


class SettingsView(AppView):
    """
    API endpoint for getting and setting user settings.
    """

    def get_threshold_settings(self, request):
        self.get_user_accounts(request)
        try:
            account_id = request.query_params.get("account", request.data.get("account", None))
            self.account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            raise ValidationError("Invalid account")
        if self.account not in self.accounts:
            raise ValidationError("Invalid account")
        try:
            threshold_settings = UserAccountSetting.objects.get(
                name="notification_balance_below_amount", account=self.account, user=request.user
            )
        except UserAccountSetting.DoesNotExist:
            threshold_settings = UserAccountSetting(
                name="notification_balance_below_amount",
                account=self.account,
                user=request.user,
                active=False,
                value="100",
            )
        return threshold_settings

    def get(self, request, format=None):
        threshold_settings = self.get_threshold_settings(request)
        settings = {
            "pin": self.account.pin,
            "user_email": request.user.email,
            "notification_balance_below_amount_active": threshold_settings.active,
            "notification_balance_below_amount_value": threshold_settings.value,
        }
        return Response({"status": "OK", "settings": settings})

    def post(self, request, format=None):
        threshold_settings = self.get_threshold_settings(request)
        new_settings = request.data.get("settings", {})
        if (
            "pin" in new_settings
            and len(new_settings["pin"]) > 2
            and len(new_settings["pin"]) <= 20
            and new_settings["pin"] != self.account.pin
        ):
            self.account.pin = new_settings["pin"]
            self.account.save()
            logger.info(f"Changed PIN for account {self.account}.")
        save_threshold = False
        if (
            "notification_balance_below_amount_active" in new_settings
            and new_settings["notification_balance_below_amount_active"]
            != threshold_settings.active
        ):
            threshold_settings.active = new_settings["notification_balance_below_amount_active"]
            save_threshold = True
        if (
            "notification_balance_below_amount_value" in new_settings
            and new_settings["notification_balance_below_amount_value"] != threshold_settings.value
        ):
            threshold_settings.value = new_settings["notification_balance_below_amount_value"]
            save_threshold = True
        if save_threshold:
            threshold_settings.save()
            logger.info(
                f"Changed notification_balance_below_amount setting for account {self.account}."
            )
        return Response({"status": "OK"})


class PosView(APIView):
    """
    Base class for POS API endpoints.
    """

    permission_classes = [
        permissions.AllowAny
    ]  ## Allow any. Authentication is done by vendor specific secret (and account PIN).

    def authenticate_vendor(self, request):
        if request.data:
            vendor_name = request.data.get("vendor")  # , request.query_params.get('vendor',None))
            secret = request.data.get("secret")  # , request.query_params.get('secret',None))
        elif request.query_params:
            vendor_name = request.query_params.get("vendor")
            secret = request.query_params.get("secret")
        else:
            raise ValidationError("Invalid request.")
        self.vendor = Vendor.objects.filter(name=vendor_name).filter(active=True).first()
        if not self.vendor:
            logger.info(f"Invalid vendor: {vendor_name}.")
            raise ValidationError("Invalid vendor.")
        if not secret or len(secret) < 10 or secret != self.vendor.api_secret:
            logger.warning(f"Vendor authentication failed: {self.vendor}")
            raise AuthenticationFailed()


class PosTransactionView(PosView):
    """
    View to submit transaction by POS.
    """

    def post(self, request, format=None):
        self.authenticate_vendor(request)

        for field in ("name", "account", "amount", "date"):
            if not request.data.get(field):
                logger.info(f"validation error: {field} not found.")
                raise ValidationError(f"Missing {field}.")
        try:
            transaction_date = datetime.datetime.strptime(
                request.data.get("date"), "%Y-%m-%d %H:%M:%S.%f%z"
            )
        except Exception as e:
            logger.info(f"validation error: Invalid date: {e}: {request.data.get('date')}.")
            raise ValidationError("Invalid date.")
        account = (
            Account.objects.filter(vendor=self.vendor)
            .filter(pin=request.data.get("account"))
            .filter(active=True)
            .first()
        )
        if not account:
            logger.info(f"validation error: Invalid account/pin: {request.data.get('account')}.")
            raise ValidationError("Invalid account/pin.")
        if (
            request.data.get("id")
            and Transaction.objects.filter(
                account=account, transaction_id=request.data.get("id")
            ).count()
        ):
            logger.warning(
                f"Transaction with ID {request.data.get('id')} exists already. Ignoring request."
            )
            return Response({"status": "Duplicate"})
        try:
            trans = Transaction(
                name=request.data.get("name"),
                account=account,
                amount=Decimal(request.data.get("amount")),
                date=transaction_date,
                description=request.data.get("note", ""),
            )
            if request.data.get("id"):
                trans.transaction_id = request.data.get("id")
            trans.save()
            logger.info(
                f"Added transaction: {request.data.get('name')}, account={account}, "
                f"CHF {request.data.get('amount')} {transaction_date} "
                f"{request.data.get('note', '')}"
            )
        except Exception as e:
            logger.error(
                f"Could not create transaction: {e} - {request.data.get('name')}, "
                f"account={account}, CHF {request.data.get('amount')} {transaction_date} "
                f"{request.data.get('note', '')} [{request.data.get('id', None)}]"
            )
            return Response({"status": "Error", "error": "Could not create transaction."})

        return Response({"status": "OK"})


class PosAccountsView(PosView):
    """
    View to get accountlist for POS.
    """

    def get(self, request, format=None):
        self.authenticate_vendor(request)
        accounts = {}
        for account in Account.objects.filter(vendor=self.vendor).filter(active=True):
            accounts[account.pin] = {"balance": account.balance}
        if len(accounts):
            return Response({"status": "OK", "accounts": accounts})
        else:
            logger.error(f"No active accounts found for vendor {self.vendor}.")
            return Response({"status": "Error", "error": "No accounts found."})


class PosAccountView(PosView):
    """
    View for creating an account from POS.
    """

    def post(self, request, format=None):
        self.authenticate_vendor(request)
        for field in ("name", "pin"):
            if not request.data.get(field):
                logger.info(f"validation error: {field} not found.")
                raise ValidationError(f"Missing {field}.")
        if not isinstance(request.data.get("transactions"), list):
            raise ValidationError("Missing transactions list (can be emtpy).")

        ru = RentalUnit.objects.filter(name=request.data.get("name")).filter(active=True).first()
        if ru:
            if ru.label:
                name = f"{ru.label} {ru.name}"
            else:
                name = f"Wohnung {ru.name}"
            contract = get_active_contracts().filter(rental_units__id__exact=ru.id).first()
        else:
            name = f"Konto {request.data.get('name')}"
            contract = None
        if not contract:
            logger.warning(f"No contract found for new account {name} (rental_unit: {ru}).")
        try:
            account = Account.objects.get(
                name=name, pin=request.data.get("pin"), vendor=self.vendor
            )
            logger.warning(f"Account exists already: {account}")
            is_duplicate = True
        except Account.DoesNotExist:
            is_duplicate = False
        except Exception as e:
            logger.error(
                f"Error while checking account: {e} - "
                f"{name}, contract={contract}, pin={request.data.get('pin')}"
            )
            return Response({"status": "Error", "error": "Duplicate check failed: {e}."})

        if not is_duplicate:
            try:
                account = Account(name=name, pin=request.data.get("pin"), vendor=self.vendor)
                account.save()
                if contract:
                    account_owner = AccountOwner(name=account, owner_object=contract)
                    account_owner.save()
                else:
                    account_owner = None
                logger.info(f"Created new account {account} / {account_owner}.")
            except Exception as e:
                logger.error(
                    f"Could not create account or account_owner: {e} - "
                    f"{name}, contract={contract}, pin={request.data.get('pin')}"
                )
                return Response({"status": "Error", "error": "Could not create account."})

        ## Import transactions
        count = {"success": 0, "skipped": 0, "error": 0}
        for t in request.data.get("transactions"):
            if (
                t.get("id")
                and Transaction.objects.filter(account=account, transaction_id=t.get("id")).count()
            ):
                ## Skip duplicate
                count["skipped"] += 1
                continue
            try:
                transaction_date = datetime.datetime.strptime(
                    t.get("date"), "%Y-%m-%d %H:%M:%S.%f%z"
                )
                trans = Transaction(
                    name=t.get("name"),
                    account=account,
                    amount=Decimal(t.get("amount")),
                    date=transaction_date,
                    description=t.get("note", ""),
                    transaction_id=t.get("id", None),
                )
                trans.save()
                count["success"] += 1
            except Exception as e:
                logger.error(
                    f"Could not create transaction: {e} - {t.get('name')}, account={account}, "
                    f"CHF {t.get('amount')} {t.get('date')} {t.get('note', '')} "
                    f"[{t.get('id', None)}]"
                )
                count["error"] += 1
        if count["success"] or count["error"] or count["skipped"]:
            logger.info(
                f"Added {count['success']} transactions to account {account} ({count['skipped']} "
                f"skipped duplicates, {count['error']} errors)."
            )
        if count["error"]:
            return Response(
                {
                    "status": "Error",
                    "error": "Could not create all transactions (see server log).",
                    "account_id": account.id,
                    "transaction_count": count,
                }
            )
        elif is_duplicate:
            return Response(
                {"status": "Duplicate", "account_id": account.id, "transaction_count": count}
            )
        else:
            return Response({"status": "OK", "account_id": account.id, "transaction_count": count})


def get_capabilities(request, capabilities):
    capabilities["credit_accounting_vendors"] = []
    for vendor in Vendor.objects.filter(active=True):
        accounts = get_accounts_for_user(request.user, vendor)
        if len(accounts):
            capabilities["credit_accounting_vendors"].append(vendor.name)
