import datetime
from decimal import Decimal
from unittest.mock import patch

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
from finance.accounting.book import AccountingBook, DummyBook
from finance.accounting.gnucash import GnucashBook
from geno.models import Building


class AccountingManagerTestCase(TestCase):
    def test_manager_init(self):
        m = AccountingManager()
        self.assertEqual(m.backend_label, "dummy_test")
        self.assertEqual(m.backend_class, DummyBook)
        self.assertEqual(m.db_id, 0)
        self.assertEqual(m.backend_obj, None)
        m = AccountingManager(backend_label="gnucash_test")
        self.assertEqual(m.backend_class, GnucashBook)
        m = AccountingManager(book_type_id="dum")
        self.assertEqual(m.backend_label, "dummy_test")
        m = AccountingManager(book_type_id="dum", db_id=1)
        self.assertEqual(m.backend_label, "dummy_test2")

    @patch("finance.accounting.book.DummyBook.close")
    def test_manager_context(self, mock_close):
        with AccountingManager() as book:
            self.assertTrue(isinstance(book, DummyBook))
            self.assertFalse(mock_close.called)
        mock_close.assert_called_once()

    def test_book_unregistered(self):
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

    def test_manager_init_error(self):
        AccountingManager.backends["invalid_class"] = {"class": object, "db_id": 0}
        messages = []
        with AccountingManager(messages, backend_label="invalid_class") as book:
            self.assertEqual(book, None)
            self.assertEqual(len(messages), 1)
            self.assertTrue(messages[0].startswith("Konnte Buchhaltung nicht initialisieren: "))

        with self.assertRaises(TypeError):
            with AccountingManager(backend_label="invalid_class") as book:
                pass

        del AccountingManager.backends["invalid_class"]

    def test_unregister_invalid(self):
        with self.assertRaises(KeyError):
            AccountingManager.unregister("invalid")

    def test_register_and_unregister(self):
        default = AccountingManager.default_backend_label
        AccountingManager.register("test1", DummyBook, db_id=999)
        self.assertIn("test1", AccountingManager.backends)
        AccountingManager.unregister("test1")
        self.assertNotIn("test1", AccountingManager.backends)
        self.assertEqual(AccountingManager.default_backend_label, default)

    def test_register_and_unregister_default(self):
        old_default = AccountingManager.default_backend_label
        AccountingManager.default_backend_label = None
        AccountingManager.register("test1", DummyBook, db_id=999)
        self.assertIn("test1", AccountingManager.backends)
        self.assertEqual(AccountingManager.default_backend_label, "test1")
        AccountingManager.unregister("test1")
        self.assertNotIn("test1", AccountingManager.backends)
        self.assertEqual(AccountingManager.default_backend_label, None)
        AccountingManager.default_backend_label = old_default

    def test_register_multiple(self):
        AccountingManager.unregister_all()
        self.assertEqual(len(AccountingManager.backends), 0)

        AccountingManager.register("test1", DummyBook)
        self.assertEqual(len(AccountingManager.backends), 1)
        self.assertEqual(AccountingManager.backends["test1"]["class"], DummyBook)
        self.assertEqual(AccountingManager.backends["test1"]["db_id"], 0)

        with self.assertRaises(KeyError):
            AccountingManager.register("test2", DummyBook)
        with self.assertRaises(KeyError):
            AccountingManager.register("test1", DummyBook, db_id=1)
        AccountingManager.register("test2", DummyBook, db_id=1)
        self.assertEqual(len(AccountingManager.backends), 2)
        self.assertEqual(AccountingManager.backends["test2"]["class"], DummyBook)
        self.assertEqual(AccountingManager.backends["test2"]["db_id"], 1)

        with self.assertRaises(KeyError):
            AccountingManager.register("test2", GnucashBook)
        AccountingManager.register("test3", GnucashBook)
        self.assertEqual(len(AccountingManager.backends), 3)
        self.assertEqual(AccountingManager.backends["test3"]["class"], GnucashBook)
        self.assertEqual(AccountingManager.backends["test3"]["db_id"], 0)

        AccountingManager.register_backends_from_settings()

    def test_register_backends_from_settings(self):
        AccountingManager.unregister_all()
        self.assertEqual(len(AccountingManager.backends), 0)
        AccountingManager.register("test1", DummyBook)
        self.assertEqual(len(AccountingManager.backends), 1)
        self.assertEqual(AccountingManager.default_backend_label, "test1")

        AccountingManager.register_backends_from_settings()
        self.assertEqual(len(AccountingManager.backends), 5)
        self.assertEqual(AccountingManager.default_backend_label, "dummy_test")
        self.assertEqual(AccountingManager.backends["dummy_test2"]["db_id"], 1)

    def test_get_backend_label_from_book_ids(self):
        self.assertEqual(AccountingManager.get_backend_label_from_book_ids("dum"), "dummy_test")
        self.assertEqual(AccountingManager.get_backend_label_from_book_ids("dum", 0), "dummy_test")
        self.assertEqual(
            AccountingManager.get_backend_label_from_book_ids("dum", 1), "dummy_test2"
        )
        with self.assertRaises(KeyError):
            AccountingManager.get_backend_label_from_book_ids("dum", 2)
        self.assertEqual(AccountingManager.get_backend_label_from_book_ids("gnc"), "gnucash_test")
        self.assertEqual(AccountingManager.get_backend_label_from_book_ids("cct"), "cashctrl_test")
        with self.assertRaises(KeyError):
            AccountingManager.get_backend_label_from_book_ids("invalid")

        AccountingManager.backends["dummy_test_duplicate"] = {"class": DummyBook, "db_id": 0}
        with self.assertRaises(
            KeyError,
            msg=(
                "Mehrere Buchhaltungen mit dem gleichen book_type_id dum "
                "und gleicher DB id 0 gefunden"
            ),
        ):
            AccountingManager.get_backend_label_from_book_ids("dum")
        del AccountingManager.backends["dummy_test_duplicate"]


class AccountTestCase(TestCase):
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


class TransactionTestCase(TestCase):
    def test_strings(self):
        t = Transaction(splits=[Split(account=Account("A", "1"), amount=150)], date="2020-01-02")
        self.assertEqual(str(t), "2020-01-02")
        t.description = "Test Description"
        self.assertEqual(str(t), "2020-01-02 Test Description")
        t.splits.append(Split(account=Account("B", "2"), amount=-50))
        self.assertEqual(str(t), "2020-01-02 CHF 150 A [1] => B [2] Test Description")
        t.splits.append(Split(account=Account("C", "3"), amount=100))
        self.assertEqual(
            str(t), "2020-01-02 CHF 150 A [1] => B [2] (+ 1 weitere Buchung) Test Description"
        )
        t.splits.append(Split(account=Account("D", "4"), amount=0))
        self.assertEqual(
            str(t), "2020-01-02 CHF 150 A [1] => B [2] (+ 2 weitere Buchungen) Test Description"
        )

        self.assertEqual(repr(t), "Transaction(date=2020-01-02, description='Test Description')")


class BookTestCase(TestCase):
    def test_transaction_id(self):
        backend_id = "999"
        with AccountingManager() as book:
            transaction_id = book.build_transaction_id(backend_id)
            self.assertEqual(transaction_id, "dum_0_999")
            self.assertEqual(book.get_backend_id(transaction_id), backend_id)
            with self.assertRaises(ValueError):
                book.get_backend_id("gnc_0_999")
            with self.assertRaises(ValueError):
                book.get_backend_id("dum_1_999")

            self.assertEqual(book.decode_transaction_id("dum_0_999"), ("dum", 0, "999"))
            self.assertEqual(book.decode_transaction_id("dum_0_999_888"), ("dum", 0, "999_888"))
            with self.assertRaises(ValueError):
                book.decode_transaction_id("dum_999")
            with self.assertRaises(ValueError):
                book.decode_transaction_id("999")

    def test_get_date(self):
        ref = datetime.datetime(2000, 1, 1, 0, 0, 0)
        self.assertEqual(AccountingBook.get_date(None), datetime.date.today())
        self.assertEqual(AccountingBook.get_date(ref), ref.date())
        self.assertEqual(AccountingBook.get_date(ref.date()), ref.date())
        self.assertEqual(AccountingBook.get_date("2000-01-01"), ref.date())
        with self.assertRaises(ValueError):
            AccountingBook.get_date("invalid")
        with self.assertRaises(ValueError):
            AccountingBook.get_date(1)


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
        DummyBook.dummy_db = {}
        with AccountingManager() as book:
            transaction_id = book.add_transaction(
                100, Account("Test1", "1000"), Account("Test2", "2000"), "2020-01-01"
            )
        self.assertEqual(transaction_id, f"dum_0_{list(DummyBook.dummy_db[0].keys())[0]}")

    def test_get_transaction(self):
        DummyBook.dummy_db = {}
        with AccountingManager() as book:
            transaction_id = book.add_transaction(
                100, Account("Test1", "1000"), Account("Test2", "2000"), "2020-01-01"
            )
            tr = book.get_transaction(transaction_id)
            self.assertTrue(isinstance(tr, Transaction))
            self.assertEqual(len(tr.splits), 2)
            self.assertEqual(tr.splits[0].amount, Decimal(100))
            self.assertEqual(tr.splits[0].account.code, "1000")
            self.assertEqual(tr.splits[1].amount, Decimal(-100))
            self.assertEqual(tr.splits[1].account.code, "2000")
            self.assertEqual(tr.date, datetime.date(2020, 1, 1))

            with self.assertRaises(KeyError):
                book.get_transaction("dum_0_invalid")

        with AccountingManager(backend_label="dummy_test2") as book:
            self.assertEqual(book._save_transactions, False)
            self.assertEqual(book.get_transaction("invalid"), None)

    def test_delete_transaction(self):
        DummyBook.dummy_db = {}
        with AccountingManager() as book:
            transaction_id = book.add_transaction(
                100, Account("Test1", "1000"), Account("Test2", "2000"), "2020-01-01"
            )
            self.assertEqual(len(book._db), 1)
            book.delete_transaction(transaction_id)
            self.assertEqual(book._db, {})

        with AccountingManager(backend_label="dummy_test2") as book:
            self.assertEqual(book._save_transactions, False)
            self.assertEqual(book.delete_transaction("invalid"), None)

    def test_save(self):
        DummyBook.dummy_db = {}
        with AccountingManager() as book:
            transaction_id = book.add_transaction(
                100,
                Account("Test1", "1000"),
                Account("Test2", "2000"),
                "2020-01-01",
                autosave=False,
            )
            with self.assertRaises(KeyError):
                book.get_transaction(transaction_id)
            book.save()
            tr = book.get_transaction(transaction_id)
            self.assertTrue(isinstance(tr, Transaction))

    def test_add_split_transaction(self):
        DummyBook.dummy_db = {}
        splits = [
            Split(account=Account("Test1", "1000"), amount=150),
            Split(account=Account("Test2", "2000"), amount=-50),
            Split(account=Account("Test3", "3000"), amount=100),
        ]
        with AccountingManager() as book:
            transaction_id = book.add_split_transaction(
                Transaction(splits, date="2020-01-02", description="Split Transaction Test"),
            )
            self.assertTrue(transaction_id.startswith("dum_0_"))
            tr = book.get_transaction(transaction_id)
            self.assertEqual(len(tr.splits), 3)
