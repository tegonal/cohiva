from unittest.mock import patch
from uuid import UUID

from django.conf import settings
from django.test import TestCase

from finance.accounting import (
    Account,
    AccountingManager,
    AccountKey,
    AccountRole,
    Split,
    Transaction,
)
from finance.accounting.book import DummyBook
from finance.accounting.gnucash import GnucashBook
from geno.models import Building


class AccountingTestCase(TestCase):
    def test_get_book_unregistered(self):
        AccountingManager.unregister_all()
        messages = []
        with AccountingManager(messages) as book:
            self.assertEqual(book, None)
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0], "Keine Buchhaltungsanbindung konfiguriert.")

        with self.assertRaises(RuntimeError, msg="Keine Buchhaltungsanbindung konfiguriert."):
            with AccountingManager() as book:
                pass
        AccountingManager.register_backends_from_settings()

    def test_account_minimal(self):
        account = Account("Test", "1000")
        self.assertEqual(account.name, "Test")
        self.assertEqual(account.code, "1000")
        self.assertEqual(account.role, AccountRole.DEFAULT)
        self.assertEqual(account.iban, None)
        self.assertEqual(account.account_iban, None)

    def test_account_iban(self):
        account = Account(
            prefix="2000",
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

    def test_set_account_code(self):
        account = Account("test", prefix="1312")
        self.assertEqual(account.code, account.prefix)
        account.set_code()
        self.assertEqual(account.code, account.prefix)
        account = Account("test", prefix="1312", building_based=True).set_code()
        self.assertEqual(account.code, account.prefix)

        building = Building.objects.create(name="b1", accounting_postfix=1)
        account = Account("test", prefix="1312").set_code(building=building)
        self.assertEqual(account.code, "1312")
        account = Account("test", prefix="1312", building_based=True).set_code(building=building)
        self.assertEqual(account.code, "1312001")
        account.building_based = False
        account.set_code(building=building)
        self.assertEqual(account.code, "1312")


class DummyBookTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.default_backend_label = "dummy_test"

    @classmethod
    def tearDownClass(cls):
        AccountingManager.default_backend_label = settings.FINANCIAL_ACCOUNTING_DEFAULT_BACKEND
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

    def test_add_transaction(self):
        messages = []
        with AccountingManager(messages) as book:
            transaction_id = book.add_transaction(
                100, self.account1, self.account2, "2020-01-01", "Test"
            )
            self.assertTrue(transaction_id.startswith("gnc_"))
            self.assertIsInstance(UUID(transaction_id[4:]), UUID)

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
            self.assertTrue(transaction_id.startswith("gnc_"))
            self.assertIsInstance(UUID(transaction_id[4:]), UUID)
            book.add_split_transaction(
                Transaction(splits, date="2020-01-02", description="Split Transaction Test"),
            )
            mock_save.assert_called_once()
