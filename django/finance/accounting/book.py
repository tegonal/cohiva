import datetime
import logging
import uuid
import warnings
from decimal import Decimal

import piecash
from django.conf import settings
from sqlalchemy import exc as sa_exc

logger = logging.getLogger("finance_accounting")


class AccountingBook:
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
            [
                {"account": account_debit, "amount": -amount},
                {"account": account_credit, "amount": amount},
            ],
            date,
            description,
            currency,
            autosave,
        )

    def add_split_transaction(
        self,
        splits,
        date=None,
        description="",
        currency="CHF",
        autosave=True,
    ):
        raise NotImplementedError

    def get_account(self, account_number):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def close(self):
        pass

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

    def add_split_transaction(
        self,
        splits,
        date=None,
        description="",
        currency="CHF",
        autosave=True,
    ):
        if len(splits) == 2:
            logging.info(
                f"Add dummy transaction: {date} {currency} {splits[0]['amount']}  "
                f"{splits[0]['account']} => {splits[1]['account']} {description}"
            )
        else:
            for split in splits:
                logging.info(
                    f"Add dummy transaction split: {date} {currency} {split['amount']} "
                    f"{split['account']} {description}"
                )
        return f"{self.book_type_id}_{uuid.uuid4()}"


class GnucashBook(AccountingBook):
    book_type_id = "gnc"

    def __init__(self):
        super().__init__()
        self.open_book()

    def add_split_transaction(
        self,
        splits,
        date=None,
        description="",
        currency="CHF",
        autosave=True,
    ):
        self.open_book()
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
                account=self.get_account(split["account"]),
                value=amount_dec,
                memo="",
                transaction=txn,
            )
        if autosave:
            self.save()
        else:
            self._book.flush()
        return f"{self.book_type_id}_{txn.guid}"

    def open_book(self):
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

    def save(self):
        if not self._book:
            return False
        self._book.save()
        return True

    def close(self):
        if self._book:
            self._book.close()
            self._book = None

    def get_account(self, account):
        return self._book.accounts(code=account.code)


class CashctrlBook(AccountingBook):
    book_type_id = "cct"
