import datetime
import logging
import uuid
from decimal import Decimal

from django.conf import settings

from . import Account
from .transaction import Split, Transaction

logger = logging.getLogger("finance_accounting")


class AccountingBook:
    book_type_id = None

    def __init__(self, settings_label):
        self._transactions = []
        self._book = None
        self._config_name = None
        self._settings_label = settings_label

    def add_transaction(
        self,
        amount: Decimal | float | str,
        account_debit: Account,
        account_credit: Account,
        date: datetime.date | datetime.datetime | str | None = None,
        description: str = "",
        currency: str = "CHF",
        autosave: bool = True,
    ):
        return self.add_split_transaction(
            Transaction(
                [
                    Split(account_debit, -amount),
                    Split(account_credit, amount),
                ],
                date,
                description,
                currency,
            ),
            autosave,
        )

    def add_split_transaction(
        self,
        transaction,
        autosave=True,
    ):
        raise NotImplementedError

    def get_transaction(self, transaction_id):
        raise NotImplementedError

    def delete_transaction(self, transaction_id):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def close(self):
        pass

    def build_transaction_id(self, backend_id):
        return f"{self.book_type_id}_{backend_id}"

    def get_backend_id(self, transaction_id):
        book_type_id, backend_id = self.decode_transaction_id(transaction_id)
        if book_type_id != self.book_type_id:
            raise ValueError(
                "book_type_id '{book_type_id}' does not match backend type '{self.book_type_id}'"
            )
        return backend_id

    def get_settings_option(self, option, default=None):
        config = settings.FINANCIAL_ACCOUNTING_BACKENDS[self._settings_label].get("OPTIONS", {})
        return config.get(option, default)

    @staticmethod
    def decode_transaction_id(transaction_id):
        parts = transaction_id.split("_", 1)
        if len(parts) != 2:
            raise ValueError("Invalid transaction_id: {transaction_id}")
        return parts

    @staticmethod
    def get_date(date):
        if not date:
            return datetime.date.today()
        if isinstance(date, datetime.date):
            return date
        if isinstance(date, str):
            return datetime.datetime.strptime(date, "%Y-%m-%d").date()
        if isinstance(date, datetime.datetime):
            return date.date()
        raise ValueError("date must be a string, datetime.date, or datetime.datetime object")


class DummyBook(AccountingBook):
    book_type_id = "dum"
    transactions = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._save_transactions = self.get_settings_option("SAVE_TRANSACTIONS")

    def add_split_transaction(
        self,
        transaction,
        autosave=True,
    ):
        backend_id = uuid.uuid4()
        if len(transaction.splits) == 2:
            logger.info(f"Add dummy transaction: {transaction} id={backend_id}")
        else:
            for split in transaction.splits:
                logger.info(
                    f"Add dummy transaction split: {transaction.date} {transaction.currency} "
                    f"{split.amount} {split.account} {transaction.description} id={backend_id}"
                )
        if self._save_transactions:
            self.transactions[backend_id] = {"transaction": transaction, "saved": autosave}
        return self.build_transaction_id(backend_id)

    def get_transaction(self, transaction_id):
        if not self._save_transactions:
            return None
        backend_id = self.get_backend_id(transaction_id)
        if self.transactions[backend_id]["saved"]:
            return self.transactions[backend_id]["transaction"]
        else:
            raise KeyError(f"Transaction {transaction_id} found")

    def delete_transaction(self, transaction_id):
        if not self._save_transactions:
            return
        backend_id = self.get_backend_id(transaction_id)
        del self.transactions[backend_id]

    def save(self):
        for transaction in self.transactions.values():
            transaction["saved"] = True
