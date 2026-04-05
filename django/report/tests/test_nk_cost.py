from django.db.models import Sum

import report.tests.data as testdata
from geno.models import RentalUnit
from report.nk.cost import NkCost, NkCostPerRentalUnit, NkCostValueType, NkTotalCost
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

    def test_split_costs_with_section_weights(self):
        """
        Test that NkTotalCost correctly applies section_weights when splitting costs.

        Two NkTotalCost instances are compared:
        - default section weights (all sections weighted equally at 1.0)
        - "reinigung" section weights (Wohnen=0.7, Gewerbe=1.0, Lager=1.0, Allgemein=0.0)

        Test data (from geno testdata):
        - 001a: Wohnung, area=100  → wohnen section
        - 001b: Wohnung, area=20   → wohnen section
        - G001: Gewerbe, area=200  → gewerbe section
        - G002: Gewerbe, area=50   → gewerbe section
        - L001: Lager,   area=10   → lager section
        - L002: Lager,   area=30   → lager section
        """
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()

        # Cost 1: default section weights — all sections weighted equally
        default_cost = NkTotalCost(
            report,
            {
                "name": "Wasser_Abwasser",
                "object_weights": "area",
            },
        )
        default_cost.load_input_data()
        default_cost.split_costs()

        # Cost 2: "reinigung" section weights — Wohnen=0.7, Gewerbe=1.0, Lager=1.0, Allgemein=0.0
        reinigung_cost = NkTotalCost(
            report,
            {
                "name": "Reinigung",
                "object_weights": "area",
                "section_weights": "reinigung",
            },
        )
        reinigung_cost.load_input_data()
        reinigung_cost.split_costs()

        # Expected weights for default (section weight 1.0 for all sections):
        # total weighted area = 100 + 20 + 200 + 50 + 10 + 30 = 410
        total_area_default = 100 + 20 + 200 + 50 + 10 + 30  # 410

        # Expected weights for reinigung (Wohnen=0.7, Gewerbe=1.0, Lager=1.0, Allgemein=0.0):
        # total weighted area = 0.7*120 + 1.0*250 + 1.0*40 = 84 + 250 + 40 = 374
        total_area_reinigung = 0.7 * (100 + 20) + 1.0 * (200 + 50) + 1.0 * (10 + 30)  # 374

        ru = self.rentalunits[0]  # 001a: Wohnung, area=100 → wohnen section

        # With default section weights, cost is proportional to area alone
        expected_default_ru = 31915.0 * float(ru.area) / total_area_default
        self.assertAlmostEqual(
            default_cost.rental_unit_values[ru.id][NkCostValueType.COST].amount,
            expected_default_ru,
            places=2,
        )

        # With "reinigung" section weights, the Wohnung unit's area is scaled by 0.7
        expected_reinigung_ru = 43875.95 * (0.7 * float(ru.area)) / total_area_reinigung
        self.assertAlmostEqual(
            reinigung_cost.rental_unit_values[ru.id][NkCostValueType.COST].amount,
            expected_reinigung_ru,
            places=2,
        )

        # Verify section totals reflect the section weights
        expected_default_wohnen = 31915.0 * (100 + 20) / total_area_default
        self.assertAlmostEqual(
            default_cost.section_values["wohnen"][NkCostValueType.COST].amount,
            expected_default_wohnen,
            places=2,
        )

        expected_reinigung_wohnen = 43875.95 * (0.7 * (100 + 20)) / total_area_reinigung
        self.assertAlmostEqual(
            reinigung_cost.section_values["wohnen"][NkCostValueType.COST].amount,
            expected_reinigung_wohnen,
            places=2,
        )

    def test_cost_per_rental_unit(self):
        """
        Test NkCostPerRentalUnit covers all three calculation paths:

        1. Fixed fee by rental unit name (G001 → 100 CHF/month)
        2. fee_per_unit + min_occupancy × fee_per_person
           - 001a (min_occupancy=3): 5 + 3×4 = 17 CHF/month
           - 001b (min_occupancy=1): 5 + 1×4 =  9 CHF/month
        3. Zero — no min_occupancy, no fixed fee (G002, L001, L002 → 0 CHF/month)

        configure_test_report_minimal() already sets:
          Internet:Tarif:ProWohnung = 5.0
          Internet:Tarif:ProPerson  = 4.0
          Internet:Tarif:Fix        = "" (empty)
        We update Fix to add a fixed fee for G001.
        """
        self.configure_test_report_minimal()
        self.update_field("Internet:Tarif:Fix", '{"G001": 100}')

        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()

        cost = NkCostPerRentalUnit(
            report,
            {
                "name": "Internet/WLAN",
                "fee_per_unit_key": "Internet:Tarif:ProWohnung",
                "fee_per_person_key": "Internet:Tarif:ProPerson",
                "fixed_fees_key": "Internet:Tarif:Fix",
            },
        )
        cost.load_input_data()
        cost.split_costs()

        num_months = report.num_months
        ru_001a = self.rentalunits[0]  # Wohnung, min_occupancy=3
        ru_001b = self.rentalunits[1]  # Wohnung, min_occupancy=1
        ru_G001 = self.rentalunits[2]  # Gewerbe, fixed fee = 100 CHF/month
        ru_G002 = self.rentalunits[3]  # Gewerbe, no min_occupancy → 0

        # Path 2: fee_per_unit + min_occupancy × fee_per_person
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001a.id][NkCostValueType.COST].amount,
            (5.0 + 3 * 4.0) * num_months,  # 17 CHF/month × 12
        )
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_001b.id][NkCostValueType.COST].amount,
            (5.0 + 1 * 4.0) * num_months,  # 9 CHF/month × 12
        )

        # Path 1: fixed fee by name
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_G001.id][NkCostValueType.COST].amount,
            100.0 * num_months,  # 100 CHF/month × 12
        )

        # Path 3: zero (no min_occupancy, no fixed fee)
        self.assertAlmostEqual(
            cost.rental_unit_values[ru_G002.id][NkCostValueType.COST].amount,
            0.0,
        )

        # Section totals aggregate correctly
        self.assertAlmostEqual(
            cost.section_values["wohnen"][NkCostValueType.COST].amount,
            (17.0 + 9.0) * num_months,  # 001a + 001b
        )
        self.assertAlmostEqual(
            cost.section_values["gewerbe"][NkCostValueType.COST].amount,
            100.0 * num_months,  # G001 only (G002 = 0)
        )
        self.assertAlmostEqual(
            cost.section_values["lager"][NkCostValueType.COST].amount,
            0.0,
        )

        # Grand total
        self.assertAlmostEqual(
            cost.total_values[NkCostValueType.COST].amount,
            (17.0 + 9.0 + 100.0) * num_months,
        )
