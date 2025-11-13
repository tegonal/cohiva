"""
Tests for the Tenant and Property Importer.
"""

from datetime import date
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from openpyxl import Workbook

from geno.models import Address, Building, Contract, RentalUnit
from importer.importer_tenant_property import ImporterTenantProperty
from importer.models import ImportJob

User = get_user_model()


class ImporterTenantPropertyTest(TestCase):
    """Test cases for ImporterTenantProperty."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def create_test_excel(self, rows):
        """
        Create a test Excel file in memory.

        Args:
            rows: List of row data (list of lists)

        Returns:
            SimpleUploadedFile with Excel content
        """
        wb = Workbook()
        ws = wb.active

        # Header row - matching actual export format
        headers = [
            "Liegenschaft Bezeichnung",
            "Liegenschaft Nummer",
            "Liegenschaft Strasse",
            "Liegenschaft Postleitzahl",
            "Liegenschaft Ort",
            "Liegenschaft Gebaeudeideidg",
            "Objekttyp Bezeichnung",
            "Nummer",
            "Bezeichnung",
            "Etage Nummer",
            "Zimmerzahl Anzahl",
            "Nutzflaeche",
            "Akonti",
            "Pauschalen",
            "Brutto",
            "Nettomiete",
            "Position",
            "Wohnung Id Eidg",
            "Wohnung Nummer Administrativ",
            "Id",
            "Mieter Person Person Name Vorname",
            "Mieter Person Person Adresse",
            "Mieter Person Person Id",
            "Verhaeltnis Gueltigvon",
            "Verhaeltnis Gueltigbis",
            "Mieter Bezeichnung",
            "Mieter Nummer",
        ]
        ws.append(headers)

        # Data rows
        for row in rows:
            ws.append(row)

        # Save to BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        return SimpleUploadedFile(
            "test_tenant_property.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_import_building_and_rental_unit(self):
        """Test importing a building with a rental unit."""
        rows = [
            [
                "Testliegenschaft",  # Liegenschaft Bezeichnung
                "1001",  # Liegenschaft Nummer
                "Hauptstrasse 10",  # Liegenschaft Strasse
                "3011",  # Liegenschaft Postleitzahl
                "Bern",  # Liegenschaft Ort
                "123456",  # Liegenschaft Gebaeudeideidg (EGID)
                "Wohnung",  # Objekttyp Bezeichnung
                "1.1",  # Nummer
                "Erdgeschoss",  # Bezeichnung
                "1",  # Etage Nummer
                "3.5",  # Zimmerzahl Anzahl
                "85.5",  # Nutzflaeche
                "150.00",  # Akonti
                "",  # Pauschalen
                "",  # Brutto
                "1200.00",  # Nettomiete
                "links",  # Position
                "",  # Wohnung Id Eidg
                "",  # Wohnung Nummer Administrativ
                "unit_001",  # Id
                "",  # Mieter Person Person Name Vorname (no tenant)
                "",  # Mieter Person Person Adresse
                "",  # Mieter Person Person Id
                "",  # Verhaeltnis Gueltigvon
                "",  # Verhaeltnis Gueltigbis
                "",  # Mieter Bezeichnung
                "",  # Mieter Nummer
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(
            file=excel_file, created_by=self.user, import_type="tenant_property"
        )

        importer = ImporterTenantProperty(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        # Check Building was created
        building = Building.objects.get(name="Testliegenschaft")
        self.assertEqual(building.street_name, "Hauptstrasse")
        self.assertEqual(building.house_number, "10")
        self.assertEqual(building.city_zipcode, "3011")
        self.assertEqual(building.city_name, "Bern")
        self.assertEqual(building.egid, 123456)

        # Check RentalUnit was created
        rental_unit = RentalUnit.objects.get(name="1.1", building=building)
        self.assertEqual(rental_unit.label, "Erdgeschoss")
        self.assertEqual(rental_unit.rental_type, "Wohnung")
        self.assertEqual(rental_unit.floor, "1")
        self.assertEqual(rental_unit.rooms, Decimal("3.5"))
        self.assertEqual(rental_unit.area, Decimal("85.5"))
        self.assertEqual(rental_unit.nk, Decimal("150.00"))
        self.assertEqual(rental_unit.rent_netto, Decimal("1200.00"))
        self.assertEqual(rental_unit.note, "links")
        self.assertEqual(rental_unit.status, "Verfügbar")
        self.assertEqual(rental_unit.import_id, f"legacy_{import_job.id}_unit_001")

    def test_import_with_contract(self):
        """Test importing a rental unit with a contract."""
        rows = [
            [
                "Haus B",  # Liegenschaft Bezeichnung
                "",  # Liegenschaft Nummer
                "Bergweg 5",  # Liegenschaft Strasse
                "8000",  # Liegenschaft Postleitzahl
                "Zürich",  # Liegenschaft Ort
                "",  # Liegenschaft Gebaeudeideidg
                "Wohnung",  # Objekttyp Bezeichnung
                "2.3",  # Nummer
                "Dachwohnung",  # Bezeichnung
                "2",  # Etage Nummer
                "2.5",  # Zimmerzahl Anzahl
                "65",  # Nutzflaeche
                "120",  # Akonti
                "",  # Pauschalen
                "",  # Brutto
                "980",  # Nettomiete
                "",  # Position
                "",  # Wohnung Id Eidg
                "",  # Wohnung Nummer Administrativ
                "unit_002",  # Id
                "Max Muster",  # Mieter Person Person Name Vorname
                "Testweg 1, 8000 Zürich",  # Mieter Person Person Adresse
                "person_001",  # Mieter Person Person Id
                "2024-01-01",  # Verhaeltnis Gueltigvon
                "",  # Verhaeltnis Gueltigbis
                "Hauptmieter",  # Mieter Bezeichnung
                "5001",  # Mieter Nummer
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(
            file=excel_file, created_by=self.user, import_type="tenant_property"
        )

        importer = ImporterTenantProperty(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)

        # Check Building
        building = Building.objects.get(name="Haus B")

        # Check RentalUnit
        rental_unit = RentalUnit.objects.get(name="2.3", building=building)
        self.assertEqual(rental_unit.status, "Vermietet")

        # Check Contract was created
        self.assertEqual(Contract.objects.count(), 1)
        contract = Contract.objects.first()
        self.assertEqual(contract.date, date(2024, 1, 1))
        self.assertEqual(contract.note, "Hauptmieter")
        self.assertEqual(contract.state, "unterzeichnet")
        self.assertEqual(contract.import_id, f"legacy_{import_job.id}_contract_5001")

        # Check contractor address was created
        self.assertEqual(Address.objects.count(), 1)
        address = Address.objects.first()
        self.assertEqual(address.first_name, "Max")
        self.assertEqual(address.name, "Muster")
        self.assertEqual(address.street_name, "Testweg")
        self.assertEqual(address.house_number, "1")
        self.assertEqual(address.city_zipcode, "8000")
        self.assertEqual(address.city_name, "Zürich")
        self.assertEqual(address.import_id, f"legacy_{import_job.id}_contractor_person_001")

        # Check contract relationships
        self.assertEqual(contract.contractors.count(), 1)
        self.assertEqual(contract.contractors.first(), address)
        self.assertEqual(contract.main_contact, address)
        self.assertEqual(contract.rental_units.count(), 1)
        self.assertEqual(contract.rental_units.first(), rental_unit)

    def test_leerstand_status(self):
        """Test that Mieter Nummer 9999 marks unit as Leerstand."""
        rows = [
            [
                "Gebäude C",  # Liegenschaft Bezeichnung
                "",  # Liegenschaft Nummer
                "Parkstrasse 20",  # Liegenschaft Strasse
                "6000",  # Liegenschaft Postleitzahl
                "Luzern",  # Liegenschaft Ort
                "",  # Liegenschaft Gebaeudeideidg
                "Wohnung",  # Objekttyp Bezeichnung
                "3.1",  # Nummer
                "Leere Wohnung",  # Bezeichnung
                "3",  # Etage Nummer
                "4",  # Zimmerzahl Anzahl
                "100",  # Nutzflaeche
                "180",  # Akonti
                "",  # Pauschalen
                "",  # Brutto
                "1500",  # Nettomiete
                "",  # Position
                "",  # Wohnung Id Eidg
                "",  # Wohnung Nummer Administrativ
                "",  # Id
                "",  # Mieter Person Person Name Vorname
                "",  # Mieter Person Person Adresse
                "",  # Mieter Person Person Id
                "",  # Verhaeltnis Gueltigvon
                "",  # Verhaeltnis Gueltigbis
                "",  # Mieter Bezeichnung
                "9999",  # Mieter Nummer (Leerstand marker)
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(
            file=excel_file, created_by=self.user, import_type="tenant_property"
        )

        importer = ImporterTenantProperty(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)

        rental_unit = RentalUnit.objects.get(name="3.1")
        self.assertEqual(rental_unit.status, "Leerstand")

    def test_rental_type_mapping(self):
        """Test that rental types are correctly mapped."""
        rows = [
            [
                "Gebäude D",
                "",
                "Dorfstr 1",
                "3000",
                "Bern",
                "",
                "Hobbyraum",  # Should map to "Hobby"
                "H.1",
                "Hobbyraum 1",
                "",
                "",
                "10",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "Gebäude D",
                "",
                "Dorfstr 1",
                "3000",
                "Bern",
                "",
                "Abstellplatz",  # Should map to "Parkplatz"
                "P.1",
                "Parkplatz 1",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(
            file=excel_file, created_by=self.user, import_type="tenant_property"
        )

        importer = ImporterTenantProperty(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 2)

        hobby = RentalUnit.objects.get(name="H.1")
        self.assertEqual(hobby.rental_type, "Hobby")

        parkplatz = RentalUnit.objects.get(name="P.1")
        self.assertEqual(parkplatz.rental_type, "Parkplatz")

    def test_update_existing_rental_unit(self):
        """Test updating an existing rental unit."""
        # Create building and rental unit
        building = Building.objects.create(
            name="Existing Building",
            street_name="Old Street",
            house_number="99",
        )

        rental_unit = RentalUnit.objects.create(
            name="E.1",
            building=building,
            rental_type="Wohnung",
            label="Old Label",
            rent_netto=Decimal("800.00"),
        )

        rows = [
            [
                "Existing Building",  # Same building name
                "",
                "New Street 5",
                "4000",
                "Basel",
                "",
                "Wohnung",
                "E.1",  # Same unit number
                "New Label",  # Updated label
                "2",
                "3",
                "70",
                "140",
                "",
                "",
                "1100",  # Updated rent
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(
            file=excel_file, created_by=self.user, import_type="tenant_property"
        )

        importer = ImporterTenantProperty(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)

        # Check that it updated the existing unit, not created new one
        self.assertEqual(RentalUnit.objects.filter(name="E.1").count(), 1)

        rental_unit.refresh_from_db()
        self.assertEqual(rental_unit.label, "New Label")
        self.assertEqual(rental_unit.rent_netto, Decimal("1100"))

        # Check building was also updated
        building.refresh_from_db()
        self.assertEqual(building.street_name, "New Street")
        self.assertEqual(building.house_number, "5")
