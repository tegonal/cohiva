
from django.conf import settings
from django.test import TestCase

from finance.accounting import (
    Account,
    AccountingManager,
    CashctrlBook,
)


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
            # clean up
            book.delete_transaction(transaction_id)
            book.save()

    def test_add_transaction_no_commit(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                100.00, self.account1, self.account2, "2026-01-01", "Test CashCtrl add_transaction_no_commit", autosave=False
            )
            self.assertTrue(transaction_id.startswith("cct_"))
            book.close()
            book.open()
            transaction = book.get_transaction(
                transaction_id
            )  # should not be found after deletion
            self.assertFalse(transaction, "Transaction should have been deleted")

    def test_delete_transaction(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                300.00, self.account2, self.account3, "2026-02-01", "Test CashCtrl delete_transaction"
            )
            self.assertTrue(transaction_id.startswith("cct_"))
            book.delete_transaction(transaction_id)
            book.save()
            transaction = book.get_transaction(transaction_id) # should not be found after deletion
            self.assertFalse(transaction, "Transaction should have been deleted")
