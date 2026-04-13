from django.db.models import Sum

import report.tests.data as testdata
from geno.models import RentalUnit
from report.nk.cost import NkCost, NkCostValueType, NkTotalCost
from report.nk.generator import NkReportGenerator

from .base import NkReportTestCase


class NKReportCostTest(NkReportTestCase):
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

    def test_split_costs_unit_weights(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        config = {
            "name": "Unit weight Test",
        }
        cost = NkCost(report, config)
        cost.split_costs()
        self.assertEqual(len(cost.rental_unit_values), len(report.rental_units))
        self.assertEqual(len(cost.section_values), len(report.sections))
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.WEIGHT].amount,
            len(self.rentalunits) * report.num_months,
        )

    def test_split_costs_total_by_area(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        config = {
            "name": "Wasser_Abwasser",  # Test data with costs CHF 31915.00
            "object_weights": "area",
        }
        cost = NkTotalCost(report, config)
        cost.load_input_data()
        cost.split_costs()
        # pprint(cost.rental_unit_values)
        # pprint(cost.total_values)
        total_area = float(RentalUnit.objects.aggregate(Sum("area")).get("area__sum"))
        self.assertAlmostEqual(cost.total_values[NkCostValueType.COST].amount, 31915.00)
        self.assertEqual(cost.total_values[NkCostValueType.USAGE].name, "Fläche")
        self.assertEqual(cost.total_values[NkCostValueType.USAGE].unit, "m2")
        self.assertAlmostEqual(cost.total_values[NkCostValueType.USAGE].amount, total_area)
        self.assertAlmostEqual(
            31915 / total_area * self.rentalunits[0].area,
            cost.rental_unit_values[self.rentalunits[0].id][NkCostValueType.COST].amount,
        )
