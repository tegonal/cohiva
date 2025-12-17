from unittest.mock import patch

from django.apps import apps as django_apps
from django.conf import settings
from django.urls import reverse

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
            reverse("geno:share-statement-form"),
            reverse("geno:share-statement", args=["current_year"]),
            reverse("geno:share-statement-for-address", args=["current_year", 1]),
            "share/mailing/",
            "share/interest/download/",
            "share/interest/transactions/",
            #'share/interest/adjust/',
            "share/duedate_reminder/",
            "member/overview/",
            # ADDED BELOW 'member/overview/plot/',
            "member/list/",
            "member/list_admin/",
            # TODO 'member/check_mailinglists/',
            "member/check_payments/",
            reverse("geno:mail-wizard-start"),
            # NEEDS SESSION reverse("geno:mail-wizard-select"),
            reverse("geno:mail-wizard-action"),
            "member/confirm/memberletter/",
            "address/export/",
            "maintenance/",
            # ADDED BELOW 'maintenance/check_portal_users/',
            "transaction/",
            reverse("geno:transaction-upload"),
            reverse("geno:transaction-process"),
            reverse("geno:transaction-testdata"),
            reverse("geno:transaction-invoice"),
            reverse("geno:invoice-manual"),
            reverse("geno:invoice-batch"),
            reverse("geno:invoice-batch-generate"),
            reverse("geno:invoice-download", args=["contract", 1]),
            reverse("geno:debtor-list"),
            # TODO: NEEDS DATA'debtor/detail/contract/1/',
            # TODO: OLD CODE'contract/create/',
            # TODO: OLD CODE'contract/create_letter/',
            reverse("geno:contract-check-forms"),
            reverse("geno:contract-report"),
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
            reverse("geno:sysadmin-overview"),
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
            if not path.startswith("/geno/"):
                path = f"/geno/{path}"
            response = self.client.get(path)
            if response.status_code != 200:
                print(f"FAILED PATH: {path} [{response.status_code}]")
            self.assertEqual(response.status_code, 200)

    @patch("geno.views.consolidate_invoices")
    def test_debtor_view_consolidate_invoices(self, mock_consolidate_invoices):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:debtor-list")
        response = self.client.post(path, data={"consolidate": ""})
        self.assertEqual(response.status_code, 200)
        mock_consolidate_invoices.assert_called_once()

        # Don't consolidate on search/filter
        response = self.client.post(path, data={"search": ""})
        self.assertEqual(response.status_code, 200)
        mock_consolidate_invoices.assert_called_once()

    @patch("geno.views.consolidate_invoices")
    def test_debtor_view_consolidate_invoices_detail(self, mock_consolidate_invoices):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:debtor-detail", args=["p", self.addresses[0].pk])
        response = self.client.post(path, data={"consolidate": ""})
        self.assertEqual(response.status_code, 200)
        mock_consolidate_invoices.assert_called_once_with(self.addresses[0])

        # Don't consolidate on search/filter
        response = self.client.post(path, data={"search": ""})
        self.assertEqual(response.status_code, 200)
        mock_consolidate_invoices.assert_called_once()
