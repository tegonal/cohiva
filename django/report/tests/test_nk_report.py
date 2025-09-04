# import time
import os
from decimal import Decimal
from pprint import pprint
from unittest.mock import patch

from django.conf import settings
from django.test import Client

import report.tests.data as testdata
from geno.models import Invoice, InvoiceCategory
from report.models import Report, ReportInputData, ReportInputField, ReportOutput, ReportType
from report.report_nk import main
from report.tests.check_report_output import CompareCSV, CompareJSON

from .base import ReportTestCase


def redirect_get_request(*args, **kwargs):
    return redirect_request("GET", *args, **kwargs)


def redirect_post_request(*args, **kwargs):
    return redirect_request("POST", *args, **kwargs)


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
    return response


class NKReportTest(ReportTestCase):
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

    def configure_test_report_minimal(self):
        self.rtype = ReportType.objects.create(name="Nebenkostenabrechnung")
        self.report = Report.objects.create(name="Test", report_type=self.rtype)

        self.add_field("Startjahr", 2023)
        # self.add_field("Vorperiode:Bezeichnung", "2022/2023")
        # self.add_field("Vorperiode:Datei", "filer:26", "file")

        self.add_field("Ausgabe:LimitiereVertragsIDs", "", "json")
        # self.add_field("Ausgabe:LimitiereVertragsIDs", "[ 11 ]", "json")
        self.add_field("Ausgabe:QR-Rechnungen", False)
        self.add_field("Ausgabe:Plots", False)
        self.add_field("Vorlage:Abrechnung", f"filer:{self.filer_template_qrbill.id}", "file")
        self.add_field(
            "Vorlage:EmpfehlungAkonto", f"filer:{self.filer_template_akonto.id}", "file"
        )

        self.add_field("Kosten:Umgebung_Siedlung", 13075.0)
        self.add_field("Kosten:Winterdienst", 0.0)
        self.add_field("Kosten:Wasser_Abwasser", 31915.0)
        self.add_field("Kosten:Serviceabo Energiemessung", 4032.7)
        self.add_field("Kosten:Reinigung", 43875.95)
        self.add_field("Kosten:Lift", 8296.6)
        self.add_field("Kosten:Kehrichtgebuehren", 14957.15)
        self.add_field("Kosten:Hauswartung_ServiceHeizungLüftung", 8637.11)
        self.add_field("Kosten:Betriebskosten_Gemeinschaft", 3858.6)
        self.add_field("Verwaltungsaufwand:Faktor", 2.0)

        self.add_field("Messdaten:Wasserverbrauch", 8088.0)
        self.add_field(
            "Messdaten:Liegenschaft", f"filer:{self.filer_measurements_building.id}", "file"
        )
        self.add_field(
            "Messdaten:Mieteinheiten", f"filer:{self.filer_measurements_units.id}", "file"
        )

        self.add_field("Internet:Tarif:ProWohnung", 5.0)
        self.add_field("Internet:Tarif:ProPerson", 4.0)
        self.add_field("Internet:Tarif:Fix", "", "json")
        # self.add_field("Internet:Tarif:Fix", "{ "204": 0 }", "json")

        self.add_field("Strom:Tarif:Korrekturen", '{"mittel": 0.28, "nacht": 0.33}', "json")
        self.add_field("Strom:Tarif:HKN", 0.07)
        self.add_field(
            "Strom:Tarif:Einspeisevergütung",
            "[0.176, 0.176, 0.176, 0.176, 0.176, 0.176, 0.136, 0.136, 0.136, 0.136, 0.136, 0.136]",
            "json",
        )
        self.add_field("Strom:Tarif:Eigenstrom", 0.1453)
        # self.add_field("Strom:Korrekturen", "", "json")
        # self.add_field("Strom:Korrekturen", "{ "0000": [ {"desc": "Allgemeinstrom: Abzug für Betrieb Tiefkühlallmend", "tarif": "mittel", "kwh": [-63.50,-59.33,-65.36,-64.17,-57.15,-61.50,-57.69,-51.51,-55.73,-53.89,-61.53,-58.55]}, {"desc": "Allgemeinstrom: Abzug für Aussenlift", "tarif": "mittel", "kwh": [-40,-40,-40,-40,-40,-40,-40,-40,-40,-40,-40,-40]} ], "011": [ {"desc": "Strom von Whg. 011 für Aussenbeleuchtung Zufahrt", "tarif": "nacht", "kwh": [-57.57,-51.92,-58.88,-73.76,-937.21,-771.08,-33.91,-26.82,-686.17,-607.14,0,0]} ] }", "json")

    def add_field(self, name, data, field_type=None):
        if not field_type:
            if isinstance(data, bool):
                field_type = "bool"
            elif isinstance(data, int):
                field_type = "int"
            elif isinstance(data, float):
                field_type = "float"
            else:
                field_type = "char"
        inpt = ReportInputField.objects.create(
            name=name, report_type=self.rtype, field_type=field_type
        )
        ReportInputData.objects.create(name=inpt, report=self.report, value=data)

    def update_field(self, name, data):
        inpt = ReportInputField.objects.get(name=name, report_type=self.rtype)
        field = ReportInputData.objects.get(name=inpt, report=self.report)
        field.value = data
        field.save()

    @patch("requests.post", wraps=redirect_post_request)
    @patch("requests.get", wraps=redirect_get_request)
    def test_report_minimal_dryrun(self, mock_get, mock_post):
        self.configure_test_report_minimal()

        log = main(self.report, dry_run=True)
        # print(log)
        self.assertTrue(log.startswith("Nebenkostenabrechung mit WARNUNGEN erstellt:"))
        self.assertIn("Ignoriere Kostenstelle, da keine Kosten definiert: Winterdienst", log)
        self.assertIn(
            "Keine Warmwasser-Messdaten vorhanden. Berechne KEINE Warmwasser-Grundkosten: 0000, 9999",
            log,
        )
        self.assertIn("Keine Messdaten für Objekt gefunden: 0000, 9999", log)
        self.assertIn("Objekt hat keine Gewichtung messung_warmwasser: 0000, 9999", log)
        self.assertIn("Objekt hat keine Gewichtung messung_heizung: 0000, 9999", log)
        self.assertIn("Objekt hat keine Gewichtung messung_wasser: 0000, 9999", log)
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
        jsondiff = CompareJSON(
            rawdata.get_filename(), "report/tests/test_data/reference_rawdata_minimal.json"
        ).compare()
        if jsondiff:
            pprint(jsondiff)
        self.assertEqual(csvdiff, [])
        self.assertEqual(jsondiff, [])

        ## Make sure not invoices were created
        self.assertEqual(Invoice.objects.count(), 0)

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
        rawdata = ReportOutput.objects.get(name="NK-Abrechnung Rohdaten")
        jsondiff = CompareJSON(
            rawdata.get_filename(), "report/tests/test_data/reference_rawdata_minimal.json"
        ).compare()
        if jsondiff:
            pprint(jsondiff)
        self.assertEqual(jsondiff, [])

        ## Make sure not invoices were created
        self.assertEqual(Invoice.objects.count(), 0)

        ## Make sure tmp dir is removed
        self.assertTrue(os.path.exists(f"{settings.SMEDIA_ROOT}/report/{self.report.id}"))
        self.assertFalse(os.path.exists(f"{settings.SMEDIA_ROOT}/report/{self.report.id}/tmp"))

        self.assertPDFPages(
            f"{settings.SMEDIA_ROOT}/report/{self.report.id}/Nebenkosten-001a-{self.contracts[0].id}.pdf",
            5,
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

    @patch("requests.post", wraps=redirect_post_request)
    @patch("requests.get", wraps=redirect_get_request)
    def test_report_minimal_fulloutput(self, mock_get, mock_post):
        self.configure_test_report_minimal()

        self.update_field("Ausgabe:QR-Rechnungen", True)
        log = main(self.report, dry_run=False)
        # print(log)
        self.assertTrue(log.startswith("Nebenkostenabrechung mit WARNUNGEN erstellt:"))

        ## Check output file(s)
        rawdata = ReportOutput.objects.get(name="NK-Abrechnung Rohdaten")
        jsondiff = CompareJSON(
            rawdata.get_filename(), "report/tests/test_data/reference_rawdata_minimal.json"
        ).compare()
        if jsondiff:
            pprint(jsondiff)
        self.assertEqual(jsondiff, [])

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
