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
    unit1_stromnk = 983.59
    unit1_strom = 2149.28 - unit1_stromnk  # Total Strom (excluding Stromnebenkosten)
    unit1_stromnk_factor = unit1_stromnk / (unit1_strom + unit1_stromnk)
    unit1_waerme = 28067.88
    unit1_wasser = 10119.50
    unit1_total_costs = (
        unit1_simple + unit1_internet + unit1_strom + unit1_waerme + unit1_wasser + unit1_stromnk
    )
    unit1_fee = 0.02 * unit1_total_costs
    unit1_total = unit1_total_costs + unit1_fee

    # Wohnung 001b
    # Area of ru1 is 100m2 and ru2 20m2
    unit2_simple = unit1_simple / 100 * 20
    unit2_internet = 108
    unit2_stromnk = 196.72
    unit2_strom = 426.50 - unit2_stromnk
    unit2_waerme = 5613.58
    unit2_wasser = 2023.90
    unit2_total_costs = (
        unit2_simple + unit2_internet + unit2_strom + unit2_waerme + unit2_wasser + unit2_stromnk
    )
    unit2_fee = 0.02 * unit2_total_costs
    unit2_total = unit2_total_costs + unit2_fee

    # Gewerbe G001
    unit3_simple = 47279.8
    unit3_internet = 0
    unit3_stromnk = 1967.17
    unit3_strom = 4298.57 - unit3_stromnk  # 4296.93 - unit3_stromnk
    unit3_waerme = 40509.06
    unit3_wasser = 14085.43
    unit3_total_costs = (
        unit3_simple + unit3_internet + unit3_strom + unit3_waerme + unit3_wasser + unit3_stromnk
    )
    unit3_fee = 0.02 * unit3_total_costs
    unit3_total = unit3_total_costs + unit3_fee

    building_simple = 92700.41
    building_internet = 312
    building_stromnk = 4032.70
    building_strom_korrektur = 6.72
    building_strom_korrektur_mistake_in_reference_calculation = 3.35
    building_strom = (
        8673.12 - building_strom_korrektur_mistake_in_reference_calculation - building_stromnk
    )  # Total Strom (excluding Stromnebenkosten)
    building_stromnk_factor = building_stromnk / (building_strom + building_stromnk)
    building_waerme = 86370.36
    building_wasser = 31915
    building_total_costs = (
        building_simple
        + building_internet
        + building_strom
        + building_waerme
        + building_wasser
        + building_stromnk
    )
    building_fee = 0.02 * building_total_costs
    building_total = building_total_costs + building_fee
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

    def test_totals_match_reference_values(self):
        """Transitional test to make sure the new implementation reproduces the results from
        the previous implementation."""
        self.assertAlmostEqual(self.unit1_total, 61874.35, delta=1.0)
        self.assertAlmostEqual(self.unit2_total, 12439.99, delta=1.0)
        self.assertAlmostEqual(self.unit3_total, 108296.40, delta=1.0)
        self.assertAlmostEqual(
            self.building_total,
            224370.31 - self.building_strom_korrektur_mistake_in_reference_calculation,
            delta=1.0,
        )

    def test_contract_bill_context(self):
        """Test context variables used for the QR-Bill invoice (1st page of the billing document)"""
        self.configure_test_report_wb_reference()
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
        self.assertAlmostEqual(
            unformat(context["s_generic_total"]), bill_total, delta=0.0001 * bill_total
        )
        self.assertNotIn("extra_text", context)

        self.assertEqual(context["sect_rent"], False)
        self.assertEqual(context["sect_generic"], True)

        self.assertEqual(context["generic_info"][0]["date"], "30.06.2024")
        self.assertEqual(context["generic_info"][0]["text"], "Nebenkosten Wohnung 001a")
        self.assertAlmostEqual(
            unformat(context["generic_info"][0]["total"]),
            self.unit1_total,
            delta=0.0001 * self.unit1_total,
        )
        self.assertEqual(context["generic_info"][1]["date"], "30.06.2024")
        self.assertEqual(context["generic_info"][1]["text"], "Abzüglich Akontozahlungen")
        self.assertEqual(context["generic_info"][1]["total"], nformat(-akonto))

        # Second contract with a negative invoice total
        akonto2 = 12 * 20 + 50000
        bill_total2 = self.unit2_total - akonto2
        (ref_number, address, context, output_filename) = (
            mocks["create_qrbill"].call_args_list[1].args
        )
        self.assertAlmostEqual(
            # Area of ru1 is 100m2 and ru2 20m2
            unformat(context["s_generic_total"]),
            bill_total2,
            delta=0.00001 * abs(bill_total2),
        )
        self.assertEqual(
            context["extra_text"],
            "Wir bitten Sie, uns die Kontoangaben für die Rückerstattung "
            f"des Guthabens von CHF {nformat(-1 * unformat(context['s_generic_total']))} in den "
            "nächsten 30 Tagen "
            "mitzuteilen (am liebsten per Email an info@cohiva.ch). Vielen Dank!",
        )

        # Third contract with a negative invoice total and bank account
        (ref_number, address, context, output_filename) = (
            mocks["create_qrbill"].call_args_list[2].args
        )
        self.assertEqual(
            context["extra_text"],
            "Ohne anderslautenden Gegenbericht in den nächsten 30 Tagen, werden wir das "
            f"Guthaben von CHF {nformat(-1 * unformat(context['s_generic_total']))} auf das bei "
            "uns registrierte Konto CH1234567890123456789 überweisen.",
        )

    def test_rental_unit_bill_context(self):
        """Test context variables used in nk_template_qrbill.odt (2nd and following pages of the billing document)"""
        self.configure_test_report_wb_reference()
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
        # Extended checks for ZEV, VEWA...
        self._extended_rental_unit_zev_context_check(context)
        self._extended_rental_unit_vewa_context_check(context)
        # Total
        self.assertAlmostEqual(unformat(context["s_chft"]), self.building_total, delta=0.05)
        self._extended_rental_unit_context_check(context)
        self.assertAlmostEqual(
            unformat(context["s_chf"]), self.unit1_total, delta=0.001 * abs(self.unit1_total)
        )
        self.assertEqual(context["akonto_chf"], nformat(akonto))
        self.assertEqual(context["akonto_chf"], nformat(akonto))  # Akonto paid
        self.assertAlmostEqual(
            unformat(context["diff_chf"]),
            self.unit1_total - akonto,
            delta=0.001 * abs(self.unit1_total),
        )  # Remaining amount to pay

        # Check the second contract with extra akonto payment
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[1].args
        self.assertEqual(context["rental_unit"], "Wohnung 001b")
        self.assertEqual(context["akonto_chf"], nformat(12 * 20 + 1000))  # Akonto paid
        self.assertAlmostEqual(
            unformat(context["s_chf"]),
            self.unit2_total,
            delta=0.001 * abs(self.unit2_total),
        )
        # ZEV: Check korrektur
        self.assertEqual(context["sk"], "-12")
        self.assertEqual(context["sk_chf"], "-3.36")

        # Check the third contract with a different billing period (only 5 months)
        (context, ru) = mocks["create_rental_unit_files"].call_args_list[2].args
        self.assertEqual(context["rental_unit"], "Gewerbe G001")
        self.assertEqual(context["billing_period"], "01.07.2023 – 30.06.2024")
        self.assertEqual(context["contract_period"], "01.07.2023 – 30.11.2023")
        ## Allow for a big delta, since the scaling is not linear!
        self.assertAlmostEqual(
            unformat(context["s_chf"]),
            self.unit3_total * 5 / 12,
            delta=0.1 * abs(self.unit3_total),
        )
        self.assertEqual(context["akonto_chf"], "0.00")  # Akonto paid

        # TODO:
        #  - Test a rental unit with paid akonto / contract period
        #  - Test different paid and contact period for akonto
        #  - Test different billing period
        #  - Test contract with multiple rental units

    def test_rental_unit_bill_context_partial_period(self):
        """Test context variables used in nk_template_qrbill.odt with partial billing period"""
        self.configure_test_report_wb_reference()
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
        # Extended checks for ZEV, VEWA...
        self._extended_rental_unit_zev_context_check(context, partial_period_factor)
        self._extended_rental_unit_vewa_context_check(context, partial_period_factor)
        # Total
        self.assertAlmostEqual(
            unformat(context["s_chft"]),
            self.building_total,
            delta=0.001 * abs(self.building_total),
        )
        self._extended_rental_unit_context_check(context, partial_period_factor)
        self.assertAlmostEqual(
            unformat(context["s_chf"]),
            self.unit1_total * partial_period_factor,
            delta=0.1 * abs(self.unit1_total),
        )
        self.assertEqual(context["akonto_chf"], nformat(akonto))
        self.assertEqual(context["akonto_chf"], nformat(akonto))  # Akonto paid
        self.assertAlmostEqual(
            unformat(context["diff_chf"]),
            self.unit1_total * partial_period_factor - akonto,
            delta=0.3 * abs(self.unit1_total * partial_period_factor - akonto),
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
                "Serviceabo Energiemessung",
                "Internet/WLAN",
                "Verwaltungsaufwand",
            ],
            "chft": [
                8637.11,
                43875.95,
                13075.00,
                3858.60,
                8296.60,
                14957.15,
                self.building_waerme,  # 86370.36,
                self.building_wasser,  # 31915.00,
                self.building_strom,
                self.building_stromnk,
                self.building_internet,
                self.building_fee,  # 4402.06,
            ],
            "pctt": [
                3.8,
                19.6,
                5.8,
                1.7,
                3.7,
                6.7,
                38.5,
                14.2,
                (1 - self.building_stromnk_factor) * 3.9,
                self.building_stromnk_factor * 3.9,
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
                32.50,  # self.unit1_waerme / self.building_waerme * 100, #31.70,
                31.71,
                self.unit1_strom / self.building_strom * 100,
                24.39,
                65.38,
                self.unit1_fee / self.building_fee * 100,
            ],
            "chf": [
                2106.61,
                8212.08,
                3189.02,
                941.12,
                2023.56,
                3648.09,
                self.unit1_waerme,  # 27379.59,
                10119.50,
                self.unit1_strom,
                self.unit1_stromnk,
                204.00,
                self.unit1_fee,  # 1195.02,
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
                (1 - self.unit1_stromnk_factor) * 3.5,
                self.unit1_stromnk_factor * 3.5,
                0.3,
                2.0,
            ],
        }
        context_i = 0
        total = {}
        for i, name in enumerate(expected_costs["name"]):
            for key in ("name", "chft", "pctt", "share", "chf", "pct"):
                expected_delta = 0
                if key in ("chf", "share"):
                    expected_value = expected_costs[key][i] * partial_period_factor
                    if name in ("Wärmekosten", "Wasserkosten"):
                        # Allow for a bigger delta, since scaling is not linear
                        expected_delta = 0.5 * abs(expected_value)
                    else:
                        expected_delta = 0.005 * abs(expected_value)
                else:
                    expected_value = expected_costs[key][i]
                    if key in ("pct", "pctt"):
                        expected_delta = 0.9
                    elif key != "name":
                        expected_delta = 0.005 * abs(expected_value)
                try:
                    if key in ("name",):
                        self.assertEqual(context["costs"][context_i][key], expected_value)
                    else:
                        value = unformat(context["costs"][context_i][key])
                        if key not in total:
                            total[key] = 0.0
                        total[key] += value
                        if partial_period_factor == 1.0 or key not in ("pct", "pctt"):
                            # We don't check percentage values for partial periods
                            self.assertAlmostEqual(value, expected_value, delta=expected_delta)
                except AssertionError as e:
                    raise AssertionError(
                        f"Cost context at {context_i=}/{i=} for '{key}' is not '{expected_value}'"
                    ) from e
            context_i += 1
        # Make sure that there are not more costs than we have checked.
        self.assertEqual(context_i, len(context["costs"]))
        # Make sure percentages add up to 100%
        self.assertAlmostEqual(total["pct"], 100.0, delta=0.5)
        self.assertAlmostEqual(total["pctt"], 100.0, delta=0.5)

    def _extended_rental_unit_zev_context_check(self, context, partial_period_factor: float = 1.0):
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
                "ssdt": 1480 + allg_ssd,  # Solar kWh building total
                "ssd_chft": 215.04 + allg_ssd * 0.1453,  # Solar CHF building total
                "snht": 2220 + allg_snh,  # Netztrombezug kWh Hochtarif
                "snh_chft": 2466,
                "sntt": 2740,  # Netztrombezug kWh Niedertarif
                "snt_chft": 767.20,
                "skt": -24,  # Korrektur kWh
                "sk_chft": -1 * self.building_strom_korrektur,
                "stt": 16896 - 480,  # Strombezug Total kWh
                "shk_chft": 620.99,
                "st_chft": 4643.78 - self.building_strom_korrektur,
                "sa_chft": 3386.26,  # Anteil Allgemeinstrom
                "sat": 410,
                "sa_eh": 8.26,
                "stot_chft": 8676.48 - self.building_strom_korrektur - self.building_stromnk,
            },
        }
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

    def _extended_rental_unit_vewa_context_check(
        self, context, partial_period_factor: float = 1.0
    ):
        expected = {
            "unit1": {
                # Wasser/Abwasser
                "wag": 100,  # m2 (ru area)
                "wag_chf": 2335.24,
                "wav": 590.4,  # m3 (measured warm water amount, scaled to total cold water use)
                "wav_chf": 1630.69,
                "wat_chf": 3965.94,
                "waa": 100,  # m2 (ru area)
                "waa_chf": 6153.56,
                "swa_chf": 10119.5,
                # Warmwasser
                "wwg": 100,  # m2 (ru area)
                "wwg_chf": 3763.23,
                "wwv": 40,  # m3 (measured amount)
                "wwv_chf": 2371.48,
                "wwbt_chf": 6134.71,
                "wwa": 100,  # m2 (ru area)
                "wwa_chf": 8948.98,
                "wwt_chf": 15083.69,
                # Heizung
                "hfg": 300,  # m3 (ru volume)
                "hfg_chf": 3368.69,
                "hfv": 700,  # kWh (measured energy)
                "hfv_chf": 7860.27,
                "hr": 3,  # m3 (ru volume, scaled by section weight)
                "hr_chf": 30.77,
                "hl": 105,  # m3 (ru volume, scaled by section weight)
                "hl_chf": 1724.57,
                "ht_chf": 12984.20,
                # Total Wärme
                "sw_chf": 28067.88,
            },
            "building": {
                # Wasser/Abwasser
                "wagt": 410,
                "wag_chft": 9574.5,
                "wavt": 8088,
                "wav_chft": 22340.5,
                "wat_chft": 31915,
                "waat": 265,
                "waa_chft": 16306.93,
                "swa_chft": 31915,
                "wag_eh": 23.35,
                "wav_eh": 2.76,
                "waa_eh": 61.54,
                # Warmwasser
                "wwgt": 370,  # m2
                "wwg_chft": 13923.97,
                "wwvt": 548,  # m3
                "wwv_chft": 32489.25,
                "wwbt_chft": 46413.22,
                "wwat": 265,  # m2
                "wwg_eh": 37.63,
                "wwv_eh": 59.29,
                "wwa_eh": 89.49,
                # Heizung
                "hfgt": 360,  # m3
                "hfg_chft": 4042.42,
                "hfvt": 840,  # kWh
                "hfv_chft": 9432.32,
                "hrt": 1254,  # m3
                "hr_chft": 12859.07,
                "hlt": 830,  # m3
                "hl_chft": 13623.33,
                "ht_chft": 39957.14,
                "hfg_eh": 11.23,
                "hfv_eh": 11.23,
                "hr_eh": 10.26,
                "hl_eh": 16.42,
                # Total Wärme
                "sw_chft": 86370.36,
            },
        }
        for key, value in expected["unit1"].items():
            try:
                if partial_period_factor != 1.0 and key in (
                    "wwg_chf",
                    "wwv_chf",
                    "wwbt_chf",
                    "wwa_chf",
                    "wwt_chf",
                    "hr",
                ):
                    # Allow for a bigger delta due to non-linear scaling
                    expected_delta_factor = 0.1
                elif partial_period_factor != 1.0 and key in (
                    "hfg_chf",
                    "hfv_chf",
                    "hr_chf",
                    "hl_chf",
                    "ht_chf",
                    "sw_chf",
                ):
                    # Allow for an even bigger delta due to non-linear scaling
                    expected_delta_factor = 0.4
                else:
                    expected_delta_factor = 0.01
                self.assertAlmostEqual(
                    unformat(context[key]),
                    value * partial_period_factor,
                    delta=expected_delta_factor * abs(value),
                )
            except AssertionError as e:
                raise AssertionError(
                    f"Unit 1 context variable '{key}' is not '{value * partial_period_factor}'"
                ) from e
        for key, value in expected["building"].items():
            try:
                self.assertAlmostEqual(unformat(context[key]), value, delta=0.01 * abs(value))
            except AssertionError as e:
                raise AssertionError(f"Building context variable '{key}' is not '{value}'") from e
