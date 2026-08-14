import report.tests.data as testdata
from geno.utils import nformat
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
            self.usage_key: 10000,
        }


class NkMeasurementTestDataBuildingMonthly(NkMeasurementDataBase):
    def __init__(self, report_generator, measurements_config):
        super().__init__(report_generator, measurements_config)
        self.num_months = report_generator.num_months

    def load(self):
        # Building-level data: Monthly costs
        self.data = {
            self.costs_key: 6 * [600] + 6 * [200],  # total = 3600 + 1200 = 4800
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
                self.usage_key: [100, 100] + equal_months * [10.0],
            },
            "001b": {
                # 50 + 50 + 10*5 = 150
                self.usage_key: [50, 50] + equal_months * [5.0],
            },
            "allg": {
                # 12*1 = 12
                self.usage_key: self.num_months * [1]
            },
        }


class NKCostVEWATest(NkReportTestCase):
    vewa_cost_config_annual = {
        "class": NkCostVEWA,
        "name": "Wasser_Abwasser",
        "billing_group": "Wasserkosten",
        "vewa_category": NkCostVEWACategories.WATER_GENERAL,
        "base_cost_factor": 0.3,
        "exclude_zero_usage_units": False,
        "Betrag": 31915.0,
        "measurement_data": {
            "building": {"class": NkMeasurementTestDataBuildingAnnual},
            "rental_units": {"class": NkMeasurementTestDataRentalUnits},
        },
    }
    vewa_cost_config_monthly = {
        "class": NkCostVEWA,
        "name": "Fernwaerme_Warmwasser",
        "billing_group": "Wärmekosten",
        "vewa_category": NkCostVEWACategories.HEAT_WATER,
        "base_cost_factor_key": 0.3,
        "exclude_zero_usage_units": True,
        "measurement_data": {
            "building": {"class": NkMeasurementTestDataBuildingMonthly},
            "rental_units": {"class": NkMeasurementTestDataRentalUnits},
        },
    }
    total_cost_annual = 31915
    total_usage_annual = 10000
    total_cost_monthly = 4800
    total_usage_monthly = 462
    total_weight = 462
    base_factor = 0.3

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_nk_data(cls)

    def _setup_report(self):
        """Configure a minimal report and populate measurement data."""
        self.configure_test_report_empty()
        report_generator = NkReportGenerator(self.report, True, output_root="/tmp/")
        report_generator.load_rental_units()
        report_generator.load_contracts()
        return report_generator

    def test_vewa_cost_calculation_annual(self):
        """
        Test NkCostVEWA per-unit cost calculation with annual costs and usage data.
        - Base costs are split among all units, also if they have no usage data.
        - Usage costs and building-level usage are split among units with unit usage data as weights.
        """
        rg = self._setup_report()
        num_months = rg.num_months

        cost = NkCostVEWA(rg, self.vewa_cost_config_annual)
        cost.load_input_data()
        cost.split_costs()

        total_area = sum([x.area for x in rg.rental_units])
        total_cost = self.total_cost_annual
        total_usage = self.total_usage_annual

        # Check that annual usage is correctly split into monthly usage by monthly weights
        for m in range(num_months):
            if m < 2:
                expected_usage = total_usage * 151 / self.total_weight
            else:
                expected_usage = total_usage * 16 / self.total_weight
            self.assertAlmostEqual(
                cost.total_values[NkCostValueType.USAGE_USAGE].monthly_amounts[m],
                expected_usage,
                delta=0.0001 * expected_usage,
            )

        # Recalculate expected values for 001a
        ru_001a = rg.get_rental_unit_by_name("001a")
        expected_base_cost_001a = total_cost * self.base_factor * ru_001a.area / total_area
        expected_usage_cost_001a = total_cost * (1.0 - self.base_factor) * 300 / self.total_weight
        expected_usage_001a = total_usage * 300 / self.total_weight
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
        expected_base_cost_001b = total_cost * self.base_factor * ru_001b.area / total_area
        expected_usage_cost_001b = total_cost * (1.0 - self.base_factor) * 150 / self.total_weight
        expected_usage_001b = total_usage * 150 / self.total_weight
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.COST].amount,
            expected_base_cost_001b,
            delta=0.0001 * expected_base_cost_001b,
        )
        self.assertAlmostEqual(
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
        expected_base_cost_allg = total_cost * self.base_factor * 0 / total_area
        expected_usage_cost_allg = total_cost * (1.0 - self.base_factor) * 12 / self.total_weight
        expected_usage_allg = total_usage * 12 / self.total_weight
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
        expected_base_cost_g001 = total_cost * self.base_factor * ru_g001.area / total_area
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.COST].amount,
            expected_base_cost_g001,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.USAGE_COST].amount,
            0.0,
        )

        expected_base_cost_others = total_cost * self.base_factor * (50 + 10 + 30) / total_area

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
            total_cost,
            places=4,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.USAGE_USAGE].amount,
            total_usage,
        )

    def test_vewa_cost_calculation_monthly(self):
        """
        Test NkCostVEWA per-unit cost calculation with monthly costs and unit-level usage data.
        - Base costs are ONLY split among units that have usage data.
        - Total costs are taken from building measurement data.
        - Total usage and unit-level usage is taken from unit usage data.
        """
        rg = self._setup_report()
        num_months = rg.num_months

        cost = NkCostVEWA(rg, self.vewa_cost_config_monthly)
        cost.load_input_data()
        cost.split_costs()

        # Rental units with usage data
        ru_001a = rg.get_rental_unit_by_name("001a")
        ru_001b = rg.get_rental_unit_by_name("001b")

        total_area = ru_001a.area + ru_001b.area
        total_cost = self.total_cost_monthly
        total_usage = self.total_usage_monthly

        total_monthly_usage_costs = 6 * [600 * (1 - self.base_factor)] + 6 * [
            200 * (1 - self.base_factor)
        ]
        self.assertEqual(
            total_monthly_usage_costs,
            cost.total_values[NkCostValueType.USAGE_COST].monthly_amounts,
        )
        total_monthly_usage = 2 * [151] + 10 * [16]
        self.assertEqual(
            total_monthly_usage, cost.total_values[NkCostValueType.USAGE_USAGE].monthly_amounts
        )

        # Recalculate expected values for 001a
        expected_base_cost_001a = total_cost * self.base_factor * ru_001a.area / total_area
        monthly_usage = 2 * [100] + 10 * [10]
        expected_usage_cost_001a = sum(
            total_monthly_usage_costs[m] * monthly_usage[m] / total_monthly_usage[m]
            for m in range(num_months)
        )
        expected_usage_001a = 300
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
        expected_base_cost_001b = total_cost * self.base_factor * ru_001b.area / total_area
        monthly_usage = 2 * [50] + 10 * [5]
        expected_usage_cost_001b = sum(
            total_monthly_usage_costs[m] * monthly_usage[m] / total_monthly_usage[m]
            for m in range(num_months)
        )
        expected_usage_001b = 150
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
        expected_base_cost_allg = total_cost * self.base_factor * 0 / total_area
        monthly_usage = 12 * [1]
        expected_usage_cost_allg = sum(
            total_monthly_usage_costs[m] * monthly_usage[m] / total_monthly_usage[m]
            for m in range(num_months)
        )
        expected_usage_allg = 12
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

        # Units without measurement data → zero costs
        ru_g001 = rg.get_rental_unit_by_name("G001")
        expected_base_cost_g001 = 0
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.COST].amount,
            expected_base_cost_g001,
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_g001.id][NkCostValueType.USAGE_COST].amount,
            0.0,
        )

        expected_base_cost_others = 0

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
            total_cost,
            places=4,
        )
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.USAGE_USAGE].amount,
            total_usage,
        )

        ## Check first and last month
        # building costs: 600 / 200
        # building usage: 151 / 16
        expected_usage_001a = (100, 10)
        expected_base_costs_001a = (
            600 * self.base_factor * ru_001a.area / total_area,
            200 * self.base_factor * ru_001a.area / total_area,
        )
        expected_usage_costs_001a = (
            600 * (1 - self.base_factor) * expected_usage_001a[0] / 151,
            200 * (1 - self.base_factor) * expected_usage_001a[1] / 16,
        )
        month_index = [0, 11]
        for i in range(2):
            m = month_index[i]
            self.assertAlmostEqual(
                cost.rental_unit_values[ru_001a.id][NkCostValueType.COST].monthly_amounts[m],
                expected_base_costs_001a[i],
                delta=0.0001 * expected_base_costs_001a[i],
            )
            self.assertAlmostEqual(
                cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE_COST].monthly_amounts[m],
                expected_usage_costs_001a[i],
                delta=0.0001 * expected_usage_costs_001a[i],
            )
            self.assertAlmostEqual(
                cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE_USAGE].monthly_amounts[
                    m
                ],
                expected_usage_001a[i],
                delta=0.0001 * expected_usage_001a[i],
            )

    def test_vewa_context(self):
        """Test that _get_context() returns the correct VEWA variables."""
        rg = self._setup_report()

        cost = NkCostVEWA(rg, self.vewa_cost_config_annual)
        cost.load_input_data()
        cost.split_costs()
        rg.assign_rental_unit_months_to_contracts()

        ru_001a = rg.get_rental_unit_by_name("001a")
        ctx = cost._get_context(ru_001a, rg.get_contract_by_id(self.contracts[0].id))
        prefix = ""
        self.assertIn(prefix + "g", ctx)
        self.assertIn(prefix + "v", ctx)
        self.assertIn(prefix + "", ctx)
        self.assertIn(prefix + "a", ctx)
        self.assertIn(prefix + "g_chf", ctx)
        self.assertIn(prefix + "v_chf", ctx)
        self.assertIn(prefix + "_chf", ctx)
        self.assertIn(prefix + "a_chf", ctx)
        # Building
        self.assertIn(prefix + "gt", ctx)
        self.assertIn(prefix + "vt", ctx)
        self.assertIn(prefix + "t", ctx)
        self.assertIn(prefix + "at", ctx)
        self.assertIn(prefix + "g_chft", ctx)
        self.assertIn(prefix + "v_chft", ctx)
        self.assertIn(prefix + "_chft", ctx)
        self.assertIn(prefix + "a_chft", ctx)
        self.assertIn(prefix + "g_eh", ctx)
        self.assertIn(prefix + "v_eh", ctx)
        self.assertIn(prefix + "_eh", ctx)
        self.assertIn(prefix + "a_eh", ctx)

        # Check some values (not exhaustive)
        self.assertEqual(
            ctx["v"],
            nformat(
                cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE_USAGE].amount,
                precision=0,
            ),
        )

    def test_vewa_update_context_wa(self):
        """Test that _get_context() returns the correct VEWA variables."""
        rg = self._setup_report()

        cost = NkCostVEWA(rg, self.vewa_cost_config_annual)
        cost.load_input_data()
        cost.split_costs()
        rg.assign_rental_unit_months_to_contracts()

        ru_001a = rg.get_rental_unit_by_name("001a")
        ctx = {}
        agg = {}
        cost.update_context(ru_001a, rg.get_contract_by_id(self.contracts[0].id), ctx, agg)
        legacy_prefix = "wa"
        vewa_key = "vewa_wasser"
        self.assertIn(vewa_key, ctx)
        # Check some of the standard context variables
        self.assertIn("g", ctx[vewa_key][0])
        self.assertIn("v_chft", ctx[vewa_key][0])
        self.assertIn("", ctx[vewa_key][0])
        self.assertIn("at", ctx[vewa_key][0])
        # Check some of the standard context variables (legacy)
        self.assertIn(legacy_prefix + "g", ctx)
        self.assertIn(legacy_prefix + "v_chft", ctx)
        self.assertIn(legacy_prefix + "", ctx)
        self.assertIn(legacy_prefix + "at", ctx)
        # Check sums are present
        self.assertIn(legacy_prefix + "t_chft", ctx)
        self.assertIn(legacy_prefix + "t_chf", ctx)
        self.assertIn("s" + legacy_prefix + "_chft", ctx)
        self.assertIn("s" + legacy_prefix + "_chf", ctx)

        # Check some values (not exhaustive)
        self.assertEqual(
            ctx[legacy_prefix + "v"],
            nformat(
                cost.rental_unit_values[ru_001a.id][NkCostValueType.USAGE_USAGE].amount,
                precision=0,
            ),
        )
