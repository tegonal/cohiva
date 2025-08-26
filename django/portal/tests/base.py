from django import VERSION as DJANGO_VERSION
from django.conf import settings

import geno.tests.data as geno_testdata
import portal.tests.data as portal_testdata
from geno.tests.base import BaseTestCase


class PortalTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        geno_testdata.create_members(cls)
        # geno_testdata.create_shares(cls)
        geno_testdata.create_users(cls)
        # geno_testdata.create_templates(cls)
        # geno_testdata.create_documenttypes(cls)
        # geno_testdata.create_invoicecategories(cls)
        geno_testdata.create_prototype_users(cls)
        portal_testdata.create_tenants(cls)

    def get_secondary(self, uri):
        if DJANGO_VERSION < (4, 2):
            return self.client.get(uri, HTTP_HOST=settings.PORTAL_SECONDARY_HOST)
        else:
            return self.client.get(uri, headers={"host": settings.PORTAL_SECONDARY_HOST})

    def post_secondary(self, uri, data):
        if DJANGO_VERSION < (4, 2):
            return self.client.post(uri, data, HTTP_HOST=settings.PORTAL_SECONDARY_HOST)
        else:
            return self.client.post(uri, data, headers={"host": settings.PORTAL_SECONDARY_HOST})

    # def setUp(self):
    #    self.client.login(username='superuser', password='secret')
