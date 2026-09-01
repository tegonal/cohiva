from django_test_migrations.contrib.unittest_case import MigratorTestCase


class TestMigration0027(MigratorTestCase):
    migrate_from = ("geno", "0026_convert_uuids_from_char")
    migrate_to = ("geno", "0027_alter_documenttype_template_to_m2m")

    def prepare(self):
        """Prepare some data before the migration."""
        template_model = self.old_state.apps.get_model("geno", "ContentTemplate")
        doctype_model = self.old_state.apps.get_model("geno", "DocumentType")
        template = template_model.objects.create(name="Test-template")
        doctype_model.objects.create(name="test", template=template)

    def test_migration(self):
        """Verify that existing templates are migrated."""
        doctype = self.new_state.apps.get_model("geno", "DocumentType")
        obj = doctype.objects.get(name="test")
        self.assertEqual(obj.templates.count(), 1)
        self.assertEqual(obj.templates.first().name, "Test-template")


class TestMigration0027Reverse(MigratorTestCase):
    migrate_to = ("geno", "0026_convert_uuids_from_char")
    migrate_from = ("geno", "0027_alter_documenttype_template_to_m2m")

    def prepare(self):
        """Prepare some data before the migration."""
        template_model = self.old_state.apps.get_model("geno", "ContentTemplate")
        doctype_model = self.old_state.apps.get_model("geno", "DocumentType")
        template1 = template_model.objects.create(name="Test-template1")
        template2 = template_model.objects.create(name="Test-template2")
        doctype = doctype_model.objects.create(name="test-reverse")
        doctype.templates.set([template1, template2])

    def test_migration(self):
        """Verify that existing templates are migrated (reverse)."""
        doctype_model = self.new_state.apps.get_model("geno", "DocumentType")
        obj = doctype_model.objects.get(name="test-reverse")
        self.assertEqual(obj.template.name, "Test-template1")
