import json
from unittest.mock import patch

import geno.tests.data as geno_testdata
from geno.tests.base import BaseTestCase
from report.models import (
    Report,
    ReportConfiguration,
    ReportInputData,
    ReportInputField,
    ReportItem,
    ReportItemConfiguration,
)
from report.nk.cost.vewa import NkCostVEWACategories
from reservation.models import ReportType


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
    def configure_test_report_empty(self):
        self.report_config = ReportConfiguration.objects.create(
            name="Test Report Config",
            report_type="NK",
        )

        self.report_config.buildings.set([self.buildings[0]])
        self.report = Report.objects.create(name="Test", report_configuration=self.report_config)

        # Base settings of the report
        item = self._add_report_item("Test-Settings", "BaseSettings")
        self._add_input(item, "Startjahr", 2023)
        self._add_input(item, "Ausgabe:LimitiereVertragsIDs", "")
        # self._add_input(item, "Ausgabe:LimitiereVertragsIDs", "[ 11 ]", "json")
        # self._add_input(item, "Vorperiode:Bezeichnung", "2022/2023")
        # self._add_input(item, "Vorperiode:Datei", "filer:26", "file")
        self._add_input(item, "Ausgabe:QR-Rechnungen", False)
        self._add_input(item, "Ausgabe:Plots", False)
        self._add_input(item, "Vorlage:Abrechnung", f"filer:{self.filer_template_qrbill.id}")
        self._add_input(item, "Vorlage:EmpfehlungAkonto", f"filer:{self.filer_template_akonto.id}")

    def configure_test_report_wb_reference(self):
        self.configure_test_report_empty()

        item = self._add_report_item(
            "Hauswartung_ServiceHeizungLüftung",
            "Standard",
            "Hauswartung (Service, Heizung, Lüftung)",
        )
        self._add_input(item, "billing_group", "Hauswartung, Service Heizung/Lüftung")
        self._add_input(item, "Betrag", 8637.11)

        item = self._add_report_item("Reinigung", "Standard")
        self._add_input(item, "section_weights", "reinigung")
        self._add_input(item, "Betrag", 43875.95)

        item = self._add_report_item("Umgebung_Siedlung", "Standard", "Umgebung/Siedlungspflege")
        self._add_input(item, "billing_group", "Siedlung/Umgebungspflege")
        self._add_input(item, "Betrag", 13075.0)

        item = self._add_report_item(
            "Betriebskosten_Gemeinschaft", "Standard", "Betriebskosten Gemeinschaftsanlagen"
        )
        self._add_input(item, "billing_group", "Betriebskosten Gemeinschaftsanlagen")
        self._add_input(item, "Betrag", 3858.6)

        item = self._add_report_item("Winterdienst", "Standard")
        self._add_input(item, "Betrag", 0.0)

        item = self._add_report_item("Lift", "Standard")
        self._add_input(item, "Betrag", 8296.6)

        item = self._add_report_item("Kehrichtgebuehren", "Standard", "Kehrichtgebühren")
        self._add_input(item, "billing_group", "Kehrichtgebühren")
        self._add_input(item, "Betrag", 14957.15)

        item = self._add_report_item(
            "Fernwaerme_Warmwasser", "VEWA-MonthlyEGON", "Fernwärme: Warmwasser"
        )
        # "config": NkVEWACostConfig, => NkVEWACostConfigMonthlyEGON
        self._add_input(item, "billing_group", "Wärmekosten")
        self._add_input(item, "vewa_category", NkCostVEWACategories.HEAT_WATER.value)
        self._add_input(item, "base_cost_factor", 0.3)
        self._add_input(item, "exclude_zero_usage_units", True)
        self._add_input(item, "common_cost_section_weights", "wasser_allgemein")
        # Cost/Measurement data
        self._add_input(item, "Liegenschaft_file", f"filer:{self.filer_measurements_building.id}")
        self._add_input(item, "Liegenschaft_file_headers_month", "Monat")
        self._add_input(item, "Liegenschaft_file_headers_Kosten", "Fernwaerme_Warmwasser")
        self._add_input(item, "Mietobjekte_file", f"filer:{self.filer_measurements_units.id}")
        self._add_input(item, "Mietobjekte_file_prefix", "egon_Waerme")
        self._add_input(item, "Mietobjekte_file_headers_rental_unit", "Gebäudeeinheit")
        self._add_input(item, "Mietobjekte_file_headers_time_period", "Mieter Abrechnungsperiode")
        self._add_input(
            item, "Mietobjekte_file_headers_Verbrauch", "Warmwasser Verbrauch (Kubikmeter)"
        )

        item = self._add_report_item(
            "Fernwaerme_Fussboden", "VEWA-MonthlyEGON", "Fernwärme: Fussbodenheizung"
        )
        # "config": NkVEWACostConfig, => NkVEWACostConfigMonthlyEGON
        self._add_input(item, "billing_group", "Wärmekosten")
        self._add_input(item, "vewa_category", NkCostVEWACategories.HEAT_HEATING.value)
        self._add_input(item, "base_cost_factor", 0.3)
        self._add_input(item, "exclude_zero_usage_units", False)
        self._add_input(item, "section_weights", "nur_wohnen")
        self._add_input(item, "object_weights", "volume")
        # self._add_input(item, "common_cost_section_weights", "wasser_allgemein")
        # Cost/Measurement data
        self._add_input(item, "Liegenschaft_file", f"filer:{self.filer_measurements_building.id}")
        self._add_input(item, "Liegenschaft_file_headers_month", "Monat")
        self._add_input(item, "Liegenschaft_file_headers_Kosten", "Fernwaerme_Fussboden")
        self._add_input(item, "Mietobjekte_file", f"filer:{self.filer_measurements_units.id}")
        self._add_input(item, "Mietobjekte_file_prefix", "egon_Waerme")
        self._add_input(item, "Mietobjekte_file_headers_rental_unit", "Gebäudeeinheit")
        self._add_input(item, "Mietobjekte_file_headers_time_period", "Mieter Abrechnungsperiode")
        self._add_input(item, "Mietobjekte_file_headers_Verbrauch", "Wärmeverbrauch (kWh)")

        item = self._add_report_item(
            "Fernwaerme_Radiatoren", "VEWA-Monthly", "Fernwärme: Radiatoren"
        )
        # "config": NkVEWACostConfig, => NkVEWACostConfigMonthly
        self._add_input(item, "billing_group", "Wärmekosten")
        self._add_input(item, "vewa_category", NkCostVEWACategories.HEAT_HEATING.value)
        # self._add_input(item, "base_cost_factor", 0.3)
        # self._add_input(item, "exclude_zero_usage_units", False)
        self._add_input(item, "section_weights", "radiatoren")
        self._add_input(item, "object_weights", "volume")
        # self._add_input(item, "common_cost_section_weights", "wasser_allgemein")
        # Cost/Measurement data
        self._add_input(item, "Liegenschaft_file", f"filer:{self.filer_measurements_building.id}")
        self._add_input(item, "Liegenschaft_file_headers_month", "Monat")
        self._add_input(item, "Liegenschaft_file_headers_Kosten", "Fernwaerme_Radiatoren")

        item = self._add_report_item("Fernwaerme_Lueftung", "VEWA-Monthly", "Fernwärme: Lüftung")
        # "config": NkVEWACostConfig, => NkVEWACostConfigMonthly
        self._add_input(item, "billing_group", "Wärmekosten")
        self._add_input(item, "vewa_category", NkCostVEWACategories.HEAT_HEATING.value)
        # self._add_input(item, "base_cost_factor", 0.3)
        # self._add_input(item, "exclude_zero_usage_units", False)
        self._add_input(item, "section_weights", "lueftung")
        self._add_input(item, "object_weights", "volume")
        # self._add_input(item, "common_cost_section_weights", "wasser_allgemein")
        # Cost/Measurement data
        self._add_input(item, "Liegenschaft_file", f"filer:{self.filer_measurements_building.id}")
        self._add_input(item, "Liegenschaft_file_headers_month", "Monat")
        self._add_input(item, "Liegenschaft_file_headers_Kosten", "Fernwaerme_Lueftung")

        item = self._add_report_item("Wasser_Abwasser", "VEWA-AnnualEGON", "Wasser/Abwasser")
        # "config": NkVEWACostConfig, => NkVEWACostConfigAnnualEGON
        self._add_input(item, "billing_group", "Wasserkosten")
        self._add_input(item, "vewa_category", NkCostVEWACategories.WATER_GENERAL.value)
        self._add_input(item, "base_cost_factor", 0.3)
        self._add_input(item, "exclude_zero_usage_units", False)
        # self._add_input(item, "section_weights", "nur_wohnen")
        # self._add_input(item, "object_weights", "volume")
        self._add_input(item, "common_cost_section_weights", "wasser_allgemein")
        # Cost/Measurement data
        self._add_input(item, "Betrag", 31915.0)
        self._add_input(item, "Liegenschaft_usage_value", 8088.0)
        self._add_input(item, "Mietobjekte_file", f"filer:{self.filer_measurements_units.id}")
        self._add_input(item, "Mietobjekte_file_prefix", "egon_Waerme")
        self._add_input(item, "Mietobjekte_file_headers_rental_unit", "Gebäudeeinheit")
        self._add_input(item, "Mietobjekte_file_headers_time_period", "Mieter Abrechnungsperiode")
        self._add_input(
            item, "Mietobjekte_file_headers_Verbrauch", "Warmwasser Verbrauch (Kubikmeter)"
        )

        item = self._add_report_item("Strom_Total", "ZEV_Stromallmend", "Stromkosten")
        korrekturen = {
            "allg": [
                {
                    "desc": "Allgemeinstrom: Abzug separat verrechneter Strom",
                    "tarif": "mittel",
                    "kwh": 12 * [-2],
                },
                {
                    "desc": "Umbuchung: Allgemein verwendeter Strom von 001b",
                    "tarif": "mittel",
                    "kwh": 12 * [1],
                },
            ],
            "001b": [
                {
                    "desc": "Umbuchung: Allgemein verwendeter Strom von 001b",
                    "tarif": "mittel",
                    "kwh": 12 * [-1],
                }
            ],
        }
        # "config": NkVEWACostConfig, => NkZEVStromallmendCostConfig
        self._add_input(item, "billing_group", "Stromkosten")
        self._add_input(item, "tarif_eigenstrom", 0.1453)
        self._add_input(
            item,
            "tarif_einspeiseverguetung",
            "[0.176, 0.176, 0.176, 0.176, 0.176, 0.176, 0.136, 0.136, 0.136, 0.136, 0.136, 0.136]",
        )
        self._add_input(item, "tarif_hkn", 0.07)
        self._add_input(item, "tarif_korrekturen", '{"mittel": 0.28, "nacht": 0.33}')
        self._add_input(item, "korrekturen", json.dumps(korrekturen))
        # self._add_input(item, "section_weights", "nur_wohnen")
        # self._add_input(item, "object_weights", "volume")
        # self._add_input(item, "common_cost_section_weights", "wasser_allgemein")
        # Cost/Measurement data
        self._add_input(item, "Liegenschaft_file", f"filer:{self.filer_measurements_building.id}")
        self._add_input(item, "Liegenschaft_file_headers_month", "Monat")
        self._add_input(item, "Liegenschaft_file_headers_strom_bezug_zev", "Strom_kwh_egon")
        self._add_input(
            item, "Liegenschaft_file_headers_strom_ruecklieferung_ew", "Strom_kwh_ruecklieferung"
        )
        self._add_input(item, "Mietobjekte_file", f"filer:{self.filer_measurements_units.id}")
        self._add_input(item, "Mietobjekte_file_prefix", "egon_Strom")
        self._add_input(item, "Mietobjekte_file_headers_rental_unit", "Gebäudeeinheit")
        self._add_input(item, "Mietobjekte_file_headers_time_period", "Mieter Abrechnungsperiode")
        self._add_input(
            item, "Mietobjekte_file_headers_strom_ew_nieder", "Strombezug Niedertarif(kWh)"
        )
        self._add_input(
            item, "Mietobjekte_file_headers_strom_ew_hoch", "Strombezug Hochtarif EW (kWh)"
        )
        self._add_input(item, "Mietobjekte_file_headers_strom_solar", "Solarstrom (kWh)")
        self._add_input(
            item, "Mietobjekte_file_headers_chf_netz_nieder", "Strombezug Niedertarif(CHF)"
        )
        self._add_input(item, "Mietobjekte_file_headers_chf_netz_hoch", "Strombezug EW (CHF)")

        item = self._add_report_item("Serviceabo Energiemessung", "Standard")
        self._add_input(item, "Betrag", 4032.7)

        item = self._add_report_item("Internet/WLAN", "PerRentalUnit")
        self._add_input(item, "fee_per_unit", 5.0)
        self._add_input(item, "fee_per_person", 4.0)
        self._add_input(item, "fixed_fees", "")
        # self._add_input(item, "fixed_fees", '{ "204": 0 }')

        item = self._add_report_item("Verwaltungsaufwand", "Verwaltungsaufwand")
        self._add_input(item, "adminfee_percentage", 2.0)

    def _add_report_item(self, name, category, bezeichnung=None):
        if bezeichnung is None:
            bezeichnung = name
        item_config = ReportItemConfiguration.objects.create(
            name=name, item_category=category, report_configuration=self.report_config
        )
        item = ReportItem.objects.create(
            name=bezeichnung, item_category=category, report=self.report
        )
        return [item, item_config]

    def _add_input(self, item, name, data):
        input_field = ReportInputField.objects.get(name=name, item_configuration=item[1])
        # print(f"Add input field {item[1]}: {name} [{input_field.field_type}]")
        ReportInputData.objects.create(
            name=input_field,
            report=self.report,
            field_type=input_field.field_type,
            item=item[0],
            value=data,
        )

    def update_input(self, item_name, field_name, data, item_bezeichnung=None):
        if item_bezeichnung is None:
            item_bezeichnung = item_name
        item = ReportItem.objects.get(name=item_bezeichnung, report=self.report)
        item_config = ReportItemConfiguration.objects.get(
            name=item_name, report_configuration=self.report_config
        )
        input_field = ReportInputField.objects.get(name=field_name, item_configuration=item_config)
        # print(f"Update input field {item_config}: {field_name} [{input_field.field_type}]")
        field = ReportInputData.objects.get(name=input_field, report=self.report, item=item)
        field.value = data
        field.save()

    #####################################################################
    ## Below is code for old tests, that will be removed in the future ##
    #####################################################################
    def configure_test_report_minimal(self, legacy=False):
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
        self.add_field("VEWA:Grundkostenanteil", 0.3)
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
        if not legacy:
            korrekturen = {
                # OLD Name: "0000": [
                "allg": [
                    {
                        "desc": "Allgemeinstrom: Abzug separat verrechneter Strom",
                        "tarif": "mittel",
                        "kwh": 12 * [-2],
                    },
                    {
                        "desc": "Umbuchung: Allgemein verwendeter Strom von 001b",
                        "tarif": "mittel",
                        "kwh": 12 * [1],
                    },
                ],
                "001b": [
                    {
                        "desc": "Umbuchung: Allgemein verwendeter Strom von 001b",
                        "tarif": "mittel",
                        "kwh": 12 * [-1],
                    }
                ],
            }
            self.add_field("Strom:Korrekturen", json.dumps(korrekturen), "json")

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

    # Add string(s) to array in return_value to simulate an error
    @patch("report.nk.bill.create_qrbill", return_value=([], -1, None))
    @patch("report.nk.bill.render_qrbill")
    @patch(
        "report.nk.bill.NkBill._create_rental_unit_files",
        return_value={"odt_file": "dummy.odt", "graph_files": []},
    )
    @patch("report.nk.bill.NkBill._create_final_pdf")
    @patch("report.nk.generator.NkReportGenerator.add_output_to_report")
    def generate_with_mock_output(
        self,
        report,
        mock_add_output_to_report,
        mock_create_final_pdf,
        mock_create_rental_unit_files,
        mock_render_qrbill,
        mock_create_qrbill,
    ):
        report.generate()
        # print("DEBUG: create_qrbill.call_count: ", mock_create_qrbill.call_count)
        # print("DEBUG: create_qrbill.call_args: ", mock_create_qrbill.call_args)
        # print("DEBUG: render_qrbill.call_count: ", mock_render_qrbill.call_count)
        # print("DEBUG: render_qrbill.call_args: ", mock_render_qrbill.call_args)
        # print(
        #     "DEBUG: create_rental_unit_files.call_count: ",
        #     mock_create_rental_unit_files.call_count,
        # )
        # print(
        #     "DEBUG: create_rental_unit_files.call_args: ", mock_create_rental_unit_files.call_args
        # )
        # print("DEBUG: create_final_pdf.call_count: ", mock_create_final_pdf.call_count)
        # print("DEBUG: create_final_pdf.call_args: ", mock_create_final_pdf.call_args)
        # print("DEBUG: add_output_to_report.call_count: ", mock_add_output_to_report.call_count)
        # print("DEBUG: add_output_to_report.call_args: ", mock_add_output_to_report.call_args)
        return {
            "create_qrbill": mock_create_qrbill,
            "render_qrbill": mock_render_qrbill,
            "create_rental_unit_files": mock_create_rental_unit_files,
            "create_final_pdf": mock_create_final_pdf,
            "add_output_to_report": mock_add_output_to_report,
        }
