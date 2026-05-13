from django.test import TestCase

from report.models import ReportConfiguration, ReportInputField, ReportItemConfiguration


class ReportItemConfigurationBaseDataTest(TestCase):
    def setUp(self):
        self.report_configuration = ReportConfiguration.objects.create(
            name="Test Config",
            report_type="NK",
        )

    def test_creates_base_input_fields_on_create(self):
        item = ReportItemConfiguration.objects.create(
            name="Wasser_Abwasser",
            item_category="NkCostVEWA",
            report_configuration=self.report_configuration,
        )

        field_names = set(
            ReportInputField.objects.filter(item_configuration=item).values_list("name", flat=True)
        )

        self.assertSetEqual(
            field_names,
            {
                "Wasser_Abwasser:Grundkostenanteil",
                "Messdaten:Liegenschaft",
                "Messdaten:Mieteinheiten",
            },
        )

    def test_creates_base_input_fields_when_item_category_changes(self):
        item = ReportItemConfiguration.objects.create(
            name="Internet/WLAN",
            item_category="NkTotalCost",
            report_configuration=self.report_configuration,
        )

        # Custom fields are preserved; only missing base fields are added for the new category.
        ReportInputField.objects.create(
            name="Custom:Value",
            description="",
            item_configuration=item,
            field_type="char",
            active=True,
            value_default="",
        )

        item.item_category = "NkPerRentalUnitCost"
        item.save()

        field_names = set(
            ReportInputField.objects.filter(item_configuration=item).values_list("name", flat=True)
        )

        self.assertIn("Kosten:Internet/WLAN", field_names)
        self.assertIn("Internet/WLAN:Tarif:ProWohnung", field_names)
        self.assertIn("Internet/WLAN:Tarif:ProPerson", field_names)
        self.assertIn("Internet/WLAN:Tarif:Fix", field_names)
        self.assertIn("Custom:Value", field_names)

