import datetime
from decimal import Decimal

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

# from pprint import pprint
from django.db.models import Sum  # , Q
from django.template import loader

import geno.tests.data as testdata
from finance.accounting import AccountingManager, AccountKey
from geno.billing import create_invoices, get_reference_nr
from geno.invoice import InvoiceCreator, InvoiceCreatorError, InvoiceNotUnique
from geno.models import Contract, Invoice, InvoiceCategory

# from geno.forms import MemberMailActionForm
from .base import GenoAdminTestCase


# 1. Test invoice if one of multiple rental_object is removed from contract.
class InvoicesTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_contracts(cls)

    def test_invoices_create_and_delete(self):
        create_invoices(dry_run=False, reference_date=datetime.datetime(2001, 4, 15))

        transaction_ids = []
        with AccountingManager() as book:
            for invoice in Invoice.objects.all():
                self.assertEqual(invoice.year, 2001)
                self.assertEqual(invoice.month, 4)
                self.assertEqual(invoice.contract, self.contracts[0])
                self.assertEqual(invoice.invoice_type, "Invoice")
                self.assertEqual(
                    invoice.invoice_category, self.invoicecategories[1]
                )  # Mietzins wiederkehrend
                tr = book.get_transaction(invoice.fin_transaction_ref)
                self.assertIn(invoice.name, tr.description)
                transaction_ids.append(invoice.fin_transaction_ref)

        Invoice.objects.all().delete()

        with AccountingManager() as book:
            for tid in transaction_ids:
                with self.assertRaises(KeyError):
                    book.get_transaction(tid)

    def test_invoices_when_rental_object_removed(self):
        msg = create_invoices(dry_run=False, reference_date=datetime.datetime(2001, 4, 15))
        # print(msg)
        # print("=====")
        self.assertIn("Montasrechnung hinzugefügt: Nettomiete 04.2001 für 001a/001b für", msg[0])
        self.assertIn("Montasrechnung hinzugefügt: Nebenkosten 04.2001 für 001a/001b für", msg[1])
        self.assertIn("Email mit QR-Rechnung an &quot;Anna Muster&quot;", msg[2])
        self.assertEqual("1 Rechnung für 1 Vertrag", msg[3])
        self.assertEqual(len(msg), 4)
        self.assert_invoices(2, 1100 + 220)

        self.assertEmailSent(1, "Mietzinsrechnung 04.2001", "Liebe Anna\n\nAnbei die Rechnung.")

        rental_unit_to_remove = self.rentalunits[1]
        self.contracts[0].rental_units.remove(rental_unit_to_remove)

        msg = create_invoices(dry_run=False, reference_date=datetime.datetime(2001, 6, 15))
        # print(msg)
        # print("=====")
        self.assertIn("Montasrechnung hinzugefügt: Nettomiete 06.2001 für 001a für", msg[0])
        self.assertIn("Montasrechnung hinzugefügt: Nettomiete 05.2001 für 001a für", msg[2])
        self.assertEqual("2 Rechnungen für 1 Vertrag", msg[4])
        self.assert_invoices(3 * 2, 3 * 1100 + 220)

    def test_invoices_when_moving_rental_object_to_separate_contract_with_link(self):
        create_invoices(dry_run=False, reference_date=datetime.datetime(2001, 6, 15))
        self.assert_invoices(3 * 2, 3 * 1100 + 3 * 220)

        rental_unit_to_move = self.rentalunits[1]
        self.contracts[0].rental_units.remove(rental_unit_to_move)
        new_contract = Contract.objects.create(
            comment="New contract with moved unit",
            state="unterzeichnet",
            date=datetime.date(2001, 7, 1),
        )
        new_contract.rental_units.set((rental_unit_to_move,))
        new_contract.contractors.set(self.addresses[0:2])
        new_contract.billing_contract = self.contracts[0]
        new_contract.save()

        create_invoices(dry_run=False, reference_date=datetime.datetime(2001, 7, 15))
        self.assert_invoices(4 * 2 + 3, 4 * 1100 + 4 * 220)

    def assert_invoices(self, count, total):
        invoices = Invoice.objects.all()
        self.assertEqual(invoices.count(), count)
        self.assertEqual(invoices.aggregate(sum_=Sum("amount")).get("sum_"), total)

    def test_invoice_creator(self):
        with self.assertRaises(InvoiceCategory.DoesNotExist):
            ic = InvoiceCreator("Invalid Invoice", dry_run=False)
        ic = InvoiceCreator("Member Invoice", dry_run=False)
        ic.add_line("Line One", 10.00)
        ic.add_line("Line Two", 20.00)
        ic.extra_text = "...Extra text test..."
        ic.create_and_send(self.addresses[0], comment="InvoiceCreator Test", check_unique=True)
        self.assert_invoices(1, 30.00)
        self.assertIn("Rechnung Member Invoice", mail.outbox[0].subject)

        with self.assertRaises(InvoiceNotUnique):
            ic.create_and_send(self.addresses[0], comment="InvoiceCreator Test", check_unique=True)

        with self.assertRaisesMessage(InvoiceCreatorError, "Invoice object exists already"):
            ic.create_and_send(
                self.addresses[0], comment="InvoiceCreator Test", check_unique=False
            )

        ic2 = InvoiceCreator("Member Invoice", dry_run=False)
        ic2.add_line("Only one line", 30.00)

        with self.assertRaises(InvoiceNotUnique):
            ic2.create_and_send(
                self.addresses[0], comment="InvoiceCreator Test2", check_unique=True
            )

        ic2.create_and_send(self.addresses[0], comment="InvoiceCreator Test2", check_unique=False)
        self.assert_invoices(2, 2 * 30.00)

        ic3 = InvoiceCreator("Member Invoice", dry_run=False)
        ic3.add_line("Only one line", 1.00)
        ic3.create_and_send(self.addresses[0], comment="InvoiceCreator Test3", check_unique=True)
        self.assert_invoices(3, 2 * 30.00 + 1)

        self.assertEqual(len(mail.outbox), 3)

    def test_invoice_creator_unique_unconsolidated(self):
        ic = InvoiceCreator("Member Invoice", dry_run=False)
        ic.add_line("Line One", 10.00)
        ic.create_and_send(self.addresses[0], comment="InvoiceCreator Test")
        self.assert_invoices(1, 10.00)

        ic2 = InvoiceCreator("Member Invoice", dry_run=False)
        ic2.add_line("Line One", 10.00)
        with self.assertRaises(InvoiceNotUnique):
            ic2.create_and_send(
                self.addresses[0], comment="InvoiceCreator Test", check_unique_unconsolidated=True
            )
        Invoice.objects.update(consolidated=True)
        ic2.create_and_send(
            self.addresses[0], comment="InvoiceCreator Test", check_unique_unconsolidated=True
        )
        self.assert_invoices(2, 2 * 10.00)

        ic3 = InvoiceCreator("Member Invoice", dry_run=False)
        ic3.add_line("Another Line One", 10.00)
        with self.assertRaises(InvoiceNotUnique):
            ic3.create_and_send(
                self.addresses[0],
                comment="InvoiceCreator Test",
                check_unique_unconsolidated=True,
                check_unique=True,
            )
        Invoice.objects.update(consolidated=True)
        ic3.create_and_send(
            self.addresses[0],
            comment="InvoiceCreator Test",
            check_unique_unconsolidated=True,
            check_unique=True,
        )
        self.assert_invoices(3, 3 * 10.00)

    def test_invoice_manual_payment(self):
        invoice = Invoice.objects.create(
            name="Test Invoice",
            person=self.addresses[0],
            invoice_type="Invoice",
            invoice_category=self.invoicecategories[0],
            date=datetime.date(2000, 1, 1),
            amount=Decimal("100"),
        )
        post_data = {
            "invoice": invoice.id,
            "date": "12.06.2025",
        }
        response = self.client.post("/geno/transaction_invoice/", post_data)
        self.assertEqual(response.status_code, 200)

        payments = Invoice.objects.filter(invoice_type="Payment")
        self.assertEqual(payments.count(), 1)
        payment = payments.first()
        self.assertEqual(payment.name, f"Zahlung Member Invoice {invoice.id}")
        self.assertEqual(payment.person, self.addresses[0])
        self.assertEqual(payment.invoice_category, self.invoicecategories[0])
        self.assertEqual(payment.date, datetime.date(2025, 6, 12))
        self.assertEqual(payment.amount, 100)
        self.assertNotEqual(payment.fin_transaction_ref, "")
        invoice.delete()
        payment.delete()

    def generate_camt053_data(self, invoices):
        template = loader.get_template("geno/camt053_demo_data.xml")
        context = {"payments": []}
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        comment = "Test Einzahlung"
        for invoice in invoices:
            date = invoice.date + datetime.timedelta(days=10)
            info = {}
            info["iban"] = settings.FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["iban"]
            info["refnr"] = get_reference_nr(
                invoice.invoice_category, invoice.person.id, invoice.id
            )
            info["transaction_id"] = f"TEST_{info['refnr']}_{ts}"
            info["date"] = date.strftime("%Y-%m-%d")
            info["comment"] = comment
            info["amount"] = format(invoice.amount, ".2f")
            info["debtor_name"] = str(invoice.person)
            context["payments"].append(info)
        return template.render(context)

    def test_invoice_camt_payments(self):
        invoice1 = Invoice.objects.create(
            name="Test Invoice1",
            person=self.addresses[0],
            invoice_type="Invoice",
            invoice_category=self.invoicecategories[0],
            date=datetime.date(2000, 1, 1),
            amount=Decimal("100"),
        )
        invoice2 = Invoice.objects.create(
            name="Test Invoice2",
            person=self.addresses[1],
            invoice_type="Invoice",
            invoice_category=self.invoicecategories[0],
            date=datetime.date(2000, 1, 2),
            amount=Decimal("99.95"),
        )

        if not settings.FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["iban"]:
            raise AssertionError(
                "FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]['iban'] must be set for this test."
            )
        if "account_iban" not in settings.FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]:
            raise AssertionError(
                "FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]['account_iban'] "
                "must be defined for this test."
            )

        camt053_data = self.generate_camt053_data([invoice1, invoice2])
        camt053_file = SimpleUploadedFile(
            "camt053_upload.xml", str.encode(camt053_data), content_type="application/xml"
        )
        response = self.client.post("/geno/transaction_upload/", {"file": camt053_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<b class="success">2 Buchungen wurden importiert:</b>', html=True
        )

        payments = Invoice.objects.filter(invoice_type="Payment").order_by("id")
        self.assertEqual(payments.count(), 2)
        self.assertEqual(payments[0].name, f"Einzahlung Member Invoice/{invoice1.id:010}")
        self.assertEqual(payments[0].person, self.addresses[0])
        self.assertEqual(payments[0].invoice_category, self.invoicecategories[0])
        self.assertEqual(payments[0].date, datetime.date(2000, 1, 11))
        self.assertEqual(payments[0].amount, 100)

        self.assertEqual(payments[1].name, f"Einzahlung Member Invoice/{invoice2.id:010}")
        self.assertEqual(payments[1].person, self.addresses[1])
        self.assertEqual(payments[1].invoice_category, self.invoicecategories[0])
        self.assertEqual(payments[1].date, datetime.date(2000, 1, 12))
        self.assertEqual(payments[1].amount, Decimal("99.95"))

        self.assertNotEqual(payments[0].fin_transaction_ref, "")
        self.assertNotEqual(payments[1].fin_transaction_ref, "")
        Invoice.objects.all().delete()


# Create two rental_objects
# Add both to a contract
# Create invoices for contract this_month-1
# remove rental_object from contract
# Create invoices for this_month
# Check invoices

# 2. Test invoice if rental_object is moved from contract to a new one with same (past) start_date
#   - with integrate bill in contract
#   - without integrate bill in contract

# 3. Test invoice switching from integrated bill to separate bills and vice-versa multiple times.
