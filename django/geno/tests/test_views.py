import datetime
import io
import zipfile
from unittest.mock import DEFAULT, patch

from django.apps import apps as django_apps
from django.conf import settings
from django.http import FileResponse
from django.test import tag
from django.urls import reverse

import geno.tests.data as geno_testdata
from geno.models import Invoice, Share, ShareType
from geno.views import ShareStatementView

from .base import GenoAdminTestCase


def create_fake_pdf(
    ref_number, address, context, output_filename, render, email_template, email_subject, dry_run
):
    with open(f"/tmp/{output_filename}", "wb") as dummy_pdf:
        dummy_pdf.write(b"Dummy PDF")
    return DEFAULT


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

    def get_invoice_manual_data(self, preview=True, send_email=False):
        data = {
            "date": datetime.date.today().strftime("%d.%m.%Y"),
            "category": self.invoicecategories[0].pk,
            "address": self.addresses[0].pk,
            "extra_text": "Test extra_text",
            "form-0-date": datetime.date.today().strftime("%d.%m.%Y"),
            "form-0-text": "Test invoice item 1",
            "form-0-amount": "99.99",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "3",
        }
        if preview:
            data["submit_action_preview"] = ""
        else:
            data["submit_action_save"] = ""
        if send_email:
            data["send_email"] = "on"
        return data

    @patch("geno.views.create_qrbill", side_effect=create_fake_pdf, return_value=([], 0, None))
    def test_invoice_manual_process_preview(self, mock_create_qrbill):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:invoice-manual")
        response = self.client.post(path, data=self.get_invoice_manual_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertEqual(b"".join(response.streaming_content), b"Dummy PDF")
        self.assertEqual(Invoice.objects.count(), 0)

    @patch("geno.views.create_qrbill", side_effect=create_fake_pdf, return_value=([], 0, None))
    def test_invoice_manual_process_download(self, mock_create_qrbill):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:invoice-manual")
        response = self.client.post(path, data=self.get_invoice_manual_data(preview=False))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertEqual(b"".join(response.streaming_content), b"Dummy PDF")
        self.assertEqual(Invoice.objects.count(), 1)

    @patch(
        "geno.views.create_qrbill",
        side_effect=create_fake_pdf,
        return_value=([], 1, "test@example.test"),
    )
    def test_invoice_manual_process_send_email(self, mock_create_qrbill):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:invoice-manual")
        response = self.client.post(
            path, data=self.get_invoice_manual_data(preview=False, send_email=True)
        )
        self.assertEqual(response.status_code, 200)
        self.assertInHTMLResponse(
            " mit QR-Rechnung an test@example.test geschickt. Rechnung_Member Invoice",
            response,
            raw=True,
        )
        self.assertEqual(Invoice.objects.count(), 1)

    @patch(
        "geno.views.create_qrbill",
        side_effect=create_fake_pdf,
        return_value=([], 0, "test@example.test"),
    )
    def test_invoice_manual_process_email_error(self, mock_create_qrbill):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:invoice-manual")
        response = self.client.post(
            path, data=self.get_invoice_manual_data(preview=False, send_email=True)
        )
        self.assertEqual(response.status_code, 200)
        self.assertInHTMLResponse(
            "FEHLER beim Versenden des Emails ",
            response,
            raw=True,
        )
        self.assertEqual(Invoice.objects.count(), 0)

    @patch(
        "geno.views.create_qrbill",
        return_value=(["Error: TEST"], 1, "test@example.test"),
    )
    def test_invoice_manual_process_creation_error(self, mock_create_qrbill):
        self.client.login(username="superuser", password="secret")
        path = reverse("geno:invoice-manual")
        response = self.client.post(
            path, data=self.get_invoice_manual_data(preview=False, send_email=False)
        )
        self.assertEqual(response.status_code, 200)
        self.assertInHTMLResponse(
            "Fehler beim Erzeugen der Rechnung für ",
            response,
            raw=True,
        )
        self.assertEqual(Invoice.objects.count(), 0)


class Odt2PdfViewTest(GenoAdminTestCase):
    @tag("slow-test")
    def test_odt2pdf_view_singlefile(self):
        self.client.login(username="superuser", password="secret")
        with open("geno/tests/template_test.odt", "rb") as dummy_file:
            response = self.client.post(reverse("geno:odt2pdf"), {"file": dummy_file})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, FileResponse))
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertInPDF(response.getvalue(), "Template-Test")

    @tag("slow-test")
    def test_odt2pdf_view_multifile(self):
        self.client.login(username="superuser", password="secret")
        with open("/tmp/test.zip", "wb") as zipfile_object:
            with zipfile.ZipFile(zipfile_object, "w") as archive:
                archive.write("geno/tests/template_test.odt", "testA.odt")
                archive.write("geno/tests/template_test.odt", "testB.odt")
        with open("/tmp/test.zip", "rb") as inputfile:
            response = self.client.post(reverse("geno:odt2pdf"), {"file": inputfile})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, FileResponse))
        self.assertEqual(response.headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(response.getvalue())) as zip_file:
            self.assertInPDF(zip_file.read("testA.pdf"), "Template-Test")
            self.assertInPDF(zip_file.read("testB.pdf"), "Template-Test")


class ShareStatementViewTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        stype_as = ShareType.objects.get(name="Anteilschein")
        Share.objects.all().delete()
        Share.objects.create(
            value=200,
            quantity=1,
            share_type=stype_as,
            date=datetime.date(2020, 1, 1),
            name=cls.addresses[0],
            state="bezahlt",
        )
        Share.objects.create(
            value=200,
            quantity=5,
            share_type=stype_as,
            date=datetime.date(2020, 1, 1),
            name=cls.addresses[1],
            state="bezahlt",
        )
        Share.objects.create(
            value=200,
            quantity=6,
            share_type=stype_as,
            date=datetime.date(2020, 1, 1),
            name=cls.addresses[2],
            state="bezahlt",
        )
        Share.objects.create(
            value=200,
            quantity=10,
            share_type=stype_as,
            date=datetime.date(2020, 1, 1),
            name=cls.addresses[3],
            state="bezahlt",
        )

    def test_get_object_skips(self):
        view = ShareStatementView()
        view.enddate = datetime.date(2020, 12, 31)
        obj = view.get_objects()
        self.assertEqual(len(obj), 2)
        self.assertIn("Anzahl ignoriert=2", view.extra_description_info)

        Share.objects.create(
            value=500,
            quantity=1,
            share_type=ShareType.objects.get(name="Depositenkasse"),
            date=datetime.date(2020, 1, 1),
            name=self.addresses[1],
            state="bezahlt",
        )
        obj = view.get_objects()
        self.assertEqual(len(obj), 3)
        self.assertIn("Anzahl ignoriert=1", view.extra_description_info)

        view.address_id = self.addresses[0].pk
        obj = view.get_objects()
        self.assertEqual(len(obj), 1)
        self.assertIn("Anzahl ignoriert=0", view.extra_description_info)
