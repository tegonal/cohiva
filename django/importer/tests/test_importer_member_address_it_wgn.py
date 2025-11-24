"""
Tests for the Member/Address importer.
"""

from datetime import date
from io import BytesIO

import openpyxl
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from geno.models import Address, Member
from importer.importer_member_address_it_wgn import ImporterMemberAddressITWGN
from importer.models import ImportJob

User = get_user_model()


class ImporterMemberAddressITWGNTest(TestCase):
    """Test cases for ImporterMemberAddress."""

    def setUp(self):
        """Set up test user and data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def create_test_excel(self, rows):
        """Create a test Excel file with given rows."""
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Headers
        headers = [
            "email",
            "____Person",
            "X_heute",
            "P_nr",
            "____Adressangaben",
            "P_ansprechperson",
            "P_co",
            "P_strasse",
            "P_postfach",
            "P_plzort",
            "P_geschlecht",
            "P_anrede",
            "P_land",
            "P_titel",
            "P_briefanrede",
            "____Kontakt",
            "P_nachname",
            "P_vorname",
            "P_telp",
            "P_telg",
            "P_faxp",
            "P_faxg",
            "P_mobilep",
            "P_mobileg",
            "P_emailp",
            "P_emailg",
            "P_homepagep",
            "P_homepageg",
            "____Persönliches",
            "P_beruf",
            "P_arbeitgeber",
            "P_heimatort",
            "P_geburtsort",
            "P_geburtsdatum",
            "P_portalregcode",
            "P_portalurllogin",
            "____Zahlstellen",
            "ZS_dd",
            "ZS_kontoinhaberdd",
            "ZS_lsv",
            "ZS_kontoinhaberlsv",
            "ZS_auszahlungnk",
            "ZS_kontoinhaberauszahlungnk",
            "ZS_auszahlungverzinsung",
            "ZS_kontoinhaberauszahlungverzinsung",
            "ZS_auszahlungmanuell",
            "ZS_kontoinhaberauszahlungmanuell",
        ]
        worksheet.append(headers)

        # Data rows
        for row in rows:
            worksheet.append(row)

        # Save to BytesIO
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        return SimpleUploadedFile(
            "test_import.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_import_simple_person(self):
        """Test importing a simple person without member."""
        rows = [
            [
                "max.test@example.com",  # email
                "",
                "2024-01-15",
                "1001",
                "",  # Person section + join date + P_nr
                "",
                "",
                "Teststrasse 42",
                "",
                "3011 Bern",  # Address
                "Herr",
                "Herr",
                "Schweiz",
                "",
                "",  # Title/salutation
                "",
                "Müller",
                "Max",
                "+41 31 123 45 67",
                "",  # Contact - name
                "",
                "",
                "+41 79 123 45 67",
                "",
                "max.test@example.com",
                "",  # Contact - phones/email
                "",
                "",
                "",
                "Informatiker",  # Contact - web, Personal - occupation (P_beruf)
                "Tech AG",
                "Bern",
                "",
                "1990-05-15",  # P_arbeitgeber, Personal info
                "",
                "",
                "",
                "",  # Portal info, Payment section start
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",  # Payment accounts
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(file=excel_file, created_by=self.user)

        # Process import
        importer = ImporterMemberAddressITWGN(import_job)
        results = importer.process()

        # Check results
        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        # Check Address was created
        address = Address.objects.get(email="max.test@example.com")
        self.assertEqual(address.name, "Müller")
        # import_id format: legacy_{importjob_id}_{person_number}
        self.assertEqual(address.import_id, f"legacy_{import_job.id}_1001")
        self.assertEqual(address.first_name, "Max")
        self.assertEqual(address.street_name, "Teststrasse")
        self.assertEqual(address.house_number, "42")
        self.assertEqual(address.city_zipcode, "3011")
        self.assertEqual(address.city_name, "Bern")
        self.assertEqual(
            address.occupation, "Informatiker, Tech AG"
        )  # Combined P_beruf + P_arbeitgeber

        # Check Member was created (X_heute was provided)
        member = Member.objects.get(name=address)
        self.assertEqual(member.date_join, date(2024, 1, 15))

    def test_import_organization(self):
        """Test importing an organization."""
        rows = [
            [
                "kontakt@example.ch",
                "",
                "",
                "1002",
                "",
                "Weber",
                "",
                "Hauptstrasse 100",
                "Postfach 1234",
                "4000 Basel",  # P_ansprechperson = Weber (contact person)
                "Firma",
                "Firma",
                "Schweiz",
                "",
                "",
                "",
                "Example GmbH",
                "Thomas",
                "+41 61 123 45 67",
                "",  # P_nachname = Example GmbH (org name), P_vorname = Thomas
                "",
                "",
                "",
                "",
                "kontakt@example.ch",
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
                "",
                "",
                "",
                "",
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(file=excel_file, created_by=self.user)

        importer = ImporterMemberAddressITWGN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)

        # Check organization
        address = Address.objects.get(email="kontakt@example.ch")
        self.assertEqual(address.organization, "Example GmbH")
        self.assertEqual(address.title, "Org")
        self.assertEqual(address.name, "Weber")
        self.assertEqual(address.first_name, "Thomas")
        self.assertTrue(address.po_box)
        self.assertEqual(address.po_box_number, "1234")

    def test_import_with_bank_account(self):
        """Test importing with bank account."""
        rows = [
            [
                "test@example.com",
                "",
                "2024-01-15",
                "1003",
                "",
                "",
                "",
                "Testweg 1",
                "",
                "3000 Bern",
                "Frau",
                "Frau",
                "Schweiz",
                "",
                "",
                "",
                "Test",
                "Anna",
                "",
                "",
                "",
                "",
                "",
                "",
                "test@example.com",
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
                "PostFinance AG, 3030 Bern, Clearing-Nr. 9000, Konto-Nr. CH93 0076 2011 6238 5295 7",  # ZS_dd
                "Anna Test",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",  # Account holder
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(file=excel_file, created_by=self.user)

        importer = ImporterMemberAddressITWGN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)

        # Check bank account was created and linked
        address = Address.objects.get(email="test@example.com")
        self.assertIsNotNone(address.bankaccount)
        self.assertEqual(
            address.bankaccount.iban, "CH9300762011623852957"
        )  # Normalized IBAN (spaces removed)
        self.assertEqual(address.bankaccount.account_holders, "Anna Test")
        self.assertEqual(address.bankaccount.financial_institution, "PostFinance AG")

    def test_update_existing_address(self):
        """Test updating an existing address by import_id."""
        # First, create an import job to get an ID
        excel_file_temp = self.create_test_excel([])
        import_job_existing = ImportJob.objects.create(file=excel_file_temp, created_by=self.user)

        # Create existing address with proper import_id format
        existing = Address.objects.create(
            name="OldName",
            first_name="OldFirst",
            email="old@example.com",
            import_id=f"legacy_{import_job_existing.id}_1004",
        )

        rows = [
            [
                "new@example.com",
                "",
                "",
                "1004",
                "",  # Same P_nr -> same import_id when using same job
                "",
                "",
                "Newstrasse 99",
                "",
                "8000 Zürich",
                "Herr",
                "Herr",
                "Schweiz",
                "",
                "",
                "",
                "NewName",
                "NewFirst",
                "",
                "",
                "",
                "",
                "",
                "",
                "new@example.com",
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
                "",
                "",
                "",
                "",
            ]
        ]

        # Use the same import job to generate matching import_id
        excel_file = self.create_test_excel(rows)
        import_job_existing.file = excel_file
        import_job_existing.save()

        importer = ImporterMemberAddressITWGN(import_job_existing)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)

        # Check address was updated, not created
        expected_import_id = f"legacy_{import_job_existing.id}_1004"
        self.assertEqual(Address.objects.filter(import_id=expected_import_id).count(), 1)
        address = Address.objects.get(import_id=expected_import_id)
        self.assertEqual(address.id, existing.id)  # Same record
        self.assertEqual(address.name, "NewName")
        self.assertEqual(address.first_name, "NewFirst")
        self.assertEqual(address.email, "new@example.com")

    def test_missing_required_fields(self):
        """Test that rows without name fail gracefully."""
        rows = [
            [
                "test@example.com",
                "",
                "",
                "1005",
                "",
                "",
                "",
                "Testweg 1",
                "",
                "3000 Bern",
                "",
                "",
                "Schweiz",
                "",
                "",
                "",
                "",
                "",
                "",
                "",  # Missing both P_nachname and P_vorname
                "",
                "",
                "",
                "",
                "test@example.com",
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
                "",
                "",
                "",
                "",
            ]
        ]

        excel_file = self.create_test_excel(rows)
        import_job = ImportJob.objects.create(file=excel_file, created_by=self.user)

        importer = ImporterMemberAddressITWGN(import_job)
        results = importer.process()

        # Should fail
        self.assertEqual(results["success_count"], 0)
        self.assertEqual(results["error_count"], 1)
        self.assertIn("Mindestens Vor- oder Nachname erforderlich", results["errors"][0]["error"])

    def test_phone_number_cleaning(self):
        """Test that phone numbers with extra leading zeros are cleaned."""
        rows = [
            [
                "phone.test@example.com",
                "",
                "",
                "1006",
                "",
                "",
                "",
                "Teststrasse 1",
                "",
                "3011 Bern",
                "Herr",
                "Herr",
                "Schweiz",
                "",
                "",
                "",
                "Schmidt",
                "Hans",
                "4031 123 45 67",
                "406198765 43",  # P_telp and P_telg with extra leading 0
                "",
                "",
                "0079 555 44 33",
                "0044 111 22 33",
                "phone.test@example.com",
                "",  # P_mobilep and P_mobileg with extra leading 0
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
        import_job = ImportJob.objects.create(file=excel_file, created_by=self.user)

        importer = ImporterMemberAddressITWGN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        # Check that phone numbers were cleaned (extra leading 0 removed)
        address = Address.objects.get(email="phone.test@example.com")
        # The cleaning should convert 0031... to 031... (Swiss format)
        self.assertIn("031", address.telephone)
        self.assertNotIn("0031", address.telephone)

        self.assertIn("079", address.mobile)
        self.assertNotIn("0079", address.mobile)

        self.assertIn("061", address.telephoneOffice)
        self.assertNotIn("0061", address.telephoneOffice)

        self.assertIn("044", address.telephoneOffice2)
        self.assertNotIn("0044", address.telephoneOffice2)
