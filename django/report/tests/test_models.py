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
            item_category="VEWA-Annual",
            report_configuration=self.report_configuration,
        )

        field_names = set(
            ReportInputField.objects.filter(item_configuration=item).values_list("name", flat=True)
        )

        self.assertSetEqual(
            field_names,
            {
                # NkCostConfig
                "billing_group",
                "monthly_weights",
                "section_weights",
                # NkTotalCostConfig
                "object_weights",
                "Betrag",
                # NkVEWACostConfig
                "vewa_category",
                "base_cost_factor",
                "exclude_zero_usage_units",
                "common_cost_section_weights",
                # NkVEWACostConfigAnnual
                "Liegenschaft_usage_value",
            },
        )

    def test_creates_base_input_fields_when_item_category_changes(self):
        item = ReportItemConfiguration.objects.create(
            name="Internet/WLAN",
            item_category="Standard",
            report_configuration=self.report_configuration,
        )
        test_field = ReportInputField.objects.get(name="billing_group", item_configuration=item)
        test_field.value_default = "test_default_value"
        test_field.save()

        field_names = set(
            ReportInputField.objects.filter(item_configuration=item).values_list("name", flat=True)
        )
        # NkCostConfig
        self.assertIn("billing_group", field_names)
        # NkTotalCostConfig
        self.assertIn("Betrag", field_names)

        # Custom fields are preserved; only missing base fields are added for the new category,
        # and the fields from the old category that don't exist in the new one are deleted.
        ReportInputField.objects.create(
            name="Custom:Value",
            description="",
            item_configuration=item,
            field_type="char",
            active=True,
            value_default="",
        )

        item.item_category = "PerRentalUnit"
        item.save()

        field_names = set(
            ReportInputField.objects.filter(item_configuration=item).values_list("name", flat=True)
        )

        # NkCostConfig: Field in both old and new category should still exist
        self.assertIn("billing_group", field_names)
        ## billing_group should still have the default value set before the category change
        test_field = ReportInputField.objects.get(name="billing_group", item_configuration=item)
        self.assertEqual(test_field.value_default, "test_default_value")

        # NkTotalCostConfig => Betrag should have been deleted since it's in the old but not the new category.
        self.assertNotIn("Betrag", field_names)

        # NkPerRentalUnitCostConfig: The new fields of the new category
        self.assertIn("fee_per_unit", field_names)
        self.assertIn("fee_per_person", field_names)
        self.assertIn("fixed_fees", field_names)

        # Custom test: Field that does not belong to the old or new category
        self.assertIn("Custom:Value", field_names)
