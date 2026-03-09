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

    def __init__(self, settings_label, db_id):
        self._transactions = []
        self._book = None
        self._config_name = None
        self._settings_label = settings_label
        self.db_id = int(db_id)

    # Convention:
    #   - account_debit: POSITIVE amount, transaction.splits[0]
    #       - receivables account for invoices
    #       - bank account for payments
    #   - account_credit: NEGATIVE amount, transaction.splits[1]
    #       - revenue account for invoices
    #       - receivables account for payments
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
        """Add a transaction with two splits: one for the debit and one for the credit.

        :param account_debit: e.g. receivables account for invoices; bank account for payments
        :param account_credit: e.g. revenue account for invoices; receivables account for payments
        """
        return self.add_split_transaction(
            Transaction(
                [
                    Split(account_debit, amount),
                    Split(account_credit, -amount),
                ],
                date,
                description,
                currency,
            ),
            autosave,
        )

    def add_split_transaction(
        self,
        transaction: Transaction,
        autosave=True,
    ):
        raise NotImplementedError

    def get_transaction(self, transaction_id):
        raise NotImplementedError

    def delete_transaction(self, transaction_id):
        raise NotImplementedError

    def account_exists(self, account: Account):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def close(self):
        pass

    def build_transaction_id(self, backend_id):
        return f"{self.book_type_id}_{self.db_id}_{backend_id}"

    def get_backend_id(self, transaction_id):
        book_type_id, db_id, backend_id = self.decode_transaction_id(transaction_id)
        if book_type_id != self.book_type_id:
            raise ValueError(
                "book_type_id '{book_type_id}' does not match backend type '{self.book_type_id}'"
            )
        if db_id != self.db_id:
            raise ValueError("db_id '{db_id}' does not match backend DB id '{self.db_id}'")
        return backend_id

    def get_settings_option(self, option, default=None):
        config = settings.FINANCIAL_ACCOUNTING_BACKENDS[self._settings_label].get("OPTIONS", {})
        return config.get(option, default)

    @staticmethod
    def decode_transaction_id(transaction_id):
        parts = transaction_id.split("_", 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid transaction_id: {transaction_id}")
        book_type_id = parts[0]
        db_id = int(parts[1])
        backend_id = parts[2]
        return book_type_id, db_id, backend_id

    @staticmethod
    def get_date(date):
        if not date:
            return datetime.date.today()
        if isinstance(date, datetime.datetime):
            return date.date()
        if isinstance(date, datetime.date):
            return date
        if isinstance(date, str):
            return datetime.datetime.strptime(date, "%Y-%m-%d").date()
        raise ValueError("date must be a string, datetime.date, or datetime.datetime object")


class DummyBook(AccountingBook):
    book_type_id = "dum"
    dummy_db = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._save_transactions = self.get_settings_option("SAVE_TRANSACTIONS")
        if self.db_id not in self.dummy_db:
            self.dummy_db[self.db_id] = {}
        self._db = self.dummy_db[self.db_id]

    def add_split_transaction(
        self,
        transaction,
        autosave=True,
    ):
        backend_id = str(uuid.uuid4())
        transaction.date = self.get_date(transaction.date)
        if len(transaction.splits) == 2:
            logger.info(f"Add dummy transaction: {transaction} id={backend_id}")
        else:
            for split in transaction.splits:
                split.amount = Decimal(split.amount)
                logger.info(
                    f"Add dummy transaction split: {transaction.date} {transaction.currency} "
                    f"{split.amount} {split.account.code} {transaction.description} "
                    f"id={backend_id}"
                )
        if self._save_transactions:
            self._db[backend_id] = {"transaction": transaction, "saved": autosave}
        return self.build_transaction_id(backend_id)

    def get_transaction(self, transaction_id):
        if not self._save_transactions:
            return None
        backend_id = self.get_backend_id(transaction_id)
        if self._db[backend_id]["saved"]:
            return self._db[backend_id]["transaction"]
        else:
            raise KeyError(f"Transaction {transaction_id} not found")

    def delete_transaction(self, transaction_id):
        if not self._save_transactions:
            return
        backend_id = self.get_backend_id(transaction_id)
        del self._db[backend_id]

    def account_exists(self, account: Account):
        # DummyBook accounts always exist
        return True

    def save(self):
        for transaction in self._db.values():
            transaction["saved"] = True
