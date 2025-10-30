import datetime
import json
import logging
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from .book import AccountingBook

logger = logging.getLogger("finance_accounting")


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
        tids = ",".join(
            str(tid).split("_", 1)[1]
            if str(tid).startswith(f"{self.cct_book_ref.book_type_id}_")
            else str(tid)
            for tid in self._inserted_transaction_ids
        )
        rest = f"journal/delete.json?ids={urllib.parse.quote_plus(tids)}"
        response = self._construct_post(rest)
        response.raise_for_status()
        self._raise_for_error(response)
        self._inserted_transaction_ids = []

        # deleted transactions can be ignored as they were not yet saved to CashCtrl
        self._deleted_transaction_ids = []

    def insert(self, transaction):
        self._inserted_transaction_ids.append(transaction)

    def delete(self, transaction):
        self._deleted_transaction_ids.append(transaction)

    def create(self, transaction):
        # Expecting two splits: debit and credit
        if not getattr(transaction, "splits", None) or len(transaction.splits) < 2:
            raise ValueError("transaction must contain at least two splits (debit and credit)")

        # Resolve CashCtrl account identifiers for the two sides
        cct_account_debit = self.get_cct_account(transaction.splits[0].account)
        cct_account_credit = self.get_cct_account(transaction.splits[1].account)

        attributes = f"amount={urllib.parse.quote_plus(transaction.splits[0].amount)}&creditId={urllib.parse.quote_plus(cct_account_credit)}&debitId={urllib.parse.quote_plus(cct_account_debit)}&title={urllib.parse.quote_plus(getattr(transaction, 'description', ''))}&dateAdded={datetime.datetime.now()}&notes=Added through API"

        # Call create endpoint
        response = self._construct_post("journal/create.json?" + attributes, None)
        response.raise_for_status()
        data = response.json()
        self._raise_for_error(response)

        txn_id = None
        if isinstance(data, dict):
            if data.get("success"):
                txn_id = data.get("insertId")
        # Record inserted transaction for the current BookTransaction
        transaction = f"{self.cct_book_ref.book_type_id}_{txn_id}"
        self.insert(transaction)
        return transaction

    def save(self):
        # inserted transactions can be ignored as they were already saved to CashCtrl via API
        self._inserted_transaction_ids = []
        # for each deleted transaction, delete on CashCtrl via API
        # Call delete endpoint. API expects a comma-separated list of ids in 'ids' param.
        # We reuse the GET-style endpoint as described in comments.
        # Normalize and strip possible book prefix (e.g. 'cct_...')
        tids = ",".join(
            str(tid).split("_", 1)[1]
            if str(tid).startswith(f"{self.cct_book_ref.book_type_id}_")
            else str(tid)
            for tid in self._deleted_transaction_ids
        )
        rest = f"journal/delete.json?ids={urllib.parse.quote_plus(tids)}"
        response = self._construct_post(rest)
        response.raise_for_status()
        self._raise_for_error(response)
        self._deleted_transaction_ids = []

    def get_cct_account(self, account_nbr):
        if account_nbr is None:
            raise ValueError("account number must not be None")
        if isinstance(account_nbr, str):
            account_nbr = account_nbr
        elif isinstance(account_nbr, int):
            account_nbr = str(account_nbr)

        # Build filter as the CashCtrl REST API expects and URL-encode it
        # comment suggested: account/list.json?filter=[{accountId=[account]}]
        filter_json = json.dumps([{"number": account_nbr}])
        rest = "account/list.json?filter=" + urllib.parse.quote_plus(filter_json)
        logger.info(f"Fetching CashCtrl account for number {account_nbr} via {rest}")

        response = self._construct_request(rest)
        response.raise_for_status()
        self._raise_for_error(response)
        data = response.json()

        # Expecting a list with a single account; return an identifier used by CashCtrl
        if isinstance(data, dict):
            candidate = data.get("data")
            # Try to extract account id or code
            if isinstance(candidate, list) and candidate:
                acct = candidate[0]
                return acct.get("id")

        # TODO Throw exception if account not found
        raise ValueError(f"Account with number {account_nbr} not found in CashCtrl.")

    def get_cct_transaction(self, transaction_id):
        # Call _get_api_url + journal/read.json?id=[transaction_id] and fetch the transaction
        # Normalize and strip possible book prefix (e.g. 'cct_...')
        tid = str(transaction_id)
        if tid.startswith(f"{self.book_type_id}_"):
            tid = tid.split("_", 1)[1]
        rest = "journal/read.json?id=" + urllib.parse.quote_plus(tid)
        response = self._construct_request(rest)
        response.raise_for_status()
        data = response.json()
        return data

    def _get_api_url(self):
        return f"https://{self._cct_tenant}.{self._api_host}/api/v1/"

    def _construct_request(self, rest_service):
        url = self._get_api_url() + rest_service
        return requests.get(url, auth=HTTPBasicAuth(self._api_token or "", ""))

    def _construct_post(self, rest_service, payload=None):
        url = self._get_api_url() + rest_service
        headers = {"Content-Type": "application/json"}
        return requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=HTTPBasicAuth(self._api_token or "", ""),
        )

    def _raise_for_error(self, response):
        # if response success is False, raise exception with message
        data = response.json()
        if isinstance(data, dict):
            if not data.get("success", True):
                error_message = data.get("message", "Unknown error")
                raise RuntimeError(f"CashCtrl API error: {error_message}")


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
        return data

    def delete_transaction(self, transaction_id):
        cct_transaction = self._book_transaction.get_cct_transaction(transaction_id)

        # Track deletion in current BookTransaction and persist
        if self._book_transaction is not None:
            self._book_transaction.delete(cct_transaction)
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

    def _open_book_transactional(self):
        if self._book_transaction:
            return
        self._book_transaction = BookTransaction(
            self, self.book_type_id, self._api_token, self._cct_tenant, self._api_host
        )
