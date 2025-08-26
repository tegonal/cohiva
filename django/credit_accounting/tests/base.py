import credit_accounting.tests.data as credit_accounting_testdata
import geno.tests.data as geno_testdata
from geno.tests.base import BaseTestCase


class CreditAccountingTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        # geno_testdata.create_members(cls)
        # geno_testdata.create_shares(cls)
        geno_testdata.create_users(cls)
        # geno_testdata.create_templates(cls)
        # geno_testdata.create_documenttypes(cls)
        # geno_testdata.create_invoicecategories(cls)
        credit_accounting_testdata.create_accounts(cls)

    # def setUp(self):
    #    self.client.login(username='superuser', password='secret')
