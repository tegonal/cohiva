import datetime

from dateutil.relativedelta import relativedelta

import report.tests.data as testdata
from finance.accounting import Account, AccountKey
from geno.models import BankAccount, Invoice, InvoiceCategory
from geno.utils import nformat, unformat
from report.nk.generator import NkReportGenerator

from .base import NkReportTestCase


class NKBillTest(NkReportTestCase):
    ## Reference costs
    # Wohnung 001a
    unit1_simple = 20120.48
    unit1_internet = 204
    unit1_strom = 2148.47 - 983.59  # Total Strom (excluding Stromnebenkosten)
    unit1_total = unit1_simple + unit1_internet + unit1_strom

    # Wohnung 001b
    # Area of ru1 is 100m2 and ru2 20m2
    unit2_simple = unit1_simple / 100 * 20
    unit2_internet = 108
    unit2_strom = 426.33 - 196.72
    unit2_total = unit2_simple + unit2_internet + unit2_strom

    # Gewerbe G001
    unit3_simple = 47279.8  # 19699.95
    unit3_strom = 4296.93 - 1967.17
    unit3_internet = 0
    unit3_total = unit3_simple + unit3_internet + unit3_strom

    building_simple = 92700.41
    building_internet = 312
    building_strom = 8805.35 - 4032.70  # Total Strom (excluding Stromnebenkosten)
    building_total = building_simple + building_internet + building_strom
    # total_building = 221054.62

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

        akonto = 12 * 100
        bill_total = self.unit1_total - akonto
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
        self.assertEqual(context["generic_info"][0]["total"], nformat(self.unit1_total))
        self.assertEqual(context["generic_info"][1]["date"], "30.06.2024")
        self.assertEqual(context["generic_info"][1]["text"], "Abzüglich Akontozahlungen")
        self.assertEqual(context["generic_info"][1]["total"], nformat(-akonto))

        # Second contract with a negative invoice total
        akonto2 = 12 * 20 + 50000
        bill_total2 = self.unit2_total - akonto2
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
        bill_total3 = self.unit3_total * 5 / 12 - akonto3
        (ref_number, address, context, output_filename) = (
            mocks["create_qrbill"].call_args_list[2].args
        )
        self.assertAlmostEqual(
            unformat(context["s_generic_total"]),
            bill_total3,
            delta=0.0001 * abs(bill_total3),
        )
        self.assertEqual(
            context["extra_text"],
            "Ohne anderslautenden Gegenbericht in den nächsten 30 Tagen, werden wir das "
            f"Guthaben von CHF {nformat(-1 * unformat(context['s_generic_total']))} auf das bei "
            "uns registrierte Konto CH1234567890123456789 überweisen.",
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
        akonto = 12 * 100
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[0].args
        self.assertEqual(context["rental_unit"], "Wohnung 001a")
        self.assertEqual(context["building"], "Musterweg 1, 3000 Bern")
        self.assertEqual(context["billing_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["contract_period"], "01.07.2023 – 30.06.2024")
        # ZEV
        self._extended_rental_unit_zev_context_check(context)
        # Total
        self.assertEqual(context["s_chft"], nformat(self.building_total))
        self._extended_rental_unit_context_check(context)
        self.assertAlmostEqual(
            unformat(context["s_chf"]), self.unit1_total, delta=0.001 * abs(self.unit1_total)
        )
        self.assertEqual(context["akonto_chf"], nformat(akonto))
        self.assertEqual(context["akonto_chf"], nformat(akonto))  # Akonto paid
        self.assertEqual(
            context["diff_chf"], nformat(self.unit1_total - akonto)
        )  # Remaining amount to pay

        # Check the second contract with extra akonto payment
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[1].args
        self.assertEqual(context["rental_unit"], "Wohnung 001b")
        self.assertEqual(context["akonto_chf"], nformat(12 * 20 + 1000))  # Akonto paid
        self.assertEqual(
            context["s_chf"],
            nformat(self.unit2_total),
        )
        # ZEV: Check korrektur
        self.assertEqual(context["sk"], "-12")
        self.assertEqual(context["sk_chf"], "-3.36")

        # Check the third contract with a different billing period (only 5 months)
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[2].args
        self.assertEqual(context["rental_unit"], "Gewerbe G001")
        self.assertEqual(context["billing_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["contract_period"], "01.07.2023 – 30.11.2023")
        self.assertAlmostEqual(
            unformat(context["s_chf"]),
            self.unit3_total * 5 / 12,
            delta=0.0001 * abs(self.unit3_total) * 5 / 12,
        )
        self.assertEqual(context["akonto_chf"], "0.00")  # Akonto paid

        # TODO:
        #  - Test a rental unit with paid akonto / contract period
        #  - Test different paid and contact period for akonto
        #  - Test different billing period
        #  - Test contract with multiple rental units

    def test_rental_unit_bill_context_partial_period(self):
        """Test context variables used in nk_template_qrbill.odt with partial billing period"""
        self.configure_test_report_minimal()
        rg = NkReportGenerator(self.report, True, output_root="/tmp/")

        ## Make the first contract end inside the billing period
        self.contracts[0].billing_date_end = datetime.date(2023, 11, 30)
        self.contracts[0].save()
        partial_period_factor = 5 / 12

        ## Create akonto payments for the first two contracts
        for contract in self.contracts[0:2]:
            self.create_akonto_invoices(contract, rg.dates)

        mocks = self.generate_with_mock_output(rg)

        # Check the context for the first contract (extended check)
        akonto = 12 * 100
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[0].args
        self.assertEqual(context["rental_unit"], "Wohnung 001a")
        self.assertEqual(context["billing_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["contract_period"], "01.07.2023 – 30.11.2023")
        # ZEV
        self._extended_rental_unit_zev_context_check(context, partial_period_factor)
        # Total
        self.assertEqual(context["s_chft"], nformat(self.building_total))
        self._extended_rental_unit_context_check(context, partial_period_factor)
        self.assertAlmostEqual(
            unformat(context["s_chf"]),
            self.unit1_total * partial_period_factor,
            delta=0.0001 * abs(self.unit1_total),
        )
        self.assertEqual(context["akonto_chf"], nformat(akonto))
        self.assertEqual(context["akonto_chf"], nformat(akonto))  # Akonto paid
        self.assertAlmostEqual(
            unformat(context["diff_chf"]),
            self.unit1_total * partial_period_factor - akonto,
            delta=0.0001 * abs(self.unit1_total * partial_period_factor - akonto),
        )  # Remaining amount to pay

    def _extended_rental_unit_context_check(self, context, partial_period_factor: float = 1.0):
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
                8637.11,
                43875.95,
                13075.00,
                3858.60,
                8296.60,
                14957.15,
                86370.36,
                31915.00,
                self.building_strom,
                self.building_internet,
                4402.06,
            ],
            "pctt": [
                3.8,
                19.5,
                5.8,
                1.7,
                3.7,
                6.7,
                38.5,
                14.2,
                3.9,
                0.1,
                2.0,
            ],
            "share": [
                24.39,
                18.72,
                24.39,
                24.39,
                24.39,
                24.39,
                31.70,
                31.02,
                self.unit1_strom / self.building_strom * 100,
                65.38,
                27.15,
            ],
            "chf": [
                2106.61,
                8212.08,
                3189.02,
                941.12,
                2023.56,
                3648.09,
                27379.59,
                9898.67,
                self.unit1_strom,
                204.00,
                1195.02,
            ],
            "pct": [
                3.5,
                13.5,
                5.2,
                1.5,
                3.3,
                6.0,
                44.9,
                16.2,
                3.5,
                0.3,
                2.0,
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
                "Internet/WLAN",
                "Stromkosten",
            ):
                print(f"Skipping {context_i=}/{i=} {name} for now")
                continue
            ## Temp. disabled percentages until we have all the costs
            # for key in ("name", "chft", "pctt", "share", "chf", "pct"):
            for key in ("name", "chft", "share", "chf"):
                if key in ("chf", "share"):
                    expected_value = expected_costs[key][i] * partial_period_factor
                else:
                    expected_value = expected_costs[key][i]
                try:
                    if key in ("name",):
                        self.assertEqual(context["costs"][context_i][key], expected_value)
                    else:
                        self.assertAlmostEqual(
                            unformat(context["costs"][context_i][key]),
                            expected_value,
                            delta=0.005 * abs(expected_value),
                        )
                except AssertionError as e:
                    raise AssertionError(
                        f"Cost context at {context_i=}/{i=} for '{key}' is not '{expected_value}'"
                    ) from e
            context_i += 1
        # Make sure that there are not more costs than we have checked.
        self.assertEqual(context_i, len(context["costs"]))

    def _extended_rental_unit_zev_context_check(self, context, partial_period_factor: float = 1.0):
        # ZEV
        allg_ssd = 4 * 1000
        allg_snh = 6 * 1000
        expected = {
            "unit1": {
                "ssd": 400,  # Solar Eigenverbrauch kWh
                "ssd_chf": 58.12,  # Amount in CHF
                "snh": 600,  # Netztrombezug kWh Hochtarif
                "snh_chf": 180,
                "sk": 0,  # Korrektur kWh
                "sk_chf": 0,
                "st": 1200,  # Strombezug Total kWh
                "st_chf": 338.96,
                "sa_chf": 825.92,  # Anteil Allgemeinstrom
                "sa": 100,
                "stot_chf": 2148.47 - 983.59,  # Total Strom (excluding Stromnebenkosten)
            },
            "building": {
                "ssdt": 1640 + allg_ssd,  # Solar kWh building total
                "ssd_chft": 238.29 + allg_ssd * 0.1453,  # Solar CHF building total
                "snht": 2460 + allg_snh,  # Netztrombezug kWh Hochtarif
                "snh_chft": 2538,
                "skt": -24,  # Korrektur kWh
                "sk_chft": -6.72,
                "stt": 16896,  # Strombezug Total kWh
                "st_chft": 4772.65,
                "sa_chft": 3386.26,  # Anteil Allgemeinstrom
                "sat": 410,
                "sa_eh": 8.26,
                "stot_chft": 8805.35 - 4032.70,  # Total Strom (excluding Stromnebenkosten)
            },
        }  # Total Strom
        for key, value in expected["unit1"].items():
            try:
                self.assertAlmostEqual(
                    unformat(context[key]), value * partial_period_factor, delta=0.001 * abs(value)
                )
            except AssertionError as e:
                raise AssertionError(
                    f"Unit 1 context variable '{key}' is not '{value * partial_period_factor}'"
                ) from e
        for key, value in expected["building"].items():
            try:
                if key.endswith(("_chft", "_eh")):
                    self.assertEqual(context[key], nformat(value))
                else:
                    self.assertEqual(context[key], nformat(value, 0))
            except AssertionError as e:
                raise AssertionError(f"Building context variable '{key}' is not '{value}'") from e
