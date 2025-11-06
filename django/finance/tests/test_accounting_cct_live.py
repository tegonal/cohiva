import unittest

from django.conf import settings
from django.test import TestCase

from finance.accounting import (
    Account,
    AccountingManager,
    CashctrlBook,
    Split,
    Transaction,
)


# Disabled by default. May be used to run live tests against a CashCtrl test instance.
@unittest.skipUnless(getattr(settings, "FINANCIAL_ACCOUNTING_CASHCTRL_LIVE_TESTS", False), "CashCtrl live tests are disabled in settings.")
class CashctrlBookTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.default_backend_label = "cashctrl_test"
        cls.account1 = Account("TestAccount CashCtrl1", "43000")
        cls.account2 = Account("TestAccount CashCtrl2", "10220")
        cls.account3 = Account("TestAccount CashCtrl3", "47400")

    @classmethod
    def tearDownClass(cls):
        AccountingManager.default_backend_label = settings.FINANCIAL_ACCOUNTING_DEFAULT_BACKEND
        super().tearDownClass()

    def test_get_book(self):
        messages = []
        with AccountingManager(messages) as book:
            self.assertTrue(isinstance(book, CashctrlBook))
            self.assertEqual(len(messages), 0)

    def test_add_transaction(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                100.00, self.account1, self.account2, "2026-01-01", "Test CashCtrl add_transaction", autosave=False
            )
            self.assertTrue(transaction_id.startswith("cct_"))
            book.save()


    def test_add_transaction_no_commit(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                100.00, self.account1, self.account2, "2026-01-01", "Test CashCtrl add_transaction_no_commit", autosave=False
            )

            self.assertTrue(transaction_id.startswith("cct_"))
            book.close()

    def test_add_transaction_split(self):
        messages = []
        with (AccountingManager(messages) as book):
            transaction_id = book.add_split_transaction(
                Transaction(
                    [
                        Split(self.account1, 800),
                        Split(self.account2, -500),
                        Split(self.account3, -300),
                    ],
                    "2026-01-01",
                    "Split or collective transaction test",
                    "CHF",
                ),
                True,
            )
            book.save()


    def test_delete_transaction(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                300.00, self.account2, self.account3, "2026-02-01", "Test CashCtrl delete_transaction"
            )
            self.assertTrue(transaction_id.startswith("cct_"))

            book.save()
            book.delete_transaction(transaction_id, autosave=False)
            book.save()

