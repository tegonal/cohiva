import datetime
import logging
import uuid

from finance.accounting.transaction import Split, Transaction

logger = logging.getLogger("finance_accounting")


class AccountingBook:
    book_type_id = None

    def __init__(self):
        self._transactions = []
        self._book = None

    def add_transaction(
        self,
        amount,
        account_debit,
        account_credit,
        date=None,
        description="",
        currency="CHF",
        autosave=True,
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
        book_type_id, backend_id = transaction_id.split("_", 1)
        if book_type_id != self.book_type_id:
            raise ValueError(
                "book_type_id '{book_type_id}' does not match backend type '{self.book_type_id}'"
            )
        return backend_id

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
        raise ValueError("date must be a string or a datetime.date object")


class DummyBook(AccountingBook):
    book_type_id = "dum"

    def __init__(self):
        super().__init__()
        self.transactions = {}

    def add_split_transaction(
        self,
        transaction,
        autosave=True,
    ):
        if len(transaction.splits) == 2:
            logging.info(f"Add dummy transaction: {transaction}")
        else:
            for split in transaction.splits:
                logging.info(
                    f"Add dummy transaction split: {transaction.date} {transaction.currency} "
                    f"{split.amount} {split.account} {transaction.description}"
                )
        backend_id = uuid.uuid4()
        self.transactions[backend_id] = {"transaction": transaction, "saved": autosave}
        return self.build_transaction_id(backend_id)

    def get_transaction(self, transaction_id):
        backend_id = self.get_backend_id(transaction_id)
        if self.transactions[backend_id]["saved"]:
            return self.transactions[backend_id]["transaction"]
        else:
            raise KeyError(f"Transaction {transaction_id} found")

    def delete_transaction(self, transaction_id):
        backend_id = self.get_backend_id(transaction_id)
        del self.transactions[backend_id]

    def save(self):
        for transaction in self.transactions.values():
            transaction["saved"] = True
