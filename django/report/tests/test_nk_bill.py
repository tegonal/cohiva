import datetime

from dateutil.relativedelta import relativedelta

import report.tests.data as testdata
from finance.accounting import Account, AccountKey
from geno.models import BankAccount, Invoice, InvoiceCategory
from geno.utils import nformat
from report.nk.generator import NkReportGenerator

from .base import NkReportTestCase


class NKBillTest(NkReportTestCase):
    # def setUpClass(cls):
    #    super().setUpClass()
    # def setUp(self):
    #    super().setUp()

    # @classmethod
    # def tearDownClass(cls):
    #    super().tearDownClass()

    # def tearDown(self):
    #    super().tearDown()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_nk_data(cls)

    @staticmethod
    def create_akonto_invoices(contract, dates):
        invoice_category = InvoiceCategory.objects.get(name="Mietzins wiederkehrend")
        akonto = 0
        for ru in contract.rental_units.all():
            akonto += ru.nk
        fiaccount = Account.from_settings(AccountKey.NK).set_code(contract=contract)
        for date in dates:
            Invoice.objects.create(
                invoice_type="Invoice",
                invoice_category=invoice_category,
                contract=contract,
                fin_account=fiaccount.code,
                amount=akonto,
                date=date["start"],
            )

    @staticmethod
    def create_special_akonto_invoice(contract, date, amount):
        invoice_category = InvoiceCategory.objects.get(name="Nebenkosten Akonto ausserordentlich")
        Invoice.objects.create(
            invoice_type="Invoice",
            invoice_category=invoice_category,
            contract=contract,
            amount=amount,
            date=date,
        )

    def test_contract_bill_context(self):
        """Test context variables used for the QR-Bill invoice (1st page of the billing document)"""
        self.configure_test_report_minimal()
        rg = NkReportGenerator(self.report, True, output_root="/tmp/")

        ## Create akonto payments for the first two contracts, with an extra payment for the second contract
        for contract in self.contracts[0:2]:
            self.create_akonto_invoices(contract, rg.dates)
        self.create_special_akonto_invoice(self.contracts[1], rg.dates[2]["end"], 50000)

        ## Make the third contract end inside the billing period
        self.contracts[2].billing_date_end = datetime.date(2023, 11, 30)
        self.contracts[2].bankaccount = BankAccount.objects.create(iban="CH1234567890123456789")
        self.contracts[2].save()
        self.create_special_akonto_invoice(self.contracts[2], rg.dates[2]["end"], 50000)

        mocks = self.generate_with_mock_output(rg)
        self.assertEqual(mocks["create_qrbill"].call_count, len(rg.contracts))

        ## First contract
        total_unit = 20120.48  # Temporary: not all costs included yet
        akonto = 12 * 100
        bill_total = total_unit - akonto
        (ref_number, address, context, output_filename) = (
            mocks["create_qrbill"].call_args_list[0].args
        )
        self.assertEqual(context["betreff"], "Nebenkostenabrechnung 01.07.2023 – 30.06.2024")
        self.assertEqual(context["building"], "Musterweg 1, 3000 Bern")
        self.assertEqual(context["contract_info"], self.contracts[0].get_contract_label())
        self.assertEqual(context["invoice_nr"], 9999999999)
        self.assertEqual(context["invoice_date"], datetime.date.today().strftime("%d.%m.%Y"))
        self.assertEqual(
            context["invoice_duedate"],
            (datetime.date.today() + relativedelta(months=2)).strftime("%d.%m.%Y"),
        )
        self.assertEqual(context["s_generic_total"], nformat(bill_total))
        self.assertNotIn("extra_text", context)

        self.assertEqual(context["sect_rent"], False)
        self.assertEqual(context["sect_generic"], True)

        self.assertEqual(context["generic_info"][0]["date"], "30.06.2024")
        self.assertEqual(context["generic_info"][0]["text"], "Nebenkosten Wohnung 001a")
        self.assertEqual(context["generic_info"][0]["total"], nformat(total_unit))
        self.assertEqual(context["generic_info"][1]["date"], "30.06.2024")
        self.assertEqual(context["generic_info"][1]["text"], "Abzüglich Akontozahlungen")
        self.assertEqual(context["generic_info"][1]["total"], nformat(-akonto))

        # Second contract with a negative invoice total
        akonto2 = 12 * 20 + 50000
        bill_total2 = total_unit / 100 * 20 - akonto2
        (ref_number, address, context, output_filename) = (
            mocks["create_qrbill"].call_args_list[1].args
        )
        self.assertEqual(
            # Area of ru1 is 100m2 and ru2 20m2
            context["s_generic_total"],
            nformat(bill_total2),
        )
        self.assertEqual(
            context["extra_text"],
            "Wir bitten Sie, uns die Kontoangaben für die Rückerstattung "
            f"des Guthabens von CHF {nformat(-1 * bill_total2)} in den nächsten 30 Tagen "
            "mitzuteilen (am liebsten per Email an info@cohiva.ch). Vielen Dank!",
        )

        # Third contract with a negative invoice total and bank account
        akonto3 = 50000
        total_unit3 = 19699.95  # Temporary: not all costs included yet
        bill_total3 = total_unit3 - akonto3
        (ref_number, address, context, output_filename) = (
            mocks["create_qrbill"].call_args_list[2].args
        )
        self.assertEqual(
            context["s_generic_total"],
            nformat(bill_total3),
        )
        self.assertEqual(
            context["extra_text"],
            "Ohne anderslautenden Gegenbericht in den nächsten 30 Tagen, "
            f"werden wir das Guthaben von CHF {nformat(-1 * bill_total3)} auf das bei uns "
            "registrierte Konto CH1234567890123456789 überweisen.",
        )

    def test_rental_unit_bill_context(self):
        """Test context variables used in nk_template_qrbill.odt (2nd and following pages of the billing document)"""
        self.configure_test_report_minimal()
        rg = NkReportGenerator(self.report, True, output_root="/tmp/")

        ## Create akonto payments for the first two contracts, with an extra payment for the second contract
        for contract in self.contracts[0:2]:
            self.create_akonto_invoices(contract, rg.dates)
        self.create_special_akonto_invoice(self.contracts[1], rg.dates[2]["end"], 1000)

        ## Make the third contract end inside the billing period
        self.contracts[2].billing_date_end = datetime.date(2023, 11, 30)
        self.contracts[2].save()

        mocks = self.generate_with_mock_output(rg)
        self.assertEqual(mocks["create_final_pdf"].call_count, len(rg.contracts))
        self.assertEqual(mocks["add_output_to_report"].call_count, 1)

        # Check the context for the first contract (extended check)
        # total_building = 221054.62
        total_building = 92700.41  # Temporary: not all costs included yet
        # total_unit = 54810.38
        total_unit = 20120.48  # Temporary: not all costs included yet
        akonto = 12 * 100
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[0].args
        self.assertEqual(context["rental_unit"], "Wohnung 001a")
        self.assertEqual(context["building"], "Musterweg 1, 3000 Bern")
        self.assertEqual(context["billing_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["contract_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["s_chft"], nformat(total_building))
        self._extended_rental_unit_context_check(context)
        self.assertEqual(context["s_chf"], nformat(total_unit))
        self.assertEqual(context["akonto_chf"], nformat(akonto))  # Akonto paid
        self.assertEqual(
            context["diff_chf"], nformat(total_unit - akonto)
        )  # Remaining amount to pay

        # Check the second contract with extra akonto payment
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[1].args
        self.assertEqual(context["rental_unit"], "Wohnung 001b")
        self.assertEqual(context["akonto_chf"], nformat(12 * 20 + 1000))  # Akonto paid
        self.assertEqual(
            # Area of ru1 is 100m2 and ru2 20m2
            context["s_chf"],
            nformat(total_unit / 100 * 20),
        )

        # Check the third contract with a different billing period (only 5 months)
        total_unit3 = 19699.95  # Temporary: not all costs included yet
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[2].args
        self.assertEqual(context["rental_unit"], "Gewerbe G001")
        self.assertEqual(context["billing_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["contract_period"], "01.07.2023 – 30.11.2023")
        self.assertEqual(context["s_chf"], nformat(total_unit3))
        self.assertEqual(context["akonto_chf"], "0.00")  # Akonto paid

        # TODO:
        #  - Test a rental unit with paid akonto / contract period
        #  - Test different paid and contact period for akonto
        #  - Test different billing period
        #  - Test contract with multiple rental units

    def _extended_rental_unit_context_check(self, context):
        expected_costs = {
            "name": [
                "Hauswartung, Service Heizung/Lüftung",
                "Reinigung",
                "Siedlung/Umgebungspflege",
                "Betriebskosten Gemeinschaftsanlagen",
                "Lift",
                "Kehrichtgebühren",
                "Wärmekosten",
                "Wasserkosten",
                "Stromkosten",
                "Internet/WLAN",
                "Verwaltungsaufwand 2.0",
            ],
            "chft": [
                "8'637.11",
                "43'875.95",
                "13'075.00",
                "3'858.60",
                "8'296.60",
                "14'957.15",
                "86'370.36",
                "31'915.00",
                "5'422.44",
                "312.00",
                "4'334.40",
            ],
            "pctt": [
                "3.9",
                "19.8",
                "5.9",
                "1.7",
                "3.8",
                "6.8",
                "39.1",
                "14.4",
                "2.5",
                "0.1",
                "2.0",
            ],
            "share": [
                "24.39%",
                "18.72%",
                "24.39%",
                "24.39%",
                "24.39%",
                "24.39%",
                "28.14%",
                "24.39%",
                "24.39%",
                "65.38%",
                "24.79%",
            ],
            "chf": [
                "2'106.61",
                "8'212.08",
                "3'189.02",
                "941.12",
                "2'023.56",
                "3'648.09",
                "24'304.49",
                "7'784.15",
                "1'322.55",
                "204.00",
                "1'074.71",
            ],
            "pct": [
                "3.8",
                "15.0",
                "5.8",
                "941.12",
                "1.7",
                "3.7",
                "6.7",
                "44.3",
                "14.2",
                "2.4",
                "0.4",
                "2.0",
            ],
        }
        context_i = 0
        for i, name in enumerate(expected_costs["name"]):
            # Skip unsupported costs for now
            if name not in (
                "Hauswartung, Service Heizung/Lüftung",
                "Reinigung",
                "Siedlung/Umgebungspflege",
                "Betriebskosten Gemeinschaftsanlagen",
                "Lift",
                "Kehrichtgebühren",
            ):
                print(f"Skipping {context_i=}/{i=} {name} for now")
                continue
            ## Temp. disabled percentages unil we have all the costs
            # for key in ("name", "chft", "pctt", "share", "chf", "pct"):
            for key in ("name", "chft", "share", "chf"):
                try:
                    self.assertEqual(context["costs"][context_i][key], expected_costs[key][i])
                except AssertionError:
                    print(f"Assertion failed at {context_i=}/{i=} for '{key}':")
                    raise
            context_i += 1
        # Make sure that there are not more costs than we have checked.
        self.assertEqual(context_i, len(context["costs"]))
