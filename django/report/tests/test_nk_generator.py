import datetime

from django.conf import settings
from django.test import tag

import report.tests.data as testdata
from geno.models import Contract
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
        self.assertEqual(report.rental_units[2].name, "strom_pauschal")
        self.assertEqual(report.rental_units[2].is_virtual, True)

    def test_load_contracts(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        report.load_contracts()
        self.assertEqual(report.get_warnings(), [])
        self.assertEqual(
            len(report.contracts), len(self.contracts) + len(report.virtual_contracts)
        )

    def test_load_costs(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        report.load_contracts()
        report.load_costs()
        self.assertEqual(report.get_warnings(), [])
        self.assertEqual(len(report.costs), 7)
        self.assertEqual(report.costs[0].name, "Hauswartung_ServiceHeizungLüftung")
        self.assertEqual(report.costs[0].billing_group, "Hauswartung, Service Heizung/Lüftung")
        self.assertEqual(report.costs[0].cost_type_id, "simple_total")
        self.assertEqual(report.costs[5].name, "Lift")
        self.assertEqual(report.costs[5].billing_group, "Lift")
        self.assertEqual(report.costs[5].cost_type_id, "simple_total")

    def test_assign_rental_units_to_contracts(self):
        self.configure_test_report_minimal()
        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        report.load_contracts()
        report.assign_rental_unit_months_to_contracts()

        for idx in range(report.num_months):
            self.assertEqual(
                report.rental_units[3].assigned_contract_per_month[idx].id, self.contracts[0].id
            )

    def test_assign_rental_units_to_contracts_with_change(self):
        self.configure_test_report_minimal()
        self.contracts[0].date_end = datetime.datetime(2023, 9, 30)
        self.contracts[0].save()

        new_contract = Contract.objects.create(
            date=datetime.datetime(2023, 12, 1), state="unterzeichnet"
        )
        new_contract.rental_units.set([self.rentalunits[0]])
        new_contract.contractors.set([self.addresses[0]])
        new_contract.save()

        report = NkReportGenerator(self.report, True, output_root="/tmp/")
        report.load_rental_units()
        report.load_contracts()
        report.assign_rental_unit_months_to_contracts()
        for idx in range(3):
            # Old contract
            self.assertEqual(
                report.rental_units[3].assigned_contract_per_month[idx].id, self.contracts[0].id
            )
        for idx in range(3, 5):
            # Virtual contract "Leerstand"
            self.assertEqual(report.rental_units[3].assigned_contract_per_month[idx].id, -6)
        for idx in range(5, report.num_months):
            # New contract
            self.assertEqual(
                report.rental_units[3].assigned_contract_per_month[idx].id, new_contract.id
            )

    # Tests TODO
    # - contract with a different billing_contract
    #

    @tag("slow-test")
    def test_report_minimal_dryrun(self):
        self.configure_test_report_minimal()

        report_generator = NkReportGenerator(self.report, True, settings.SMEDIA_ROOT)
        report_generator.generate()
        status_msg = report_generator.get_status_message()
        self.assertTrue(
            status_msg.startswith(
                ("Nebenkostenabrechung mit WARNUNGEN erstellt", "Nebenkostenabrechnung erstellt")
            )
        )
