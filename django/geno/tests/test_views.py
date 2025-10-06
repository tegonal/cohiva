from django.apps import apps as django_apps
from django.conf import settings

import geno.tests.data as geno_testdata

from .base import GenoAdminTestCase


class GenoViewsTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)

    def test_views_status200(self):
        logged_in = self.client.login(username="superuser", password="secret")
        self.assertTrue(logged_in)
        paths = [
            #'import/([a-z_-]+)/',
            "export/adit/",
            "documents/shareconfirm/1/create/",
            "documents/shareconfirm/1/download/",
            "share/overview/",
            # ADDED BELOW 'share/overview/plot/',
            "share/export/",
            "share/confirm/",
            "share/statement/current_year/1/",
            "share/statement/current_year/",
            "share/mailing/",
            "share/interest/download/",
            "share/interest/transactions/",
            #'share/interest/adjust/',
            "share/check/",
            "share/duedate_reminder/",
            "member/overview/",
            # ADDED BELOW 'member/overview/plot/',
            "member/list/",
            "member/list_admin/",
            # TODO 'member/check_mailinglists/',
            "member/check_payments/",
            "member/send_mail/",
            # NEEDS SESSION'member/send_mail/select/',
            "member/send_mail/action/",
            "member/send_mail/contract/",
            "member/confirm/memberletter/",
            "address/export/",
            "maintenance/",
            # ADDED BELOW 'maintenance/check_portal_users/',
            "transaction/",
            "transaction_upload/",
            "transaction_upload/process/",
            "transaction_testdata/",
            "transaction_invoice/",
            "invoice/",
            "invoice/auto/",
            "invoice/download/contract/1/",
            "invoice/overview/",
            "invoice/overview/all/",
            # TODO: NEEDS DATA'invoice/detail/contract/1/',
            # TODO: NEEDS DATA'invoice/detail/contract/1/all/',
            # TODO: OLD CODE'contract/create/',
            # TODO: OLD CODE'contract/create_letter/',
            "contract/create_documents/check/",
            "rental/units/",
            "rental/units/mailbox/",
            "rental/units/protocol/",
            "odt2pdf/",
            #'webstamp/',
            #'oauth_client/',
            #'oauth_client/login'
            #'oauth_client/callback/',
            #'oauth_client/test/',
            "preview/",
        ]
        if hasattr(settings, "SHARE_PLOT") and settings.SHARE_PLOT:
            paths += [
                "member/overview/plot/",
                "share/overview/plot/",
            ]
        if django_apps.is_installed("portal"):
            paths += [
                "maintenance/check_portal_users/",
            ]
        for path in paths:
            response = self.client.get(f"/geno/{path}")
            if response.status_code != 200:
                print(f"FAILED PATH: /geno/{path} [{response.status_code}]")
            self.assertEqual(response.status_code, 200)
