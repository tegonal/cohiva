import datetime
from unittest.mock import patch

from django.http import FileResponse
from rest_framework.test import APIRequestFactory

import geno.tests.data as geno_testdata
from finance.accounting import Account, AccountingManager, AccountKey
from geno.api_views import Akonto, QRBill
from geno.billing import get_income_account, get_receivables_account
from geno.models import Contract, Invoice, InvoiceCategory

from .base import GenoAdminTestCase


class AkontoViewTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)

    def setUp(self):
        self.view = Akonto()
        self.view.billing_period_start = datetime.datetime(2020, 7, 1)
        self.view.billing_period_end = datetime.datetime(2021, 6, 30)
        self.view.invoice_category_nk_ausserordentlich = InvoiceCategory.objects.get(
            name="Nebenkosten Akonto ausserordentlich"
        )
        self.invoice_cat_rent = InvoiceCategory.objects.get(name="Mietzins wiederkehrend")

    def create_akonto_invoices(self, contract):
        fiaccount = Account.from_settings(AccountKey.NK).set_code(contract=contract)
        Invoice.objects.create(
            name="NK akonto test 1",
            amount=100,
            contract=contract,
            invoice_category=self.invoice_cat_rent,
            fin_account=fiaccount.code,
            date=datetime.date(2020, 8, 1),
        )
        Invoice.objects.create(
            name="NK akonto test 2",
            amount=200,
            contract=contract,
            invoice_category=self.invoice_cat_rent,
            fin_account=fiaccount.code,
            date=datetime.date(2020, 9, 1),
        )
        Invoice.objects.create(
            name="NK akonto ausserordentlich 1",
            amount=25,
            contract=contract,
            invoice_category=self.view.invoice_category_nk_ausserordentlich,
            invoice_type="Invoice",
            date=datetime.date(2020, 10, 15),
        )
        Invoice.objects.create(
            name="NK akonto ausserordentlich 2",
            amount=50,
            contract=contract,
            invoice_category=self.view.invoice_category_nk_ausserordentlich,
            invoice_type="Invoice",
            date=datetime.date(2020, 11, 15),
        )

    def create_billing_contract_and_invoices(self, contract):
        fiaccount = Account.from_settings(AccountKey.NK).set_code(contract=contract)
        billing_contract = Contract.objects.create(
            state="unterzeichnet",
            date=datetime.date(2020, 1, 1),
            billing_contract=contract,
        )
        billing_contract.rental_units.set([self.rentalunits[3]])
        billing_contract.contractors.set(self.addresses[0:2])
        billing_contract.save()
        Invoice.objects.create(
            name="NK akonto billing contract",
            amount=1000,
            contract=billing_contract,
            invoice_category=self.invoice_cat_rent,
            fin_account=fiaccount.code,
            date=datetime.date(2021, 1, 1),
        )
        Invoice.objects.create(
            name="NK akonto ausserordentlich billing contract",
            amount=1,
            contract=billing_contract,
            invoice_category=self.view.invoice_category_nk_ausserordentlich,
            invoice_type="Invoice",
            date=datetime.date(2021, 6, 1),
        )

    def test_get_akonto_for_contract(self):
        contract = self.contracts[0]
        self.view.contract_id = contract.id
        self.assertEqual(self.view.get_akonto_for_contract(), 0)

        self.create_akonto_invoices(contract)
        self.assertEqual(self.view.get_akonto_for_contract(), 100 + 200 + 25 + 50)

        self.view.contract_id = -1
        self.assertEqual(self.view.get_akonto_for_contract(), 0)

    def test_get_akonto_for_contract_date_ranges(self):
        contract = self.contracts[0]
        self.view.contract_id = contract.id
        self.create_akonto_invoices(contract)

        self.view.billing_period_start = datetime.datetime(2020, 7, 1)
        self.view.billing_period_end = datetime.datetime(2020, 9, 30)
        self.assertEqual(self.view.get_akonto_for_contract(), 100 + 200)

        self.view.billing_period_start = datetime.datetime(2020, 9, 1)
        self.view.billing_period_end = datetime.datetime(2021, 6, 30)
        self.assertEqual(self.view.get_akonto_for_contract(), 200 + 25 + 50)

    def test_get_akonto_for_contract_with_billing_contract(self):
        contract = self.contracts[0]
        self.view.contract_id = contract.id
        self.create_billing_contract_and_invoices(contract)
        self.assertEqual(self.view.get_akonto_for_contract(), 1000 + 1)

        self.create_akonto_invoices(contract)
        self.assertEqual(self.view.get_akonto_for_contract(), 100 + 200 + 25 + 50 + 1000 + 1)

    def test_get_akonto_for_all_contracts(self):
        self.assertEqual(self.view.get_akonto_for_all_contracts(), {})

        contract = self.contracts[0]
        self.create_akonto_invoices(contract)
        self.assertEqual(
            self.view.get_akonto_for_all_contracts(), {contract.id: 100 + 200 + 25 + 50}
        )
        self.create_billing_contract_and_invoices(contract)
        self.assertEqual(
            self.view.get_akonto_for_all_contracts(), {contract.id: 100 + 200 + 25 + 50 + 1000 + 1}
        )

        contract2 = Contract.objects.create(
            state="unterzeichnet",
            date=datetime.date(2020, 1, 1),
        )
        contract2.rental_units.set([self.rentalunits[4]])
        contract2.contractors.set([self.addresses[4]])
        contract2.save()
        self.create_akonto_invoices(contract2)
        fiaccount = Account.from_settings(AccountKey.NK).set_code(contract=contract2)
        Invoice.objects.create(
            name="NK akonto with postfix",
            amount=2000,
            contract=contract2,
            invoice_category=self.invoice_cat_rent,
            fin_account=fiaccount.code + "0099",
            date=datetime.date(2021, 2, 1),
        )
        self.assertEqual(
            self.view.get_akonto_for_all_contracts(),
            {
                contract.id: 100 + 200 + 25 + 50 + 1000 + 1,
                contract2.id: 100 + 200 + 25 + 50 + 2000,
            },
        )


class QRBillAPIViewTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = QRBill()
        self.view.contract = self.contracts[0]
        self.view.address = self.view.contract.get_contact_address()
        self.view.context = self.view.address.get_context()
        self.view.dry_run = False
        self.view.invoice_category = InvoiceCategory.objects.get(
            reference_id=12
        )  # Nebenkostenabrechnung
        self.view.invoice_date = datetime.date(2021, 10, 10)
        self.fiaccount_nk_receivables = Account.from_settings(AccountKey.NK_RECEIVABLES).set_code(
            contract=self.view.contract
        )
        self.fiaccount_nk = Account.from_settings(AccountKey.NK).set_code(
            contract=self.view.contract
        )

    def test_get_virtual_contract_account(self):
        with self.assertRaises(KeyError):
            self.view.get_virtual_contract_account(1)
        self.assertEqual(
            self.view.get_virtual_contract_account(-1),
            Account.from_settings(AccountKey.NK_VIRTUAL_1).set_code(self.view.contract),
        )
        self.assertEqual(
            self.view.get_virtual_contract_account(-3),
            Account.from_settings(AccountKey.NK_VIRTUAL_3).set_code(self.view.contract),
        )

    def build_request(self, modified_data=None):
        data = {
            "contract_id": self.view.contract.id if self.view.contract else 0,
            "billing_period_end": "2021-06-30",
            "total_akonto": 0,
            "total_amount": 100,
            "comment": "QRBill test",
            "bill_lines": [],
        }
        if modified_data is not None:
            data.update(modified_data)
        request = self.factory.post("/geno/qrbill/", data, content_type="application/json")
        return self.view.initialize_request(request)

    def test_do_accounting_without_akonto(self):
        request = self.build_request()
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            self.view.do_accounting(request, book)
            self.assertEqual(len(book._db), 1)

            created_invoice = Invoice.objects.get(id=self.view.invoice_id)
            self.assertEqual(created_invoice.amount, 100)
            self.assertTrue(created_invoice.fin_transaction_ref.startswith("dum_"))
            self.assertEqual(
                created_invoice.fin_account,
                get_income_account(self.view.invoice_category, None, self.view.contract).code,
            )
            self.assertEqual(
                created_invoice.fin_account_receivables,
                get_receivables_account(self.view.invoice_category, self.view.contract).code,
            )
            self.assertEqual(created_invoice.invoice_type, "Invoice")
            self.assertEqual(created_invoice.invoice_category, self.view.invoice_category)
            self.assertEqual(created_invoice.name, "Nebenkostenabrechnung")
            self.assertEqual(created_invoice.contract, self.view.contract)
            self.assertEqual(created_invoice.date, datetime.date(2021, 10, 10))

    def test_do_accounting_with_akonto(self):
        request = self.build_request({"total_akonto": 50})
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            self.view.do_accounting(request, book)
            self.assertEqual(len(book._db), 2)

            created_invoice = Invoice.objects.get(id=self.view.invoice_id)
            self.assertEqual(created_invoice.amount, 100)

            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            for split in tr.splits:
                if split.amount == -50:
                    self.assertEqual(split.account, self.fiaccount_nk_receivables)
                elif split.amount == 50:
                    self.assertEqual(split.account, self.fiaccount_nk)
                else:
                    raise ValueError("Amount should be 50")
            self.assertEqual(tr.date, datetime.date(2021, 6, 30))
            self.assertEqual(
                tr.description, f"NK-Abrechnung Verrechnung Akontozahlungen {self.view.contract}"
            )

    def test_do_accounting_virtual_contract(self):
        self.view.contract = None
        request = self.build_request({"contract_id": -1})
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            self.view.do_accounting(request, book)
            self.assertEqual(len(book._db), 1)
            self.assertEqual(self.view.invoice_id, None)
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            for split in tr.splits:
                if split.amount == -100:
                    self.assertEqual(split.account, self.fiaccount_nk_receivables)
                elif split.amount == 100:
                    self.assertEqual(split.account, self.view.get_virtual_contract_account(-1))
                else:
                    raise ValueError("Amount should be 100")
            self.assertEqual(tr.date, datetime.date(2021, 6, 30))

    @patch("geno.api_views.QRBill.do_accounting")
    def test_post_dry_run(self, mock_do_accounting):
        test_view = QRBill()
        ret = test_view.post(self.build_request())
        self.assertEqual(test_view.dry_run, True)
        mock_do_accounting.assert_called_once()
        self.assertTrue(isinstance(ret, FileResponse))
        ret.file_to_stream.close()

        ret = test_view.post(self.build_request({"dry_run": False}))
        self.assertEqual(test_view.dry_run, False)
        self.assertEqual(mock_do_accounting.call_count, 2)
        self.assertTrue(isinstance(ret, FileResponse))
        ret.file_to_stream.close()

    def test_get_qrbill_virtual_contract_file_name(self):
        self.view.contract = None
        ret = self.view.get_qrbill(self.build_request({"contract_id": -1}))
        self.assertEqual(ret.filename, "NK_Gästezimmer_20211010.pdf")
        self.assertEqual(self.view.context["contract_info"], "Gästezimmer")
        self.assertTrue(isinstance(ret, FileResponse))
        ret.file_to_stream.close()
