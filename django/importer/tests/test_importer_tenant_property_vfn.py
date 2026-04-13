"""
Tests for the VFN Building/RentalUnit importer.
"""

from io import BytesIO

import openpyxl
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from geno.models import Building, RentalUnit
from importer.importer_tenant_property_vfn import ImporterTenantPropertyVFN
from importer.models import ImportJob

User = get_user_model()

HEADERS = [
    "Liegenschaft ID",
    "Liegenschaft Name",
    "Strasse",
    "PLZ",
    "Ort",
    "EGID",
    "Einheit ID",
    "Einheit Nummer",
    "Einheit Bezeichnung",
    "Typ",
    "Etage",
    "Zimmer",
    "Fläche",
    "NK Akonto",
    "Nettomiete",
    "EWID",
]


class ImporterTenantPropertyVFNTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

    def create_test_excel(self, rows):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.append(HEADERS)
        for row in rows:
            worksheet.append(row)
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        return SimpleUploadedFile(
            "test_buildings.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def make_row(self, **kwargs):
        defaults = {h: "" for h in HEADERS}
        defaults.update(kwargs)
        return [defaults[h] for h in HEADERS]

    # ------------------------------------------------------------------
    # Building + RentalUnit creation
    # ------------------------------------------------------------------

    def test_import_building_and_rental_unit(self):
        """Import creates a Building and a RentalUnit."""
        row = self.make_row(
            **{
                "Liegenschaft ID": "10",
                "Liegenschaft Name": "Musterweg 1",
                "Strasse": "Musterweg 1",
                "PLZ": "3011",
                "Ort": "Bern",
                "EGID": "12345",
                "Einheit ID": "201",
                "Einheit Nummer": "101",
                "Einheit Bezeichnung": "Wohnung Erdgeschoss",
                "Typ": "Wohnung",
                "Etage": "EG",
                "Zimmer": "3.5",
                "Fläche": "85.5",
                "NK Akonto": "150",
                "Nettomiete": "1200",
                "EWID": "5001",
            }
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file, import_type="tenant_property_vfn")
        results = ImporterTenantPropertyVFN(import_job).process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        building = Building.objects.get(name="Musterweg 1")
        self.assertEqual(building.street_name, "Musterweg")
        self.assertEqual(building.house_number, "1")
        self.assertEqual(building.city_zipcode, "3011")
        self.assertEqual(building.city_name, "Bern")
        self.assertEqual(building.egid, 12345)

        unit = RentalUnit.objects.get(name="101", building=building)
        self.assertEqual(unit.label, "Wohnung Erdgeschoss")
        self.assertEqual(unit.rental_type, "Wohnung")
        self.assertEqual(unit.floor, "EG")
        self.assertEqual(float(unit.rooms), 3.5)
        self.assertEqual(float(unit.area), 85.5)
        self.assertEqual(float(unit.nk), 150)
        self.assertEqual(float(unit.rent_netto), 1200)
        self.assertEqual(unit.ewid, 5001)
        self.assertEqual(unit.import_id, f"vfn_{import_job.id}_201")

    def test_multiple_units_same_building(self):
        """Multiple rows sharing a building name reuse the same Building object."""
        rows = [
            self.make_row(
                **{
                    "Liegenschaft ID": "10",
                    "Liegenschaft Name": "Testhaus",
                    "Strasse": "Testweg 5",
                    "PLZ": "8000",
                    "Ort": "Zürich",
                    "Einheit ID": "301",
                    "Einheit Nummer": "201",
                    "Einheit Bezeichnung": "EG links",
                    "Typ": "Wohnung",
                    "Fläche": "70",
                    "Nettomiete": "1100",
                }
            ),
            self.make_row(
                **{
                    "Liegenschaft ID": "10",
                    "Liegenschaft Name": "Testhaus",
                    "Strasse": "Testweg 5",
                    "PLZ": "8000",
                    "Ort": "Zürich",
                    "Einheit ID": "302",
                    "Einheit Nummer": "202",
                    "Einheit Bezeichnung": "EG rechts",
                    "Typ": "Wohnung",
                    "Fläche": "65",
                    "Nettomiete": "1050",
                }
            ),
        ]
        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterTenantPropertyVFN(import_job).process()

        self.assertEqual(results["success_count"], 2)
        self.assertEqual(Building.objects.filter(name="Testhaus").count(), 1)
        self.assertEqual(RentalUnit.objects.filter(building__name="Testhaus").count(), 2)

    def test_rental_type_mapping(self):
        """Rental type aliases are resolved correctly."""
        rows = [
            self.make_row(
                **{
                    "Liegenschaft ID": "20",
                    "Liegenschaft Name": "Alias Test",
                    "Einheit ID": "401",
                    "Einheit Nummer": "H01",
                    "Typ": "Hobbyraum",
                }
            ),
            self.make_row(
                **{
                    "Liegenschaft ID": "20",
                    "Liegenschaft Name": "Alias Test",
                    "Einheit ID": "402",
                    "Einheit Nummer": "P01",
                    "Typ": "Abstellplatz",
                }
            ),
            self.make_row(
                **{
                    "Liegenschaft ID": "20",
                    "Liegenschaft Name": "Alias Test",
                    "Einheit ID": "403",
                    "Einheit Nummer": "Z01",
                    "Typ": "Zimmer",
                }
            ),
            self.make_row(
                **{
                    "Liegenschaft ID": "20",
                    "Liegenschaft Name": "Alias Test",
                    "Einheit ID": "404",
                    "Einheit Nummer": "U01",
                    "Typ": "UnbekanntTyp",
                }
            ),
        ]
        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(file=excel_file)
        ImporterTenantPropertyVFN(import_job).process()

        self.assertEqual(RentalUnit.objects.get(name="H01").rental_type, "Hobby")
        self.assertEqual(RentalUnit.objects.get(name="P01").rental_type, "Parkplatz")
        self.assertEqual(RentalUnit.objects.get(name="Z01").rental_type, "Jokerzimmer")
        self.assertEqual(RentalUnit.objects.get(name="U01").rental_type, "Wohnung")

    def test_prevent_duplicate_without_override(self):
        """Re-importing same Einheit ID without override raises an error."""
        row = self.make_row(
            **{
                "Liegenschaft ID": "30",
                "Liegenschaft Name": "DupBuilding",
                "Einheit ID": "501",
                "Einheit Nummer": "A01",
                "Typ": "Wohnung",
            }
        )
        excel_file1 = self.create_test_excel([row])
        job1 = ImportJob.objects.create(file=excel_file1)
        ImporterTenantPropertyVFN(job1).process()

        excel_file2 = self.create_test_excel([row])
        job2 = ImportJob.objects.create(file=excel_file2, override_existing=False)
        results = ImporterTenantPropertyVFN(job2).process()

        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 0)

    def test_override_existing_updates_unit(self):
        """With override_existing=True, existing rental unit is updated."""
        row = self.make_row(
            **{
                "Liegenschaft ID": "40",
                "Liegenschaft Name": "UpdateBuilding",
                "Einheit ID": "601",
                "Einheit Nummer": "B01",
                "Typ": "Wohnung",
                "Fläche": "60",
                "Nettomiete": "900",
            }
        )
        excel_file1 = self.create_test_excel([row])
        job1 = ImportJob.objects.create(file=excel_file1)
        ImporterTenantPropertyVFN(job1).process()

        row_updated = self.make_row(
            **{
                "Liegenschaft ID": "40",
                "Liegenschaft Name": "UpdateBuilding",
                "Einheit ID": "601",
                "Einheit Nummer": "B01",
                "Typ": "Wohnung",
                "Fläche": "75",
                "Nettomiete": "1100",
            }
        )
        excel_file2 = self.create_test_excel([row_updated])
        job2 = ImportJob.objects.create(file=excel_file2, override_existing=True)
        results = ImporterTenantPropertyVFN(job2).process()

        self.assertEqual(results["success_count"], 1)
        unit = RentalUnit.objects.get(name="B01", building__name="UpdateBuilding")
        self.assertEqual(float(unit.area), 75)
        self.assertEqual(float(unit.rent_netto), 1100)

    def test_missing_building_name_fails(self):
        """Row without Liegenschaft Name fails validation."""
        row = self.make_row(**{"Einheit ID": "700", "Einheit Nummer": "X01"})
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterTenantPropertyVFN(import_job).process()

        self.assertEqual(results["error_count"], 1)

    def test_missing_unit_number_fails(self):
        """Row without Einheit Nummer fails validation."""
        row = self.make_row(**{"Liegenschaft ID": "50", "Liegenschaft Name": "NoUnit"})
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterTenantPropertyVFN(import_job).process()

        self.assertEqual(results["error_count"], 1)

    def test_import_type_registered_in_model(self):
        """The import type 'tenant_property_vfn' is a valid ImportJob choice."""
        valid_types = [c[0] for c in ImportJob.IMPORT_TYPE_CHOICES]
        self.assertIn("tenant_property_vfn", valid_types)
