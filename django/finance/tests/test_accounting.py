from unittest.mock import patch
from uuid import UUID

from django.test import TestCase

from finance.accounting import AccountingManager, CashctrlBook, DummyBook, GnucashBook
from finance.accounting.accounts import Account, AccountKey, AccountRole


class AccountingTestCase(TestCase):
    def test_get_book_unregistered(self):
        AccountingManager.unregister_all()
        messages = []
        with AccountingManager(messages) as book:
            self.assertEqual(book, None)
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0], "No accounting backend configured.")

    def test_account_minimal(self):
        account = Account("Test", "1000")
        self.assertEqual(account.name, "Test")
        self.assertEqual(account.code, "1000")
        self.assertEqual(account.role, AccountRole.DEFAULT)
        self.assertEqual(account.iban, None)
        self.assertEqual(account.account_iban, None)

    def test_account_iban(self):
        account = Account(
            code="2000",
            name="Test IBAN",
            iban="CH111111111111111",
            account_iban="CH2222222222222222",
            role=AccountRole.QR_DEBTOR,
        )
        self.assertEqual(account.name, "Test IBAN")
        self.assertEqual(account.code, "2000")
        self.assertEqual(account.role, AccountRole.QR_DEBTOR)
        self.assertEqual(account.iban, "CH111111111111111")
        self.assertEqual(account.account_iban, "CH2222222222222222")

    def test_account_from_settings(self):
        account = Account.from_settings(AccountKey.DEFAULT_DEBTOR)
        self.assertEqual(account.name, "Bankkonto QR-Einzahlungen")
        self.assertEqual(account.code, "1020.1")
        self.assertEqual(account.role, AccountRole.QR_DEBTOR)
        self.assertEqual(account.iban, "CH7730000001250094239")
        self.assertEqual(account.account_iban, None)


class DummyBookTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.unregister_all()
        AccountingManager.register(DummyBook)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_get_book(self):
        messages = []
        with AccountingManager(messages) as book:
            self.assertTrue(isinstance(book, DummyBook))
            self.assertEqual(len(messages), 0)

    def test_add_transaction(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(100, "1000", "2000", "2020-01-01")
        self.assertTrue(transaction_id.startswith("dum_"))


class GnucashBookTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.unregister_all()
        AccountingManager.register(GnucashBook)
        cls.account1 = Account("Test1", "1000")
        cls.account2 = Account("Test2", "2000")
        cls.account3 = Account("Test3", "3000")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_get_book(self):
        messages = []
        with AccountingManager(messages) as book:
            self.assertTrue(isinstance(book, GnucashBook))
            self.assertEqual(len(messages), 0)

    def test_add_transaction(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                100, self.account1, self.account2, "2020-01-01", "Test"
            )
            self.assertTrue(transaction_id.startswith("gnc_"))
            self.assertIsInstance(UUID(transaction_id[4:]), UUID)

    @patch("finance.accounting.book.GnucashBook.save")
    def test_add_split_transaction_and_autosave(
        self,
        mock_save,
    ):
        messages = []
        splits = [
            {"account": self.account1, "amount": 150},
            {"account": self.account2, "amount": -50},
            {"account": self.account3, "amount": -100},
        ]
        with AccountingManager(messages) as book:
            transaction_id = book.add_split_transaction(
                splits, date="2020-01-02", description="Split Transaction Test", autosave=False
            )
            self.assertFalse(mock_save.called)
            self.assertTrue(transaction_id.startswith("gnc_"))
            self.assertIsInstance(UUID(transaction_id[4:]), UUID)
            book.add_split_transaction(
                splits,
                date="2020-01-02",
                description="Split Transaction Test",
            )
            mock_save.assert_called_once()


class CashctrlBookTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.unregister_all()
        AccountingManager.register(CashctrlBook)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
