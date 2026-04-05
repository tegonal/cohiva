import report.tests.data as testdata
from report.nk.cost import NkCostValueType, NkCostZEVStromallmend
from report.nk.generator import NkReportGenerator

from .base import NkReportTestCase


class NKCostZEVStromallmendTest(NkReportTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_nk_data(cls)

    def _setup_report_with_strom_data(self):
        """Configure a minimal report and populate measurement data for ZEV strom."""
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()

        # Building-level data: 1000 kWh produced per month, 300 kWh returned to grid
        # => einspeisefaktor = 300/1000 = 0.3 per month
        num_months = report.num_months
        report.data_amount["Strom_kwh_egon"] = num_months * [1000.0]
        report.data_amount["Strom_kwh_ruecklieferung"] = num_months * [300.0]

        # Per-unit measurement data keyed by ru.name
        # 001a (area=100): solar=50, ew_hoch=30, ew_nieder=20 kWh/month
        # 001b (area=20):  solar=10, ew_hoch=6,  ew_nieder=4  kWh/month
        # Others: no measurement data (skip ZEV)
        report.object_messung["001a"] = {
            "strom_solar": num_months * [50.0],
            "strom_ew_hoch": num_months * [30.0],
            "strom_ew_nieder": num_months * [20.0],
            "chf_netz_hoch": num_months * [9.0],   # 30 kWh * 0.30 CHF/kWh
            "chf_netz_nieder": num_months * [5.6],  # 20 kWh * 0.28 CHF/kWh
        }
        report.object_messung["001b"] = {
            "strom_solar": num_months * [10.0],
            "strom_ew_hoch": num_months * [6.0],
            "strom_ew_nieder": num_months * [4.0],
            "chf_netz_hoch": num_months * [1.8],   # 6 kWh * 0.30 CHF/kWh
            "chf_netz_nieder": num_months * [1.12], # 4 kWh * 0.28 CHF/kWh
        }
        return report

    def test_zev_cost_calculation(self):
        """Test NkCostZEVStromallmend per-unit cost calculation.

        For 001a per month:
          solar_eigen = 50 kWh * 0.1453 = 7.265 CHF
          kwh_netz = 30 + 20 = 50 kWh
          kwh_speicher = 0.3 * 50 = 15 kWh
          kwh_einkauf = 50 - 15 = 35 kWh
          chf_speicher = 15 * (0.1453 - 0.176) = 15 * (-0.0307) = -0.4605 CHF
            (negative because einspeisung tariff > eigenstrom tariff in summer months)
          chf_hkn = 35 * 0.07 = 2.45 CHF
          chf_total = 7.265 + (-0.4605) + 2.45 + 9.0 + 5.6 = 23.8545 CHF/month

        Note: tarif_einspeiseverguetung[0] = 0.176 (Jul, index 0 in the list)
        """
        report = self._setup_report_with_strom_data()

        cost = NkCostZEVStromallmend(report, {"name": "Stromkosten"})
        cost.load_input_data()
        cost.split_costs()

        num_months = report.num_months
        tarif_eigenstrom = 0.1453
        tarif_hkn = 0.07
        tarif_einspeiseverguetung = [
            0.176, 0.176, 0.176, 0.176, 0.176, 0.176,
            0.136, 0.136, 0.136, 0.136, 0.136, 0.136,
        ]

        # Recalculate expected values for 001a
        ru_001a = self.rentalunits[0]
        expected_chf_001a = 0.0
        for m in range(num_months):
            kwh_netz = 30.0 + 20.0
            kwh_speicher = 0.3 * kwh_netz
            kwh_einkauf = kwh_netz - kwh_speicher
            chf_eigen = 50.0 * tarif_eigenstrom
            chf_speicher = kwh_speicher * (tarif_eigenstrom - tarif_einspeiseverguetung[m])
            chf_hkn = kwh_einkauf * tarif_hkn
            chf_total_month = chf_eigen + chf_speicher + chf_hkn + 9.0 + 5.6
            expected_chf_001a += chf_total_month

        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.COST].amount,
            expected_chf_001a,
            places=4,
        )

        # Recalculate expected values for 001b
        ru_001b = self.rentalunits[1]
        expected_chf_001b = 0.0
        for m in range(num_months):
            kwh_netz = 6.0 + 4.0
            kwh_speicher = 0.3 * kwh_netz
            kwh_einkauf = kwh_netz - kwh_speicher
            chf_eigen = 10.0 * tarif_eigenstrom
            chf_speicher = kwh_speicher * (tarif_eigenstrom - tarif_einspeiseverguetung[m])
            chf_hkn = kwh_einkauf * tarif_hkn
            chf_total_month = chf_eigen + chf_speicher + chf_hkn + 1.8 + 1.12
            expected_chf_001b += chf_total_month

        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.COST].amount,
            expected_chf_001b,
            places=4,
        )

        # Units without measurement data → 0
        ru_G001 = self.rentalunits[2]
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_G001.id][NkCostValueType.COST].amount,
            0.0,
        )

        # Grand total = sum of all units
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.COST].amount,
            expected_chf_001a + expected_chf_001b,
            places=4,
        )

    def test_zev_extra_context(self):
        """Test that get_extra_context() returns the correct Stromkosten variables."""
        report = self._setup_report_with_strom_data()

        cost = NkCostZEVStromallmend(report, {"name": "Stromkosten"})
        cost.load_input_data()
        cost.split_costs()

        ru_001a = self.rentalunits[0]
        # Use a dummy contract — extra context doesn't use it currently
        ctx = cost.get_extra_context(ru_001a, None)

        num_months = report.num_months
        # ssd: Eigenverbrauch Solar direkt
        expected_ssd_kwh = 50.0 * num_months  # 50 kWh/month
        expected_ssd_chf = expected_ssd_kwh * 0.1453
        self.assertAlmostEqual(ctx["ssd"], expected_ssd_kwh, places=4)
        self.assertEqual(ctx["ssd_chf"], "{:,.2f}".format(expected_ssd_chf).replace(",", "'"))

        # sss: Eigenverbrauch Solar via Speicher
        # kwh_netz = 50/month, kwh_speicher = 0.3 * 50 = 15/month
        expected_sss_kwh = 15.0 * num_months
        self.assertAlmostEqual(ctx["sss"], expected_sss_kwh, places=4)

        # Building totals are formatted strings (non-empty)
        self.assertIsInstance(ctx["ssd_chft"], str)
        self.assertIsInstance(ctx["stot_chft"], str)

        # Units without data get zeros in context
        ru_G001 = self.rentalunits[2]
        ctx_g001 = cost.get_extra_context(ru_G001, None)
        self.assertAlmostEqual(ctx_g001["ssd"], 0.0)
        self.assertAlmostEqual(ctx_g001["sss"], 0.0)
        self.assertEqual(ctx_g001["st_chf"], "0.00")

    def test_zev_no_measurement_data(self):
        """When no measurement data is present, all costs are zero."""
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        # No data_amount or object_messung set

        cost = NkCostZEVStromallmend(report, {"name": "Stromkosten"})
        cost.load_input_data()
        cost.split_costs()

        self.assertAlmostEqual(cost.total_values[NkCostValueType.COST].amount, 0.0)
        for ru in report.rental_units:
            self.assertAlmostEqual(
                cost.rental_unit_values[ru.id][NkCostValueType.COST].amount, 0.0
            )
