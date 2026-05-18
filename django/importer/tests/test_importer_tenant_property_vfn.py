"""
Tests for the VFN Building/RentalUnit importer.
"""

import datetime
from decimal import Decimal
from io import BytesIO

import openpyxl
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from geno.models import Address, Building, RentalUnit
from importer.importer_tenant_property_vfn import ImporterTenantPropertyVFN
from importer.models import ImportJob

User = get_user_model()

HEADERS_BUILDINGS = [
    "Name der Liegenschaft",
    "Beschreibung",
    "Strasse",
    "Hausnummer",
    "PLZ",
    "Ort",
    "Land",
    "Gebäudeversicherungswert (Fr.)",
    "Anlagekosten (Fr.)",
    "EGID",
]

HEADERS_RENTAL_UNITS = [
    "Liegenschaft",
    "Typ",
    "Nr.",
    "Bezeichnung",
    "Stockwerk",
    "Anzahl Zimmer",
    "Mindestbelegung",
    "Fläche (m²)",
    "Balkonfläche (m²)",
    "Zusatzfläche (m²)",
    "Raumhöhe (m)",
    "Volumen (m³)",
    "Zahlungsperiodizität (Monate)",
    "Nebenkosten akonto (CHF/Periode)",
    # "Nebenkosten pauschal (CHF/Mt.)",
    "Nebenkosten pauschal (CHF/Periode)",
    "Strompauschale (CHF/Periode)",
    # "Nettomiete (CHF/Mt.)",
    "Nettomiete (CHF/Periode)",
    "Mietzinsdepot (CHF)",
    "Anteilskapital (CHF)",
    "Zusatzinfo",
    "Status",
    "EWID",
    "Interne Nr.",
    "Beschreibung",
    "ADIT-Nr.",
    "Import-ID",
    "Import-ID 1 Mieter*in (Person)",
    "Import-ID 2 Mieter*in (Person)",
    "Bemerkungen Mietvertrag",
    "Vertragsbeginn",
]


class ImporterTenantPropertyVFNTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

    def create_test_excel(self, building_rows, rental_unit_rows):
        workbook = openpyxl.Workbook()
        ws_buildings = workbook.active
        ws_buildings.title = "Liegenschaften"
        ws_buildings.append(HEADERS_BUILDINGS)
        for row in building_rows:
            ws_buildings.append(row)
        ws_rental_units = workbook.create_sheet("Mietobjekte")
        ws_rental_units.append(HEADERS_RENTAL_UNITS)
        for row in rental_unit_rows:
            ws_rental_units.append(row)
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        return SimpleUploadedFile(
            "test_buildings.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def make_row(self, headers, **kwargs):
        defaults = {h: "" for h in headers}
        defaults.update(kwargs)
        return [defaults[h] for h in headers]

    def test_import_building_and_rental_unit_and_contract(self):
        """Import creates a Building, a RentalUnit and a Contract."""
        address01 = Address.objects.create(name="Test 01", import_id="vfn_01")
        results = self._run_import()

        self.assertEqual(results["success_count"], 2)
        self.assertEqual(results["error_count"], 0)

        building = Building.objects.get(name="Musterweg 1")
        self.assertEqual(building.street_name, "Musterweg")
        self.assertEqual(building.house_number, "1")
        self.assertEqual(building.city_zipcode, "3011")
        self.assertEqual(building.city_name, "Bern")
        self.assertEqual(building.egid, 12345)
        self.assertEqual(building.value_insurance, Decimal("2500000.00"))
        self.assertEqual(building.value_build, Decimal("1950000.00"))

        unit = RentalUnit.objects.get(name="101", building=building)
        self.assertEqual(unit.label, "Wohnung Erdgeschoss")
        self.assertEqual(unit.rental_type, "Wohnung")
        self.assertEqual(unit.floor, "EG")
        self.assertEqual(float(unit.rooms), 3.5)
        self.assertEqual(unit.min_occupancy, Decimal("2"))
        self.assertEqual(float(unit.area), 85.5)
        self.assertEqual(unit.billing_period, Decimal("1"))
        self.assertEqual(float(unit.nk), 150)
        self.assertEqual(float(unit.rent_netto), 1200)
        self.assertEqual(unit.depot, Decimal("2400"))
        self.assertEqual(unit.share, Decimal("15000"))
        self.assertEqual(unit.note, "Test Zusatzinfo")
        self.assertEqual(unit.ewid, 5001)
        self.assertEqual(unit.import_id, "vfn_Musterweg1-101")

        self.assertEqual(unit.rentalunit_contracts.count(), 1)
        contract = unit.rentalunit_contracts.first()
        self.assertEqual(contract.contractors.count(), 1)
        self.assertEqual(contract.contractors.first(), address01)
        self.assertEqual(contract.date, datetime.date(2020, 1, 1))
        self.assertEqual(contract.note, "Test Bemerkung Mietvertrag")

    def test_import_building_and_rental_unit_and_contract_with_two_addresses(self):
        """Import creates a Building, a RentalUnit and a Contract."""
        address01 = Address.objects.create(name="Test 01", import_id="vfn_01")
        address02 = Address.objects.create(name="Test 02", import_id="vfn_02")
        row_ru = self.make_row(
            HEADERS_RENTAL_UNITS,
            **{
                "Liegenschaft": "Musterweg 1",
                "Typ": "Wohnung",
                "Nr.": "101",
                "Import-ID": "Musterweg1-101",
                "Import-ID 1 Mieter*in (Person)": "01",
                "Import-ID 2 Mieter*in (Person)": "02",
            },
        )
        results = self._run_import(rows_ru=[row_ru])

        self.assertEqual(results["success_count"], 2)
        self.assertEqual(results["error_count"], 0)

        building = Building.objects.get(name="Musterweg 1")
        unit = RentalUnit.objects.get(name="101", building=building)
        self.assertEqual(unit.rentalunit_contracts.count(), 1)
        contract = unit.rentalunit_contracts.first()
        self.assertEqual(contract.contractors.count(), 2)
        contractors = contract.contractors.all()
        self.assertIn(address01, contractors)
        self.assertIn(address02, contractors)
        self.assertEqual(contract.date, datetime.date.today())

    def test_multiple_units_same_building(self):
        """Multiple rows sharing a building name reuse the same Building object."""
        rows = [
            self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Nr.": "301",
                    "Typ": "Wohnung",
                },
            ),
            self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Nr.": "302",
                    "Typ": "Wohnung",
                },
            ),
        ]
        results = self._run_import(rows_ru=rows)

        self.assertEqual(results["success_count"], 3)
        self.assertEqual(Building.objects.filter(name="Musterweg 1").count(), 1)
        self.assertEqual(RentalUnit.objects.filter(building__name="Musterweg 1").count(), 2)

    def test_rental_type_mapping(self):
        """Rental type aliases are resolved correctly."""
        rows = [
            self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Nr.": "H01",
                    "Typ": "Raum / Atelier",
                },
            ),
            self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Nr.": "P01",
                    "Typ": "Stellplatz",
                },
            ),
            self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Nr.": "Z01",
                    "Typ": "Jokerzimmer",
                },
            ),
            self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Nr.": "U01",
                    "Typ": "UnbekanntTyp",
                },
            ),
        ]
        self._run_import(rows_ru=rows)

        self.assertEqual(RentalUnit.objects.get(name="H01").rental_type, "Hobby")
        self.assertEqual(RentalUnit.objects.get(name="P01").rental_type, "Parkplatz")
        self.assertEqual(RentalUnit.objects.get(name="Z01").rental_type, "Zimmer")
        self.assertEqual(RentalUnit.objects.get(name="U01").rental_type, "Wohnung")

    def test_prevent_duplicate_without_override(self):
        """Re-importing same Unit or Building ID without override raises an error."""
        row = self.make_row(
            HEADERS_RENTAL_UNITS,
            **{
                "Liegenschaft": "Musterweg 1",
                "Nr.": "101",
                "Typ": "Wohnung",
                "Import-ID": "Musterweg1-101",
            },
        )
        self._run_import(rows_ru=[row])

        results = self._run_import(rows_ru=[row], override_existing=False)

        self.assertEqual(results["error_count"], 2)
        self.assertEqual(results["success_count"], 0)

    def test_override_existing_updates_unit(self):
        """With override_existing=True, existing rental unit is updated."""
        row = self.make_row(
            HEADERS_RENTAL_UNITS,
            **{
                "Liegenschaft": "Musterweg 1",
                "Nr.": "101",
                "Typ": "Wohnung",
                "Import-ID": "Musterweg1-101",
                "Fläche (m²)": "60",
                "Nettomiete (CHF/Periode)": "900",
            },
        )
        self._run_import(rows_ru=[row])

        row_updated = self.make_row(
            HEADERS_RENTAL_UNITS,
            **{
                "Liegenschaft": "Musterweg 1",
                "Nr.": "101",
                "Typ": "Wohnung",
                "Import-ID": "Musterweg1-101",
                "Fläche (m²)": "75",
                "Nettomiete (CHF/Periode)": "1100",
            },
        )
        results = self._run_import(rows_ru=[row_updated], override_existing=True)

        self.assertEqual(results["success_count"], 2)
        unit = RentalUnit.objects.get(name="101", building__name="Musterweg 1")
        self.assertEqual(float(unit.area), 75)
        self.assertEqual(float(unit.rent_netto), 1100)

    def test_missing_building_name_fails(self):
        """Row without Liegenschaft Name fails validation."""
        row = self.make_row(
            HEADERS_RENTAL_UNITS,
            **{
                "Nr.": "101",
                "Typ": "Wohnung",
                "Import-ID": "Musterweg1-101",
            },
        )
        results = self._run_import(rows_ru=[row])
        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 1)

    def test_missing_unit_number_fails(self):
        """Row without Rental Unit Number fails validation."""
        row = self.make_row(
            HEADERS_RENTAL_UNITS,
            **{
                "Liegenschaft": "Musterweg 1",
                "Typ": "Wohnung",
                "Import-ID": "Musterweg1-101",
            },
        )
        results = self._run_import(rows_ru=[row])
        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 1)

    def test_import_type_registered_in_model(self):
        """The import type 'tenant_property_vfn' is a valid ImportJob choice."""
        valid_types = [c[0] for c in ImportJob.IMPORT_TYPE_CHOICES]
        self.assertIn("tenant_property_vfn", valid_types)

    def _run_import(self, rows_bu=None, rows_ru=None, override_existing=False):
        """Import creates a Building, a RentalUnit and a Contract."""
        if not rows_bu:
            row_bu = self.make_row(
                HEADERS_BUILDINGS,
                **{
                    "Name der Liegenschaft": "Musterweg 1",
                    "Strasse": "Musterweg",
                    "Hausnummer": "1",
                    "PLZ": "3011",
                    "Ort": "Bern",
                    "Land": "Schweiz",
                    "Gebäudeversicherungswert (Fr.)": "2'500'000.00",
                    "Anlagekosten (Fr.)": "1'950'000.00",
                    "EGID": "12345",
                },
            )
            rows_bu = [row_bu]
        if not rows_ru:
            row_ru = self.make_row(
                HEADERS_RENTAL_UNITS,
                **{
                    "Liegenschaft": "Musterweg 1",
                    "Typ": "Wohnung",
                    "Nr.": "101",
                    "Bezeichnung": "Wohnung Erdgeschoss",
                    "Stockwerk": "EG",
                    "Anzahl Zimmer": "3.5",
                    "Mindestbelegung": "2",
                    "Fläche (m²)": "85.5",
                    "Zahlungsperiodizität (Monate)": "1",
                    "Nebenkosten akonto (CHF/Periode)": "150",
                    "Nettomiete (CHF/Periode)": "1200",
                    "Mietzinsdepot (CHF)": "2400",
                    "Anteilskapital (CHF)": "15'000",
                    "Zusatzinfo": "Test Zusatzinfo",
                    "EWID": "5001",
                    "Import-ID": "Musterweg1-101",
                    "Import-ID 1 Mieter*in (Person)": "01",
                    "Import-ID 2 Mieter*in (Person)": "",
                    "Bemerkungen Mietvertrag": "Test Bemerkung Mietvertrag",
                    "Vertragsbeginn": "2020-01-01",
                },
            )
            rows_ru = [row_ru]
        excel_file = self.create_test_excel(rows_bu, rows_ru)
        import_job = ImportJob.objects.create(
            file=excel_file, import_type="tenant_property_vfn", override_existing=override_existing
        )
        return ImporterTenantPropertyVFN(import_job).process()
