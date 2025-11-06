import datetime
import json
import logging
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from . import Account
from .book import AccountingBook

logger = logging.getLogger("finance_accounting")

# CashCtrl Handler for transactional operations
# Inserts are executed immediately via API, but tracked for possible rollback on close()
# Deletes are tracked and executed on save()
#
# Possible improvements:
# - Batch inserts and deletes to reduce number of API calls
# - inserts only on save(): possibility to fetch ID provided by CashCtrl API, but needs more complex tracking (concurrency)


class BookTransaction:
    _inserted_transaction_ids = []
    _deleted_transaction_ids = []

    def __init__(self, cct_book_ref, book_type_id, _api_token, _cct_tenant, _api_host):
        self.cct_book_ref = cct_book_ref
        self.book_type_id = book_type_id
        self._api_token = _api_token
        self._cct_tenant = _cct_tenant
        self._api_host = _api_host

    def close(self):
        # for inserted transactions still in array, delete on CashCtrl via API as rollback
        # Call delete endpoint. API expects a comma-separated list of ids in 'ids' param.
        # We reuse the GET-style endpoint as described in comments.
        # Normalize and strip possible book prefix (e.g. 'cct_...')
        self._delete(self._inserted_transaction_ids)
        self._inserted_transaction_ids.clear()

        # deleted transactions can be ignored as they were not yet saved to CashCtrl
        self._deleted_transaction_ids.clear()

    def insert(self, transaction):
        if "id" in transaction:
            self._inserted_transaction_ids.append(transaction["id"])
        else:
            self._inserted_transaction_ids.append(transaction)

    def delete(self, transaction):
        if "id" in transaction:
            self._deleted_transaction_ids.append(transaction["id"])
        else:
            self._deleted_transaction_ids.append(transaction)

    def create(self, transaction):
        # Expecting two splits: debit and credit
        if not getattr(transaction, "splits", None) or len(transaction.splits) < 2:
            raise ValueError("transaction must contain at least two splits (debit and credit)")
        elif len(transaction.splits) == 2:
            return self._create_simple_transaction(transaction)
        else:
            return self._create_collective_transaction(transaction)

    def _create_collective_transaction(self, transaction):
        # Expecting two splits: debit and credit
        if not getattr(transaction, "splits", None) or len(transaction.splits) <= 2:
            raise ValueError("transaction must contain at least two splits")

        split_items_o = []
        for split in transaction.splits:
            cct_account = self.get_cct_account(split.account)
            credit_type = "debit" if split.amount > 0 else "credit"
            amount = abs(split.amount)
            split_items_o.append({"accountId": cct_account, credit_type: amount})

        payload = dict(
            dateAdded="2025-11-06",
            title="API generated collective entry",
            sequenceNumberId="1000",
            items=json.dumps(split_items_o),
        )

        # Call create endpoint
        response = self._construct_request_post("journal/create.json", payload=payload)
        response.raise_for_status()
        data = response.json()
        self._raise_for_error(
            response, f"create collective transaction: len: {len(transaction.splits)}"
        )

        txn_id = None
        if isinstance(data, dict):
            if data.get("success"):
                txn_id = data.get("insertId")
        # Record inserted transaction for the current BookTransaction
        transaction_id = self.cct_book_ref.build_transaction_id(txn_id)
        self.insert(transaction_id)
        return transaction_id

    def _create_simple_transaction(self, transaction):
        # Expecting two splits: debit and credit
        if not getattr(transaction, "splits", None) or len(transaction.splits) != 2:
            raise ValueError("transaction must contain at exactly two splits (debit and credit)")

        # Resolve CashCtrl account identifiers for all involved accounts
        cct_account_debit = self.get_cct_account(transaction.splits[0].account)
        cct_account_credit = self.get_cct_account(transaction.splits[1].account)

        attributes = f"amount={transaction.splits[1].amount}&creditId={cct_account_credit}&debitId={cct_account_debit}&title={urllib.parse.quote_plus(getattr(transaction, 'description', ''))}&dateAdded={datetime.datetime.now()}&notes={urllib.parse.quote_plus('Added through API"')}"

        # Call create endpoint
        response = self._construct_request_post("journal/create.json?" + attributes, None)
        response.raise_for_status()
        data = response.json()
        self._raise_for_error(
            response,
            f"create:{cct_account_debit}:{cct_account_credit}:{transaction.splits[1].amount}",
        )

        txn_id = None
        if isinstance(data, dict):
            if data.get("success"):
                txn_id = data.get("insertId")
        # Record inserted transaction for the current BookTransaction
        transaction_id = self.cct_book_ref.build_transaction_id(txn_id)
        self.insert(transaction_id)
        return transaction_id

    def save(self):
        # inserted transactions can be ignored as they were already saved to CashCtrl via API
        self._inserted_transaction_ids.clear()
        # for each deleted transaction, delete on CashCtrl via API
        # Call delete endpoint. API expects a comma-separated list of ids in 'ids' param.
        # We reuse the GET-style endpoint as described in comments.
        # Normalize and strip possible book prefix (e.g. 'cct_...')
        self._delete(self._deleted_transaction_ids)
        self._deleted_transaction_ids.clear()

    def get_cct_account(self, account_nbr):
        if account_nbr is None:
            raise ValueError("account number must not be None")
        elif isinstance(account_nbr, Account):
            account_nbr = account_nbr.code
        elif isinstance(account_nbr, str):
            account_nbr = account_nbr
        elif isinstance(account_nbr, int):
            account_nbr = str(account_nbr)

        # Build filter as the CashCtrl REST API expects and URL-encode it
        filter_json = json.dumps([{"comparison": "eq", "field": "number", "value": account_nbr}])
        rest = "account/list.json?filter=" + urllib.parse.quote_plus(filter_json)
        logger.info(f"Fetching CashCtrl account for number {account_nbr} via {rest}")

        response = self._construct_request_get(rest)
        response.raise_for_status()
        self._raise_for_error(response, f"account_lookup:{account_nbr}")
        data = response.json()

        # Expecting a list with a single account; return an identifier used by CashCtrl
        if isinstance(data, dict):
            candidate = data.get("data")
            # Try to extract account id or code
            if isinstance(candidate, list) and candidate and len(candidate) == 1:
                acct = candidate[0]
                return acct.get("id")

        # TODO Throw exception if account not found
        raise ValueError(f"Account with number {account_nbr} not found in CashCtrl.")

    def get_cct_transaction(self, transaction_id):
        # Call _get_api_url + journal/read.json?id=[transaction_id] and fetch the transaction
        # Normalize and strip possible book prefix (e.g. 'cct_...')
        backend_id = self.cct_book_ref.get_backend_id(transaction_id)
        rest = "journal/read.json?id=" + urllib.parse.quote_plus(backend_id)
        response = self._construct_request_get(rest)
        response.raise_for_status()
        try:
            self._raise_for_error(response, f"get_transaction:{backend_id}")
        except RuntimeError:
            return None
        data = response.json()
        return data

    def _delete(self, transaction_ids):
        if transaction_ids and len(transaction_ids) > 0:
            tids = ",".join(
                self.cct_book_ref.get_backend_id(tid)
                if str(tid).startswith(f"{self.cct_book_ref.book_type_id}_")
                else str(tid)
                for tid in transaction_ids
            )
            rest = f"journal/delete.json?ids={urllib.parse.quote_plus(tids)}"
            response = self._construct_request_post(rest)
            response.raise_for_status()
            self._raise_for_error(response, f"delete:{tids}")

    def _get_api_url(self):
        return f"https://{self._cct_tenant}.{self._api_host}/api/v1/"

    def _construct_request_get(self, rest_service):
        url = self._get_api_url() + rest_service
        return requests.get(url, auth=HTTPBasicAuth(self._api_token or "", ""))

    def _construct_request_post(self, rest_service, payload=None):
        url = self._get_api_url() + rest_service

        return requests.post(
            url,
            data=payload,
            auth=HTTPBasicAuth(self._api_token or "", ""),
        )

    def _raise_for_error(self, response, request_info=None):
        # if response success is False, raise exception with message
        data = response.json()
        if isinstance(data, dict):
            if not data.get("success", True):
                error_message = data.get("message", "Unknown error")
                raise RuntimeError(
                    f"CashCtrl API error: {error_message} - for request {request_info}"
                )


class CashctrlBook(AccountingBook):
    book_type_id = "cct"

    _book_transaction: BookTransaction | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_token = self.get_settings_option("API_TOKEN")
        self._cct_tenant = self.get_settings_option("TENANT")
        self._api_host = self.get_settings_option("API_HOST")
        self._open_book_transactional()

    def add_split_transaction(
        self,
        transaction,
        autosave=True,
    ):
        self._open_book_transactional()
        transaction = self._book_transaction.create(transaction)
        if autosave:
            self.save()
        return transaction

    def get_transaction(self, transaction_id):
        # Use the same endpoint as _get_cct_transaction but expose it here
        data = self._book_transaction.get_cct_transaction(transaction_id)
        if data:
            return data
        return None

    def delete_transaction(self, transaction_id, autosave=True):
        cct_transaction = self._book_transaction.get_cct_transaction(transaction_id)

        # Track deletion in current BookTransaction and persist
        if cct_transaction and "data" in cct_transaction:
            self._book_transaction.delete(cct_transaction["data"])
        if autosave:
            self.save()

    def save(self):
        if not self._book_transaction:
            return False
        self._book_transaction.save()
        return True

    def close(self):
        if self._book_transaction:
            self._book_transaction.close()
            self._book_transaction = None

    def open(self):
        self._open_book_transactional()

    def _open_book_transactional(self):
        if self._book_transaction:
            return
        self._book_transaction = BookTransaction(
            self, self.book_type_id, self._api_token, self._cct_tenant, self._api_host
        )
