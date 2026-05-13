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
    "ImportID",
    # Address
    "Organisation",
    "Nachname",
    "Vorname",
    "Anrede",
    "Duzen",
    "Adresszusatz",
    "Strasse",
    "Hausnummer",
    "Postfach",
    "Postfach Nr.",
    "PLZ",
    "Ort",
    "Land",
    "Telefon",
    "2. Telefon",
    "Telefon Geschäft",
    "Email",
    "2. Email",
    "AHV-Nr.",
    "Geburtsdatum",
    "Heimatort",
    "Kontoverbindung",
    ## Member
    "Eintritt [Mitglied]",
    "Austritt [Mitglied]",
    "Flag 1: Test A",
    "Flag 2: Test B",
    "Flag 3: Test C",
    "Flag 4: Test D",
    "Flag 5: Test E",
    "Bemerkungen [Mitglied]",
    ## Share
    "Typ [Beteiligungen]",
    "Status [Beteiligungen]",
    "Datum Beginn [Beteiligungen]",
    "Datum Ende [Beteiligungen]",
    "Beteiligungs-ID",
    "Beteiligungs-ID extern",
    "Anzahl [Beteiligungen]",
    "Betrag pro Stück [Beteiligungen]",
    "Zusatzinfo [Beteiligungen]",
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
            ImportID="101",
            Anrede="Herr",
            Vorname="Hans",
            Nachname="Muster",
            Strasse="Musterstrasse",
            Hausnummer="1",
            PLZ="3011",
            Ort="Bern",
            Land="Schweiz",
            Email="hans.muster@example.com",
            **{
                "Eintritt [Mitglied]": "2020-05-01",
                "Flag 1: Test A": "Ja",
                "Flag 2: Test B": "Nein",
                "Typ [Beteiligungen]": "Genossenschaftsanteilschein",
                "Status [Beteiligungen]": "einbezahlt",
                "Datum Beginn [Beteiligungen]": "2020-05-15",
                "Beteiligungs-ID": "99",
                "Beteiligungs-ID extern": "99ex",
                "Anzahl [Beteiligungen]": "3",
                "Betrag pro Stück [Beteiligungen]": "1000",
                "Zusatzinfo [Beteiligungen]": "Test",
            },
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
        self.assertEqual(address.import_id, "vfn_101")

        member = Member.objects.get(name=address)
        self.assertEqual(member.date_join, date(2020, 5, 1))
        self.assertEqual(member.flag_01, True)
        self.assertEqual(member.flag_02, False)

        share = Share.objects.get(name=address)
        self.assertEqual(share.quantity, 3)
        self.assertEqual(share.value, Decimal("1000"))
        self.assertEqual(share.state, "bezahlt")
        self.assertEqual(share.date, date(2020, 5, 15))
        self.assertEqual(share.identifier, "99")
        self.assertEqual(share.identifier_external, "99ex")
        self.assertEqual(share.note, "Test")

    def test_import_person_no_membership(self):
        """Import a person without membership date — no Member should be created."""
        row = self.make_row(
            ImportID="102",
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

    def test_import_simple_person_with_extra_data(self):
        """Import a single person who is a member and has shares."""
        row = self.make_row(
            ImportID="101",
            Anrede="Frau",
            Vorname="Susi",
            Nachname="Muster",
            Adresszusatz="Whg.099",
            Email="susi.muster@example.com",
            **{
                "Postfach": "Ja",
                "Postfach Nr.": "301",
                "Telefon": "111",
                "2. Telefon": "222",
                "Telefon Geschäft": "333",
                "2. Email": "susi2@example.com",
                "AHV-Nr.": "756.1234.5678.97",
                "Geburtsdatum": "1950-01-01",
                "Heimatort": "Hometown",
                "Eintritt [Mitglied]": "2020-05-01",
                "Austritt [Mitglied]": "2021-05-01",
                "Bemerkungen [Mitglied]": "Test-Bemerkung",
                "Status [Beteiligungen]": "zurückbezahlt",
                "Datum Beginn [Beteiligungen]": "2020-05-15",
                "Datum Ende [Beteiligungen]": "2021-05-15",
                "Anzahl [Beteiligungen]": "1",
                "Betrag pro Stück [Beteiligungen]": "100",
            },
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(
            file=excel_file, import_type="member_address_shares_vfn"
        )
        importer = ImporterMemberAddressSharesVFN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        address = Address.objects.get(email="susi.muster@example.com")
        self.assertEqual(address.title, "Frau")
        self.assertEqual(address.extra, "Whg.099")
        self.assertTrue(address.po_box)
        self.assertEqual(address.po_box_number, "301")
        self.assertEqual(address.telephone, "111")
        self.assertEqual(address.mobile, "222")
        self.assertEqual(address.telephoneOffice, "333")
        self.assertEqual(address.email2, "susi2@example.com")
        self.assertEqual(address.ahv_number, "756.1234.5678.97")
        self.assertEqual(address.date_birth, date(1950, 1, 1))
        self.assertEqual(address.hometown, "Hometown")

        member = Member.objects.get(name=address)
        self.assertEqual(member.date_join, date(2020, 5, 1))
        self.assertEqual(member.date_leave, date(2021, 5, 1))
        self.assertEqual(member.notes, "Test-Bemerkung")

        share = Share.objects.get(name=address)
        self.assertEqual(share.quantity, 1)
        self.assertEqual(share.value, Decimal("100"))
        self.assertEqual(share.state, "bezahlt")
        self.assertEqual(share.date, date(2020, 5, 15))
        self.assertEqual(share.date_end, date(2021, 5, 15))

    def test_import_organization(self):
        """Import a Firma with contact person."""
        row = self.make_row(
            ImportID="200",
            Anrede="Firma",
            Organisation="Musterfirma AG",
            Nachname="Meier",
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
            ImportID="103",
            Vorname="Karl",
            Nachname="Reich",
            Email="karl@example.com",
            Eintrittsdatum="2021-03-10",
            Kontoverbindung="CH5604835012345678009",
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        ImporterMemberAddressSharesVFN(import_job).process()

        address = Address.objects.get(email="karl@example.com")
        self.assertIsNotNone(address.bankaccount)
        self.assertEqual(address.bankaccount.iban, "CH5604835012345678009")

    def test_share_type_created_automatically(self):
        """The default ShareType is created automatically if it does not exist."""
        ShareType.objects.all().delete()
        row = self.make_row(
            ImportID="104",
            Vorname="Lena",
            Nachname="Neumann",
            Email="lena@example.com",
            Eintrittsdatum="2022-06-01",
            **{
                "Anzahl [Beteiligungen]": 1,
                "Betrag pro Stück [Beteiligungen]": 500,
                "Datum Beginn [Beteiligungen]": "2022-06-01",
            },
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
            ImportID="105",
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
            ImportID="106",
            Vorname="Original",
            Nachname="Person",
            Email="original@example.com",
            Eintrittsdatum="2023-01-01",
        )
        excel_file1 = self.create_test_excel([row])
        job1 = ImportJob.objects.create(file=excel_file1)
        ImporterMemberAddressSharesVFN(job1).process()

        row_updated = self.make_row(
            ImportID="106",
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
        row = self.make_row(ImportID="999", Email="noname@example.com")
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file)
        results = ImporterMemberAddressSharesVFN(import_job).process()

        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 0)

    def test_share_state_gefordert_default(self):
        """Shares without explicit 'bezahlt' state default to 'gefordert'."""
        row = self.make_row(
            ImportID="107",
            Vorname="Pending",
            Nachname="Share",
            Email="pending@example.com",
            Eintrittsdatum="2023-01-01",
            **{
                "Anzahl [Beteiligungen]": 2,
                "Betrag pro Stück [Beteiligungen]": 500,
                "Datum Beginn [Beteiligungen]": "2022-06-01",
                "Status [Beteiligungen]": "offen",
            },
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
