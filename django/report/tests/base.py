import geno.tests.data as geno_testdata
from geno.tests.base import BaseTestCase
from report.models import Report, ReportInputData, ReportInputField, ReportType


class ReportTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Set up data for the whole TestCase
        # geno_testdata.create_members(cls)
        # geno_testdata.create_shares(cls)
        geno_testdata.create_users(cls)
        geno_testdata.create_templates(cls)
        geno_testdata.create_documenttypes(cls)
        geno_testdata.create_invoicecategories(cls)
        # reservation_testdata.create_reservationobjects(cls)

    # def setUp(self):
    #    self.client.login(username='superuser', password='secret')


class NkReportTestCase(ReportTestCase):
    def configure_test_report_minimal(self):
        self.rtype = ReportType.objects.create(name="Nebenkostenabrechnung")
        self.report = Report.objects.create(name="Test", report_type=self.rtype)

        self.add_field("Startjahr", 2023)
        # self.add_field("Vorperiode:Bezeichnung", "2022/2023")
        # self.add_field("Vorperiode:Datei", "filer:26", "file")

        self.add_field("Liegenschaften", f"['{self.buildings[0].id}', '{self.buildings[1].id}']")

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
