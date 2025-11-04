import datetime
import warnings
from decimal import Decimal

import piecash
from sqlalchemy import exc as sa_exc

from .account import Account
from .book import AccountingBook
from .transaction import Split, Transaction

# logger = logging.getLogger("finance_accounting")


class GnucashBook(AccountingBook):
    book_type_id = "gnc"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._open_book()

    def add_split_transaction(
        self,
        transaction,
        autosave=True,
    ):
        self._open_book()
        txn = piecash.Transaction(
            post_date=self.get_date(transaction.date),
            enter_date=datetime.datetime.now(),
            currency=self._book.currencies(mnemonic=transaction.currency),
            description=transaction.description,
        )
        for split in transaction.splits:
            if isinstance(split.amount, Decimal):
                amount_dec = split.amount
            else:
                amount_dec = Decimal(split.amount)
            piecash.Split(
                account=self._get_gnc_account(split.account),
                value=amount_dec,
                memo="",
                transaction=txn,
            )
        if autosave:
            self.save()
        else:
            self._book.flush()
        return self.build_transaction_id(txn.guid)

    def get_transaction(self, transaction_id):
        gnc_transaction = self._get_gnc_transaction(transaction_id)
        return Transaction(
            splits=[
                Split(
                    account=Account(split.account.name, split.account.code),
                    amount=split.value,
                )
                for split in gnc_transaction.splits
            ],
            date=gnc_transaction.post_date,
            description=gnc_transaction.description,
            currency=gnc_transaction.currency.mnemonic,
        )

    def delete_transaction(self, transaction_id):
        gnc_transaction = self._get_gnc_transaction(transaction_id)
        self._book.delete(gnc_transaction)
        self.save()

    def save(self):
        if not self._book:
            return False
        self._book.save()
        return True

    def close(self):
        if self._book:
            self._book.close()
            self._book = None

    def _open_book(self):
        if self._book:
            return
        if self.get_settings_option("IGNORE_SQLALCHEMY_WARNINGS"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=sa_exc.SAWarning)
                self._book = piecash.open_book(
                    uri_conn=self.get_settings_option("DB_SECRET"),
                    readonly=self.get_settings_option("READONLY", False),
                    do_backup=False,
                )
        else:
            self._book = piecash.open_book(
                uri_conn=self.get_settings_option("DB_SECRET"),
                readonly=self.get_settings_option("READONLY", False),
                do_backup=False,
            )

    def _get_gnc_account(self, account):
        return self._book.accounts(code=account.code)

    def _get_gnc_transaction(self, transaction_id):
        backend_id = self.get_backend_id(transaction_id)
        self._open_book()
        return self._book.transactions.get(guid=backend_id)
