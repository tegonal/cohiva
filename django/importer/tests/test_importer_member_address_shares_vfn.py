"""
Tests for the VFN Member/Address/Share importer.
"""

from datetime import date
from decimal import Decimal
from io import BytesIO

import openpyxl
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from geno.models import Address, Member, Share, ShareType
from importer.importer_member_address_shares_vfn import ImporterMemberAddressSharesVFN
from importer.models import ImportJob

User = get_user_model()

HEADERS = [
    "ID", "Anrede", "Titel", "Vorname", "Nachname", "Firma", "Kontaktperson",
    "Strasse", "PLZ", "Ort", "Land", "Telefon", "Mobile", "Email",
    "Eintrittsdatum", "Genossenschaftsanteile Anzahl", "Genossenschaftsanteile Wert",
    "Genossenschaftsanteile Status", "Genossenschaftsanteile Datum", "IBAN", "Kontoinhaber", "Bank",
]


class ImporterMemberAddressSharesVFNTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
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
            "test_import.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def make_row(self, **kwargs):
        """Build a row list from keyword args (keyed by column name)."""
        defaults = {h: "" for h in HEADERS}
        defaults.update(kwargs)
        return [defaults[h] for h in HEADERS]

    # ------------------------------------------------------------------
    # Basic person import
    # ------------------------------------------------------------------

    def test_import_simple_person_with_member_and_share(self):
        """Import a single person who is a member and has shares."""
        row = self.make_row(
            ID="101",
            Anrede="Herr",
            Vorname="Hans",
            Nachname="Muster",
            Strasse="Musterstrasse 1",
            PLZ="3011",
            Ort="Bern",
            Land="CH",
            Email="hans.muster@example.com",
            Eintrittsdatum="2020-05-01",
            **{"Genossenschaftsanteile Anzahl": 3,
               "Genossenschaftsanteile Wert": 1000,
               "Genossenschaftsanteile Status": "bezahlt",
               "Genossenschaftsanteile Datum": "2020-05-15"},
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(
            file=excel_file, import_type="member_address_shares_vfn"
        )
        importer = ImporterMemberAddressSharesVFN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        address = Address.objects.get(email="hans.muster@example.com")
        self.assertEqual(address.name, "Muster")
        self.assertEqual(address.first_name, "Hans")
        self.assertEqual(address.title, "Herr")
        self.assertEqual(address.street_name, "Musterstrasse")
        self.assertEqual(address.house_number, "1")
        self.assertEqual(address.city_zipcode, "3011")
        self.assertEqual(address.city_name, "Bern")
        self.assertEqual(address.import_id, f"vfn_{import_job.id}_101")

        member = Member.objects.get(name=address)
        self.assertEqual(member.date_join, date(2020, 5, 1))

        share = Share.objects.get(name=address)
        self.assertEqual(share.quantity, 3)
        self.assertEqual(share.value, Decimal("1000"))
        self.assertEqual(share.state, "bezahlt")
        self.assertEqual(share.date, date(2020, 5, 15))

    def test_import_person_no_membership(self):
        """Import a person without membership date — no Member should be created."""
        row = self.make_row(
            ID="102",
            Anrede="Frau",
            Vorname="Anna",
            Nachname="Beispiel",
            Email="anna@example.com",
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterMemberAddressSharesVFN(import_job).process()

        self.assertEqual(results["success_count"], 1)
        address = Address.objects.get(email="anna@example.com")
        self.assertFalse(Member.objects.filter(name=address).exists())

    def test_import_organization(self):
        """Import a Firma with contact person."""
        row = self.make_row(
            ID="200",
            Anrede="Firma",
            Firma="Musterfirma AG",
            Kontaktperson="Meier",
            Vorname="Beat",
            Email="info@musterfirma.ch",
            Eintrittsdatum="2019-01-01",
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterMemberAddressSharesVFN(import_job).process()

        self.assertEqual(results["success_count"], 1)
        address = Address.objects.get(email="info@musterfirma.ch")
        self.assertEqual(address.organization, "Musterfirma AG")
        self.assertEqual(address.name, "Meier")
        self.assertEqual(address.title, "Org")

    def test_import_with_bank_account(self):
        """Import person with IBAN creates a BankAccount."""
        row = self.make_row(
            ID="103",
            Vorname="Karl",
            Nachname="Reich",
            Email="karl@example.com",
            Eintrittsdatum="2021-03-10",
            IBAN="CH5604835012345678009",
            Kontoinhaber="Karl Reich",
            Bank="Raiffeisenbank",
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        ImporterMemberAddressSharesVFN(import_job).process()

        address = Address.objects.get(email="karl@example.com")
        self.assertIsNotNone(address.bankaccount)
        self.assertEqual(address.bankaccount.iban, "CH5604835012345678009")
        self.assertEqual(address.bankaccount.financial_institution, "Raiffeisenbank")

    def test_share_type_created_automatically(self):
        """The default ShareType is created automatically if it does not exist."""
        ShareType.objects.all().delete()
        row = self.make_row(
            ID="104",
            Vorname="Lena",
            Nachname="Neumann",
            Email="lena@example.com",
            Eintrittsdatum="2022-06-01",
            **{"Genossenschaftsanteile Anzahl": 1,
               "Genossenschaftsanteile Wert": 500,
               "Genossenschaftsanteile Datum": "2022-06-01"},
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        ImporterMemberAddressSharesVFN(import_job).process()

        self.assertTrue(ShareType.objects.filter(name="Anteilschein").exists())
        share = Share.objects.get(name__email="lena@example.com")
        self.assertEqual(share.quantity, 1)

    def test_prevent_duplicate_without_override(self):
        """Second import of same ID raises error when override_existing=False."""
        row = self.make_row(
            ID="105",
            Vorname="Test",
            Nachname="Doppelt",
            Email="doppelt@example.com",
            Eintrittsdatum="2023-01-01",
        )
        excel_file1 = self.create_test_excel([row])
        import_job1 = ImportJob.objects.create(file=excel_file1)
        ImporterMemberAddressSharesVFN(import_job1).process()

        excel_file2 = self.create_test_excel([row])
        import_job2 = ImportJob.objects.create(file=excel_file2, override_existing=False)
        results = ImporterMemberAddressSharesVFN(import_job2).process()

        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 0)

    def test_override_existing_updates_address(self):
        """With override_existing=True an existing address is updated."""
        row = self.make_row(
            ID="106",
            Vorname="Original",
            Nachname="Person",
            Email="original@example.com",
            Eintrittsdatum="2023-01-01",
        )
        excel_file1 = self.create_test_excel([row])
        job1 = ImportJob.objects.create(file=excel_file1)
        ImporterMemberAddressSharesVFN(job1).process()

        row_updated = self.make_row(
            ID="106",
            Vorname="Geändert",
            Nachname="Person",
            Email="original@example.com",
            Eintrittsdatum="2023-01-01",
        )
        excel_file2 = self.create_test_excel([row_updated])
        job2 = ImportJob.objects.create(file=excel_file2, override_existing=True)
        results = ImporterMemberAddressSharesVFN(job2).process()

        self.assertEqual(results["success_count"], 1)
        address = Address.objects.get(email="original@example.com")
        self.assertEqual(address.first_name, "Geändert")

    def test_missing_name_fails(self):
        """Row with no name fields at all fails validation."""
        row = self.make_row(ID="999", Email="noname@example.com")
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterMemberAddressSharesVFN(import_job).process()

        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 0)

    def test_share_state_gefordert_default(self):
        """Shares without explicit 'bezahlt' state default to 'gefordert'."""
        row = self.make_row(
            ID="107",
            Vorname="Pending",
            Nachname="Share",
            Email="pending@example.com",
            Eintrittsdatum="2023-01-01",
            **{"Genossenschaftsanteile Anzahl": 2,
               "Genossenschaftsanteile Wert": 500,
               "Genossenschaftsanteile Status": "offen",
               "Genossenschaftsanteile Datum": "2023-01-01"},
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        ImporterMemberAddressSharesVFN(import_job).process()

        share = Share.objects.get(name__email="pending@example.com")
        self.assertEqual(share.state, "gefordert")

    def test_import_type_registered_in_model(self):
        """The import type 'member_address_shares_vfn' is a valid ImportJob choice."""
        from importer.models import ImportJob
        valid_types = [c[0] for c in ImportJob.IMPORT_TYPE_CHOICES]
        self.assertIn("member_address_shares_vfn", valid_types)
