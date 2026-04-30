import report.tests.data as testdata
from report.nk.cost import NkCostValueType, NkCostVEWA
from report.nk.cost.vewa import NkCostVEWACategories
from report.nk.generator import NkReportGenerator
from report.nk.measurement_data import (
    NkMeasurementDataBase,
)
from report.nk.rental_unit import NkVirtualRentalUnitId

from .base import NkReportTestCase


class NkMeasurementTestDataBuildingAnnual(NkMeasurementDataBase):
    def __init__(self, report_generator, measurements_config):
        super().__init__(report_generator, measurements_config)
        self.num_months = report_generator.num_months

    def load(self):
        # Building-level data: Just one annual value
        self.data = {
            "verbrauch": 10000,
        }


class NkMeasurementTestDataRentalUnits(NkMeasurementDataBase):
    def __init__(self, report_generator, measurements_config):
        super().__init__(report_generator, measurements_config)
        self.num_months = report_generator.num_months

    def load(self):
        # Per-unit measurement data keyed by ru.name
        # 001a:  300
        # 001b:  150
        # allg:   12
        # Total: 462 (151 + 151 + 10*16)
        equal_months = self.num_months - 2
        self.data = {
            "001a": {
                # 100 + 100 + 10*10 = 300
                "verbrauch": [100, 100] + equal_months * [10.0],
            },
            "001b": {
                # 50 + 50 + 10*5 = 150
                "verbrauch": [50, 50] + equal_months * [5.0],
            },
            "allg": {
                # 12*1 = 12
                "verbrauch": self.num_months * [1]
            },
        }


class NKCostVEWATest(NkReportTestCase):
    vewa_cost_config_annual = {
        "class": NkCostVEWA,
        "name": "Wasser_Abwasser",
        "billing_group": "VEWA",
        "vewa_category": NkCostVEWACategories.WATER_GENERAL,
        "base_cost_factor_key": "Wasserkosten:Grundkostenanteil",
        "measurement_data": {
            "building": {"class": NkMeasurementTestDataBuildingAnnual},
            "rental_units": {"class": NkMeasurementTestDataRentalUnits},
        },
    }
    total_cost = 31915
    total_usage = 10000
    total_weight = 462
    base_factor = 0.3

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_nk_data(cls)

    def _setup_report(self):
        """Configure a minimal report and populate measurement data for ZEV strom."""
        self.configure_test_report_minimal()
        report_generator = NkReportGenerator(self.report, True, output_root="/tmp/")
        report_generator.load_rental_units()
        report_generator.load_contracts()
        return report_generator

    def test_vewa_cost_calculation_annual(self):
        """
        Test NkCostVEWA per-unit cost calculation with annual usage data
        and base cost split among all units, also if they have no usage data.
        """
        rg = self._setup_report()
        num_months = rg.num_months

        cost = NkCostVEWA(rg, self.vewa_cost_config_annual)
        cost.load_input_data()
        cost.split_costs()

        # Check that annual usage is correctly split into monthly usage by monthly weights
        for m in range(num_months):
            if m < 2:
                expected_usage = self.total_usage * 151 / self.total_weight
            else:
                expected_usage = self.total_usage * 16 / self.total_weight
            self.assertAlmostEqual(
                cost.total_values[NkCostValueType.USAGE_USAGE].monthly_amounts[m],
                expected_usage,
                delta=0.0001 * expected_usage,
            )

        total_area = sum([x.area for x in rg.rental_units])

        # Recalculate expected values for 001a
        ru_001a = rg.get_rental_unit_by_name("001a")
        expected_base_cost_001a = self.total_cost * self.base_factor * ru_001a.area / total_area
        expected_usage_cost_001a = (
            self.total_cost * (1.0 - self.base_factor) * 300 / self.total_weight
        )
        expected_usage_001a = self.total_usage * 300 / self.total_weight
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.COST].amount,
            expected_base_cost_001a,
            delta=0.0001 * expected_base_cost_001a,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE].amount, ru_001a.area
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE_COST].amount,
            expected_usage_cost_001a,
            delta=0.0001 * expected_usage_cost_001a,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE_USAGE].amount,
            expected_usage_001a,
            delta=0.0001 * expected_usage_001a,
        )

        # Recalculate expected values for 001b
        ru_001b = rg.get_rental_unit_by_name("001b")
        expected_base_cost_001b = self.total_cost * self.base_factor * ru_001b.area / total_area
        expected_usage_cost_001b = (
            self.total_cost * (1.0 - self.base_factor) * 150 / self.total_weight
        )
        expected_usage_001b = self.total_usage * 150 / self.total_weight
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.COST].amount,
            expected_base_cost_001b,
            delta=0.0001 * expected_base_cost_001b,
        )
        self.assertEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.USAGE].amount, ru_001b.area
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.USAGE_COST].amount,
            expected_usage_cost_001b,
            delta=0.0001 * expected_usage_cost_001b,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.USAGE_USAGE].amount,
            expected_usage_001b,
            delta=0.0001 * expected_usage_001b,
        )

        # Virtual rental units (Allgemein)
        expected_base_cost_allg = self.total_cost * self.base_factor * 0 / total_area
        expected_usage_cost_allg = (
            self.total_cost * (1.0 - self.base_factor) * 12 / self.total_weight
        )
        expected_usage_allg = self.total_usage * 12 / self.total_weight
        self.assertAlmostEqual(
            cost.rental_unit_values[NkVirtualRentalUnitId.COMMON][NkCostValueType.COST].amount,
            expected_base_cost_allg,
            delta=0.0001 * expected_base_cost_allg,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[NkVirtualRentalUnitId.COMMON][
                NkCostValueType.USAGE_COST
            ].amount,
            expected_usage_cost_allg,
            delta=0.0001 * expected_usage_cost_allg,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[NkVirtualRentalUnitId.COMMON][
                NkCostValueType.USAGE_USAGE
            ].amount,
            expected_usage_allg,
            delta=0.0001 * expected_usage_allg,
        )

        # Units without measurement data → only base costs
        ru_g001 = rg.get_rental_unit_by_name("G001")
        expected_base_cost_g001 = self.total_cost * self.base_factor * ru_g001.area / total_area
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.COST].amount,
            expected_base_cost_g001,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.USAGE_COST].amount,
            0.0,
        )

        expected_base_cost_others = (
            self.total_cost * self.base_factor * (50 + 10 + 30) / total_area
        )

        # Grand total = sum of all units
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.COST].amount,
            expected_base_cost_001a
            + expected_base_cost_001b
            + expected_base_cost_allg
            + expected_base_cost_g001
            + expected_base_cost_others,
            places=4,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.USAGE_COST].amount,
            expected_usage_cost_001a + expected_usage_cost_001b + expected_usage_cost_allg,
            places=4,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.USAGE_USAGE].amount,
            expected_usage_001a + expected_usage_001b + expected_usage_allg,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.COST].amount
            + cost.total_values[NkCostValueType.USAGE_COST].amount,
            self.total_cost,
            places=4,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.USAGE_USAGE].amount,
            self.total_usage,
        )

    def test_vewa_cost_calculation_monthly(self):
        """
        Test NkCostVEWA per-unit cost calculation with annual usage data
        and base cost ONLY split among all units THAT HAVE usage data.
        """
        rg = self._setup_report()
        # num_months = rg.num_months

        cost = NkCostVEWA(rg, self.vewa_cost_config_annual)
        cost.load_input_data()
        cost.split_costs()

    # def test_zev_extra_context(self):
    #     """Test that get_extra_context() returns the correct Stromkosten variables."""
    #     rg = self._setup_report_with_strom_data()
    #
    #     cost = NkCostVEWA(rg, self.zev_cost_config)
    #     cost.load_input_data()
    #     cost.split_costs()
    #     rg.assign_rental_unit_months_to_contracts()
    #
    #     ru_001a = rg.get_rental_unit_by_name("001a")
    #     ctx = cost.get_extra_context(ru_001a, rg.get_contract_by_id(self.contracts[0].id))
    #
    #     num_months = rg.num_months
    #     # ssd: Eigenverbrauch Solar direkt
    #     expected_ssd_kwh = 50.0 * num_months  # 50 kWh/month
    #     expected_ssd_chf = expected_ssd_kwh * 0.1453
    #     self.assertEqual(ctx["ssd"], nformat(expected_ssd_kwh, 0))
    #     self.assertEqual(ctx["ssd_chf"], f"{expected_ssd_chf:,.2f}".replace(",", "'"))
    #
    #     # snh/snt: Netzstrom hoch/tief
    #     expected_snh_kwh = 30.0 * num_months  # 30 kWh/month
    #     expected_snh_chf = expected_snh_kwh * self.tarif_hoch
    #     expected_snt_kwh = 20.0 * num_months  # 20 kWh/month
    #     expected_snt_chf = expected_snt_kwh * self.tarif_nieder
    #     self.assertEqual(ctx["snh"], nformat(expected_snh_kwh, 0))
    #     self.assertEqual(ctx["snt"], nformat(expected_snt_kwh, 0))
    #     self.assertEqual(ctx["snh_chf"], nformat(expected_snh_chf))
    #     self.assertEqual(ctx["snt_chf"], nformat(expected_snt_chf))
    #
    #     # sss: Eigenverbrauch Solar via Speicher
    #     # kwh_netz = 50/month, kwh_speicher = 0.3 * 50 = 15/month
    #     expected_sss_kwh = 15.0 * num_months
    #     self.assertEqual(ctx["sss"], nformat(expected_sss_kwh, 0))
    #
    #     # Building totals
    #     expected_ssdt = num_months * (50 + 10 + 100 + 1)
    #     expected_snht = num_months * (30 + 6 + 70 + 2)
    #     self.assertEqual(ctx["ssdt"], nformat(expected_ssdt, 0))
    #     self.assertEqual(ctx["ssd_chft"], nformat(expected_ssdt * self.tarif_eigenstrom))
    #     self.assertEqual(ctx["snht"], nformat(expected_snht, 0))
    #     self.assertEqual(ctx["snh_chft"], nformat(expected_snht * self.tarif_hoch))
    #     self.assertIsInstance(ctx["stot_chft"], str)
    #
    #     # Units without data get zeros in context
    #     ru_g001 = rg.get_rental_unit_by_name("G001")
    #     ctx_g001 = cost.get_extra_context(ru_g001, rg.get_contract_by_id(self.contracts[2].id))
    #     self.assertEqual(ctx_g001["ssd"], "0")
    #     self.assertEqual(ctx_g001["sss"], "0")
    #     self.assertEqual(ctx_g001["st_chf"], "0.00")
    #
    # def test_zev_no_measurement_data(self):
    #     """When no measurement data is present, all costs are zero."""
    #     self.configure_test_report_minimal()
    #     rg = NkReportGenerator(self.report, True, output_root="/tmp/")
    #     rg.load_rental_units()
    #
    #     cost = NkCostVEWA(rg, self.zev_cost_config)
    #     # Remove measurement data
    #     cost.measurements = {
    #         "building": NkMeasurementDataBase(rg, {}),
    #         "rental_units": NkMeasurementDataBase(rg, {}),
    #     }
    #     cost.load_input_data()
    #     cost.split_costs()
    #
    #     self.assertAlmostEqual(cost.total_values[NkCostValueType.COST].amount, 0.0)
    #     for ru in rg.rental_units:
    #         self.assertAlmostEqual(
    #             cost.rental_unit_values[ru.id][NkCostValueType.COST].amount, 0.0
    #         )
    #
    # def test_zev_invalid_correction_rental_unit(self):
    #     self.configure_test_report_minimal()
    #     inputdata = ReportInputData.objects.get(
    #         name=ReportInputField.objects.get(name="Strom:Korrekturen"), report=self.report
    #     )
    #     inputdata.value = json.dumps(
    #         {
    #             "_INVALID_RU_": [
    #                 {
    #                     "desc": "Test",
    #                     "tarif": "mittel",
    #                     "kwh": 12 * [-1],
    #                 }
    #             ]
    #         }
    #     )
    #     inputdata.save()
    #     rg = NkReportGenerator(self.report, True, output_root="/tmp/")
    #     rg.load_rental_units()
    #
    #     with self.assertRaises(ValueError):
    #         NkCostVEWA(rg, self.zev_cost_config)
    #
    # def test_zev_invalid_correction_tarif(self):
    #     self.configure_test_report_minimal()
    #     inputdata = ReportInputData.objects.get(
    #         name=ReportInputField.objects.get(name="Strom:Korrekturen"), report=self.report
    #     )
    #     inputdata.value = json.dumps(
    #         {
    #             "allg": [
    #                 {
    #                     "desc": "Test",
    #                     "tarif": "_INVALID_TARIF_",
    #                     "kwh": 12 * [-1],
    #                 }
    #             ]
    #         }
    #     )
    #     inputdata.save()
    #     rg = NkReportGenerator(self.report, True, output_root="/tmp/")
    #     rg.load_rental_units()
    #
    #     with self.assertRaises(ValueError):
    #         NkCostVEWA(rg, self.zev_cost_config)
