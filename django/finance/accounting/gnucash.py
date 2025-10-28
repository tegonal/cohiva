import datetime
import warnings
from decimal import Decimal

import piecash
from django.conf import settings
from sqlalchemy import exc as sa_exc

from finance.accounting.accounts import Account
from finance.accounting.book import AccountingBook
from finance.accounting.transaction import Split, Transaction

# logger = logging.getLogger("finance_accounting")


class GnucashBook(AccountingBook):
    book_type_id = "gnc"

    def __init__(self):
        super().__init__()
        self._open_book()

    def add_split_transaction(
        self,
        splits,
        date=None,
        description="",
        currency="CHF",
        autosave=True,
    ):
        self._open_book()
        txn = piecash.Transaction(
            post_date=self.get_date(date),
            enter_date=datetime.datetime.now(),
            currency=self._book.currencies(mnemonic="CHF"),
            description=description,
        )
        for split in splits:
            amount = split["amount"]
            if isinstance(amount, Decimal):
                amount_dec = amount
            else:
                amount_dec = Decimal(amount)
            piecash.Split(
                account=self._get_gnc_account(split["account"]),
                value=amount_dec,
                memo="",
                transaction=txn,
            )
        if autosave:
            self.save()
        else:
            self._book.flush()
        return f"{self.book_type_id}_{txn.guid}"

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
        if settings.GNUCASH_IGNORE_SQLALCHEMY_WARNINGS:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=sa_exc.SAWarning)
                self._book = piecash.open_book(
                    uri_conn=settings.GNUCASH_DB_SECRET,
                    readonly=settings.GNUCASH_READONLY,
                    do_backup=False,
                )
        else:
            self._book = piecash.open_book(
                uri_conn=settings.GNUCASH_DB_SECRET,
                readonly=settings.GNUCASH_READONLY,
                do_backup=False,
            )

    def _get_gnc_account(self, account):
        return self._book.accounts(code=account.code)

    def _get_gnc_transaction(self, transaction_id):
        backend_id = self.get_backend_id(transaction_id)
        self._open_book()
        return self._book.transactions.get(guid=backend_id)
