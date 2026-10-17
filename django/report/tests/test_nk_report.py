# import time
import os
from decimal import Decimal
from pprint import pprint
from unittest.mock import patch

import requests
from django.conf import settings
from django.test import Client, tag
from requests.structures import CaseInsensitiveDict

import report.tests.data as testdata
from geno.models import Invoice, InvoiceCategory
from report.models import ReportOutput
from report.report_nk import main
from report.tests.check_report_output import CompareCSV

from .base import NkReportTestCase


def redirect_get_request(*args, **kwargs):
    return redirect_request("GET", *args, **kwargs)


def redirect_post_request(*args, **kwargs):
    return redirect_request("POST", *args, **kwargs)


def convert_to_requests_response(response, url_path):
    ## Convert response to a requests-like response
    r = requests.Response()
    r.status_code = response.status_code
    if hasattr(response, "content"):
        r._content = response.content
    else:
        r._content = response.getvalue()
    r.headers = CaseInsensitiveDict(response.headers)
    r.url = url_path
    r.encoding = response.charset
    r.reason = response.reason_phrase
    return r


def redirect_request(method, *args, **kwargs):
    c = Client()
    login_ok = c.login(username="superuser", password="secret")
    assert login_ok
    url = args[0]
    newargs = args[1:]
    if url.startswith(settings.BASE_URL):
        url_path = url[len(settings.BASE_URL) :]
    elif url.startswith("http"):
        raise RuntimeError(f"Don't know how to redirect {url}.")
    else:
        url_path = url

    ## Remove dummy auth token (we are already logged in as superuser)
    headers = kwargs.pop("headers", None)
    if (
        headers is not None
        and "Authorization" in headers
        and headers["Authorization"].startswith("Token ")
    ):
        del headers["Authorization"]

    if method == "GET":
        params = kwargs.pop("params")
        response = c.get(url_path, *newargs, data=params, headers=headers, **kwargs)
    elif method == "POST":
        json = kwargs.pop("json")
        response = c.post(
            url_path,
            *newargs,
            data=json,
            content_type="application/json",
            headers=headers,
            **kwargs,
        )
    else:
        raise ValueError(f"Method {method} not implemented.")
    return convert_to_requests_response(response, url_path)


class NKReportTest(NkReportTestCase):
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

    @patch("requests.post", wraps=redirect_post_request)
    @patch("requests.get", wraps=redirect_get_request)
    def test_report_minimal_dryrun(self, mock_get, mock_post):
        self.configure_test_report_minimal()

        log = main(self.report, dry_run=True)
        # print(log)
        self.assertTrue(log.startswith("Nebenkostenabrechung mit WARNUNGEN erstellt:"))
        self.assertIn("Ignoriere Kostenstelle, da keine Kosten definiert: Winterdienst", log)
        self.assertIn(
            "Keine Warmwasser-Messdaten vorhanden. Berechne KEINE Warmwasser-Grundkosten: 0000, 9998, 9999",
            log,
        )
        self.assertIn("Keine Messdaten für Objekt gefunden: 0000, 9998, 9999", log)
        self.assertIn("Objekt hat keine Gewichtung messung_warmwasser: 0000, 9998, 9999", log)
        self.assertIn("Objekt hat keine Gewichtung messung_heizung: 0000, 9998, 9999", log)
        self.assertIn("Objekt hat keine Gewichtung messung_wasser: 0000, 9998, 9999", log)
        self.assertIn(
            "In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.: 001a: 1200.0 -> 0.0",
            log,
        )
        self.assertIn(
            "In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.: 001b: 240.0 -> 0.0",
            log,
        )
        self.assertIn(
            "In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.: G001: 3600.0 -> 0.0",
            log,
        )
        self.assertIn(
            "In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.: G002: 1440.0 -> 0.0",
            log,
        )
        self.assertIn(
            "In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.: L001: 240.0 -> 0.0",
            log,
        )
        self.assertIn(
            "In Rechnung gestelltes NK-Akonto stimmt nicht mit NK-Akontosumme der Objekte überein. Skaliere Akonto pro Objekt entsprechend.: L002: 720.0 -> 0.0",
            log,
        )

        ## Check ReportOutput (Log + Abrechnung.csv + Rohdaten.json + Plots + Bills + Strom-Korrektur)
        # for rep in ReportOutput.objects.all():
        #    print(f" - {rep.name} {rep.group} {rep.output_type} {rep.value}")
        self.assertEqual(ReportOutput.objects.count(), 3)

        overview = ReportOutput.objects.get(name="NK-Abrechnung Übersicht")
        self.assertEqual(overview.group, "[A] Übersicht")
        self.assertEqual(overview.output_type, "csv")

        rawdata = ReportOutput.objects.get(name="NK-Abrechnung Rohdaten")
        self.assertEqual(rawdata.output_type, "json")
        self.assertEqual(ReportOutput.objects.get(name="Log").output_type, "text")

        ## Check output file(s)
        csvdiff = CompareCSV(
            overview.get_filename(), "report/tests/test_data/reference_overview_minimal.csv"
        ).compare()
        if csvdiff:
            pprint(csvdiff)
        # jsondiff = CompareJSON(
        #     rawdata.get_filename(), "report/tests/test_data/reference_rawdata_minimal.json"
        # ).compare()
        # if jsondiff:
        #     pprint(jsondiff)
        self.assertEqual(csvdiff, [])
        # self.assertEqual(jsondiff, [])

        ## Make sure not invoices were created
        self.assertEqual(Invoice.objects.count(), 0)

    @tag("slow-test")
    @patch("requests.post", wraps=redirect_post_request)
    @patch("requests.get", wraps=redirect_get_request)
    def test_report_minimal_fulloutput_dryrun(self, mock_get, mock_post):
        self.configure_test_report_minimal()

        self.update_field("Ausgabe:QR-Rechnungen", True)
        self.update_field("Ausgabe:Plots", True)
        log = main(self.report, dry_run=True)
        # print(log)
        self.assertTrue(log.startswith("Nebenkostenabrechung mit WARNUNGEN erstellt:"))

        ## Check ReportOutput (Log + Abrechnung.csv + Rohdaten.json + 12xPlots +6x Bills + Strom-Korrektur)
        # for rep in ReportOutput.objects.all():
        #    print(f" - {rep.name} {rep.group} {rep.output_type} {rep.value}")
        self.assertEqual(ReportOutput.objects.count(), 3 + 12 + 6)

        ## Check output file(s)
        # rawdata = ReportOutput.objects.get(name="NK-Abrechnung Rohdaten")
        # jsondiff = CompareJSON(
        #     rawdata.get_filename(), "report/tests/test_data/reference_rawdata_minimal.json"
        # ).compare()
        # if jsondiff:
        #     pprint(jsondiff)
        # self.assertEqual(jsondiff, [])

        ## Make sure not invoices were created
        self.assertEqual(Invoice.objects.count(), 0)

        ## Make sure tmp dir is removed
        self.assertTrue(os.path.exists(f"{settings.SMEDIA_ROOT}/report/{self.report.id}"))
        self.assertFalse(os.path.exists(f"{settings.SMEDIA_ROOT}/report/{self.report.id}/tmp"))

        self.assertPDFPages(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            5,
            accept_more_pages_than_expected=True,  # depending on the font etc. it could be more
        )
        self.assertInPDF(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            "<adr-line1>: Hans Muster1",
            on_page=1,
        )
        self.assertInPDF(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            "<betreff>: Nebenkostenabrechnung 01.07.2023 – 30.06.2024",
            on_page=1,
        )
        self.assertInPDF(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            "Rechnung 9999999999",
            on_page=1,
        )
        self.assertInPDF(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            "700 kWh",
            on_page=3,
        )

    @tag("slow-test")
    @patch("requests.post", wraps=redirect_post_request)
    @patch("requests.get", wraps=redirect_get_request)
    def test_report_minimal_fulloutput(self, mock_get, mock_post):
        self.configure_test_report_minimal()

        self.update_field("Ausgabe:QR-Rechnungen", True)
        log = main(self.report, dry_run=False)
        # print(log)
        self.assertTrue(log.startswith("Nebenkostenabrechung mit WARNUNGEN erstellt:"))

        ## Check output file(s)
        # rawdata = ReportOutput.objects.get(name="NK-Abrechnung Rohdaten")
        # jsondiff = CompareJSON(
        #     rawdata.get_filename(), "report/tests/test_data/reference_rawdata_minimal.json"
        # ).compare()
        # if jsondiff:
        #     pprint(jsondiff)
        # self.assertEqual(jsondiff, [])

        ## Check invoices
        self.assertEqual(Invoice.objects.count(), 6)
        invoice1 = Invoice.objects.get(contract=self.contracts[0])
        self.assertEqual(invoice1.amount, Decimal("54810.38"))
        self.assertEqual(invoice1.invoice_type, "Invoice")
        self.assertEqual(
            invoice1.invoice_category, InvoiceCategory.objects.get(name="Nebenkostenabrechnung")
        )

        self.assertInPDF(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            f"Rechnung {invoice1.id}",
            on_page=1,
        )

    def test_import_from_api(self):
        pass
