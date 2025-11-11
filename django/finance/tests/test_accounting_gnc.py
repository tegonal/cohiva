import datetime
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

from django.conf import settings
from django.test import TestCase

from finance.accounting import (
    Account,
    AccountingManager,
    Split,
    Transaction,
)
from finance.accounting.gnucash import GnucashBook


class GnucashBookTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.default_backend_label = "gnucash_test"
        cls.account1 = Account("Test1", "1000")
        cls.account2 = Account("Test2", "2000")
        cls.account3 = Account("Test3", "3000")

    @classmethod
    def tearDownClass(cls):
        AccountingManager.default_backend_label = settings.FINANCIAL_ACCOUNTING_DEFAULT_BACKEND
        super().tearDownClass()

    def test_get_book(self):
        messages = []
        with AccountingManager(messages) as book:
            self.assertTrue(isinstance(book, GnucashBook))
            self.assertEqual(len(messages), 0)

    def test_transactions(self):
        with AccountingManager() as book:
            ## Add
            transaction_id = book.add_transaction(
                100, self.account1, self.account2, "2020-01-01", "Test"
            )
            self.assertTrue(transaction_id.startswith("gnc_0_"))
            self.assertIsInstance(UUID(transaction_id[6:]), UUID)

        with AccountingManager() as book:
            ## Get
            tr = book.get_transaction(transaction_id)
            self.assertTrue(isinstance(tr, Transaction))
            self.assertEqual(len(tr.splits), 2)
            for split in tr.splits:
                self.assertIn(split.account.code, ("1000", "2000"))
                if split.account.code == "1000":
                    self.assertEqual(split.amount, Decimal(-100))
                elif split.account.code == "2000":
                    self.assertEqual(split.amount, Decimal(100))
            self.assertEqual(tr.date, datetime.date(2020, 1, 1))
            self.assertEqual(tr.description, "Test")
            self.assertEqual(tr.currency, "CHF")

            with self.assertRaises(KeyError):
                book.get_transaction("gnc_0_invalid")

        with AccountingManager() as book:
            ## Delete
            book.delete_transaction(transaction_id)
            with self.assertRaises(KeyError):
                book.get_transaction(transaction_id)
            with self.assertRaises(KeyError):
                book.delete_transaction(transaction_id)

    @patch("finance.accounting.gnucash.GnucashBook.save")
    def test_add_split_transaction_and_autosave(
        self,
        mock_save,
    ):
        messages = []
        splits = [
            Split(account=self.account1, amount=150),
            Split(account=self.account2, amount=-50),
            Split(account=self.account3, amount=100),
        ]
        with AccountingManager(messages) as book:
            transaction_id = book.add_split_transaction(
                Transaction(splits, date="2020-01-02", description="Split Transaction Test"),
                autosave=False,
            )
            self.assertFalse(mock_save.called)
            self.assertTrue(transaction_id.startswith("gnc_0_"))
            self.assertIsInstance(UUID(transaction_id[6:]), UUID)
            book.add_split_transaction(
                Transaction(splits, date="2020-01-02", description="Split Transaction Test"),
            )
            mock_save.assert_called_once()
