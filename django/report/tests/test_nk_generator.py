from django.conf import settings

import report.tests.data as testdata
from report.nk.generator import NkReportGenerator

from .base import NkReportTestCase


class NKReportGeneratorTest(NkReportTestCase):
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

    def test_load_rental_units(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        self.assertEqual(report.get_warnings(), [])
        self.assertEqual(len(report.rental_units), len(self.rentalunits) + 3)
        self.assertEqual(report.rental_units[0].id, -1)
        self.assertEqual(report.rental_units[0].name, "allg")
        self.assertEqual(report.rental_units[0].is_virtual, True)
        self.assertEqual(report.rental_units[1].id, -2)
        self.assertEqual(report.rental_units[1].name, "pauschal")
        self.assertEqual(report.rental_units[1].is_virtual, True)
        self.assertEqual(report.rental_units[2].id, -3)
        self.assertEqual(report.rental_units[2].name, "pauschal_strom")
        self.assertEqual(report.rental_units[2].is_virtual, True)

    def test_load_contracts(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        report.load_contracts()
        self.assertEqual(report.get_warnings(), [])
        self.assertEqual(len(report.contracts), len(self.contracts))

    def test_load_costs(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        report.load_contracts()
        report.load_costs()
        self.assertEqual(report.get_warnings(), [])
        self.assertEqual(len(report.costs), 1)
        self.assertEqual(report.costs[0].name, "Lift")
        self.assertEqual(report.costs[0].cost_type_id, "simple_total")

    def test_report_minimal_dryrun(self):
        self.configure_test_report_minimal()

        report_generator = NkReportGenerator(self.report, True, settings.SMEDIA_ROOT)
        report_generator.generate()
        status_msg = report_generator.get_status_message()
        # print(status_msg)
        self.assertTrue(status_msg.startswith("Nebenkostenabrechung mit WARNUNGEN erstellt:"))
