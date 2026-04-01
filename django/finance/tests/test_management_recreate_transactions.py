import datetime

from finance.accounting import (
    Account,
    AccountingManager,
    AccountKey,
    Transaction,
)
from finance.management.commands.recreate_transactions import Command as recreate_transactions
from geno.billing import add_invoice_obj, get_income_account, get_receivables_account
from geno.models import Invoice, InvoiceCategory
from geno.tests.base import GenoAdminTestCase


class ManagementRecreateTransactionTestCase(GenoAdminTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ic = InvoiceCategory.objects.first()
        diff_payment_account = Account.from_settings(AccountKey.DEFAULT_DEBTOR)
        diff_receivables_account = Account.from_settings(AccountKey.DEFAULT_RECEIVABLES)
        payment_account = get_income_account(ic, None, None)
        receivables_account = get_receivables_account(ic, None)
        ## Add invoices for currently configured book
        with AccountingManager() as book:
            add_invoice_obj(
                book,
                "Payment",  # invoice_type,
                ic,
                "Test current 1",
                cls.addresses[0],
                payment_account,
                receivables_account,
                datetime.date(2026, 1, 15),
                101,
                contract=None,
                year=None,
                month=None,
                transaction_id="test-id1",
                reference_nr="test-ref1",
                additional_info="test-extra-info1",
                dry_run=False,
            )
            add_invoice_obj(
                book,
                "Payment",  # invoice_type,
                ic,
                "Test current 2",
                cls.addresses[0],
                payment_account,
                receivables_account,
                datetime.date(2026, 2, 15),
                102,
                contract=None,
                year=None,
                month=None,
                transaction_id="test-id2",
                reference_nr="test-ref2",
                additional_info="test-extra-info2",
                dry_run=False,
            )
        ## Add invoices for different book
        with AccountingManager(backend_label="dummy_test2") as book:
            add_invoice_obj(
                book,
                "Payment",  # invoice_type,
                ic,
                "Test other 1",
                cls.addresses[0],
                payment_account,
                receivables_account,
                datetime.date(2026, 1, 1),
                101,
                contract=None,
                year=None,
                month=None,
                transaction_id="test-other-id1",
                reference_nr="test-other-ref1",
                additional_info="test-other-extra-info1",
                dry_run=False,
            )
            add_invoice_obj(
                book,
                "Payment",  # invoice_type,
                ic,
                "Test other 2",
                cls.addresses[0],
                payment_account,
                receivables_account,
                datetime.date(2026, 1, 15),
                102,
                contract=None,
                year=None,
                month=None,
                transaction_id="test-other-id2",
                reference_nr="test-other-ref2",
                additional_info="test-other-extra-info2",
                dry_run=False,
            )
            add_invoice_obj(
                book,
                "Payment",  # invoice_type,
                ic,
                "Test other just before cutoff date",
                cls.addresses[0],
                payment_account,
                receivables_account,
                datetime.date(2025, 12, 31),
                103,
                contract=None,
                year=None,
                month=None,
                transaction_id="test-other-id3",
                reference_nr="test-other-ref3",
                additional_info="test-other-extra-info3",
                dry_run=False,
            )
            add_invoice_obj(
                book,
                "Payment",  # invoice_type,
                ic,
                "Test with different accounts",
                cls.addresses[0],
                diff_payment_account,
                diff_receivables_account,
                datetime.date(2025, 12, 31),
                103,
                contract=None,
                year=None,
                month=None,
                transaction_id="test-other-id4",
                reference_nr="test-other-ref4",
                additional_info="test-other-extra-info4",
                dry_run=False,
            )

    def test_get_invoices(self):
        command = recreate_transactions()
        with AccountingManager() as book:
            start_date = datetime.date(2026, 1, 1)
            invoices = command.get_invoices(book, start_date)
        self.assertEqual(len(invoices), 2)
        self.assertEqual(invoices[0].reference_nr, "test-other-ref1")
        self.assertEqual(invoices[1].reference_nr, "test-other-ref2")

    def test_recreate_transactions_dry_run(self):
        command = recreate_transactions()
        invoices = Invoice.objects.filter(name__startswith="Test other")
        old_refs = []
        for invoice in invoices:
            old_refs.append(invoice.fin_transaction_ref)
        with AccountingManager() as book:
            output = command.recreate_transactions(book, invoices, dry_run=True)
        self.assertEqual(len(output), len(old_refs) * 2 + 7)
        invoices_new = Invoice.objects.filter(name__startswith="Test other")
        for i, invoice_new in enumerate(invoices_new):
            self.assertEqual(old_refs[i], invoice_new.fin_transaction_ref)
            with self.assertRaises(ValueError):
                book.get_transaction(invoice_new.fin_transaction_ref)

    def test_recreate_transactions(self):
        command = recreate_transactions()
        invoices = Invoice.objects.filter(name__startswith="Test other")
        old_refs = []
        for invoice in invoices:
            old_refs.append(invoice.fin_transaction_ref)
        with AccountingManager() as book:
            output = command.recreate_transactions(book, invoices, dry_run=False)
        self.assertEqual(len(output), len(old_refs) * 2 + 7)
        invoices_new = Invoice.objects.filter(name__startswith="Test other")
        for i, invoice_new in enumerate(invoices_new):
            self.assertNotEqual(old_refs[i], invoice_new.fin_transaction_ref)
            tr = book.get_transaction(invoice_new.fin_transaction_ref)
            self.assertTrue(isinstance(tr, Transaction))
            self.assertEqual(len(tr.splits), 2)
            # self.assertEqual(tr.splits[0].amount, invoice.new.amount)
            # self.assertEqual(tr.splits[0].account.code, "1000")
            # self.assertEqual(tr.splits[1].amount, Decimal(-100))
            # self.assertEqual(tr.splits[1].account.code, "2000")
            self.assertEqual(tr.date, invoice_new.date)
