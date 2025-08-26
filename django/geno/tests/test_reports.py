import datetime

import geno.tests.data as testdata
from geno.shares import check_rental_shares_report

# from pprint import pprint
# from geno.models import Invoice, Contract
# from geno.forms import MemberMailActionForm
from .base import GenoAdminTestCase


class ReportsTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        testdata.create_contracts(cls)

    def test_share_reduction_with_multiple_rental_units(self):
        self.contracts[0].share_reduction = 3000
        self.contracts[0].date_end = None
        self.contracts[0].save()

        report = check_rental_shares_report()
        ru1 = report[0]
        ru2 = report[1]
        # print("=====\n"+str(ru1))
        self.assertEqual(ru1.share_total, 10000)
        self.assertEqual(ru1.share_reduction, 3000)
        self.assertEqual(ru1.share_req, 7000)
        self.assertEqual(ru1.share_paid, 2000)
        self.assertEqual(ru1.share_remain, 5000)
        self.assertEqual(ru1.share_nocontract, 0)

        # print("=====\n"+str(ru2))
        self.assertEqual(ru2.share_total, 4000)
        self.assertEqual(ru2.share_reduction, 0)
        self.assertEqual(ru2.share_req, 4000)
        self.assertEqual(ru2.share_paid, 0)
        self.assertEqual(ru2.share_remain, 4000)

    def test_share_reduction_with_multiple_rental_units_shared_reduction(self):
        self.contracts[0].share_reduction = 11000
        self.contracts[0].date_end = None
        self.contracts[0].save()

        report = check_rental_shares_report()
        ru1 = report[0]
        ru2 = report[1]
        # print("=====\n"+str(ru1))
        self.assertEqual(ru1.share_total, 10000)
        self.assertEqual(ru1.share_reduction, 10000)
        self.assertEqual(ru1.share_req, 0)
        self.assertEqual(ru1.share_paid, 0)
        self.assertEqual(ru1.share_remain, 0)

        # print("=====\n"+str(ru2))
        self.assertEqual(ru2.share_total, 4000)
        self.assertEqual(ru2.share_reduction, 1000)
        self.assertEqual(ru2.share_req, 3000)
        self.assertEqual(ru2.share_paid, 2000)
        self.assertEqual(ru2.share_remain, 1000)

    def test_share_check_leerstand(self):
        self.contracts[0].date_end = datetime.date(2001, 8, 31)
        self.contracts[0].save()

        report = check_rental_shares_report()
        ru1 = report[0]

        # print("=====\n"+str(ru1))
        self.assertEqual(ru1.share_total, 10000)
        self.assertEqual(ru1.share_reduction, 0)
        self.assertEqual(ru1.share_req, 0)
        self.assertEqual(ru1.share_paid, 0)
        self.assertEqual(ru1.share_remain, 0)
        self.assertEqual(ru1.share_nocontract, 10000)
