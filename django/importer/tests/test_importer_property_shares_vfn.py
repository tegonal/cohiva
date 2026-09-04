"""
Tests for the VFN property Share importer.
"""

from datetime import date
from decimal import Decimal
from io import BytesIO

import openpyxl
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from geno.models import Address, Building, Contract, Member, Share
from importer.importer_property_shares_vfn import ImporterPropertySharesVFN
from importer.models import ImportJob

User = get_user_model()

HEADERS = [
    "Person",
    "Typ",
    "Status",
    "Datum Beginn",
    "Datum Ende",
    "Anzahl",
    "Betrag pro Stück",
    "WEF-Guthaben (BVG/3. Säule)",
    "Fixe Zuteilung zu Vertrag",
    "Zuordnung zu Liegenschaft",
    "Zusatzinfo",
]


class ImporterPropertySharesVFNTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @staticmethod
    def create_test_excel(rows):
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

    @staticmethod
    def make_row(**kwargs):
        """Build a row list from keyword args (keyed by column name)."""
        defaults = {h: "" for h in HEADERS}
        defaults.update(kwargs)
        return [defaults[h] for h in HEADERS]

    def test_import_simple_share(self):
        """Import a single share of one person."""
        address101 = Address.objects.create(name="Test 101", import_id="vfn_101")
        contract123 = Contract.objects.create(date=date(2000, 1, 1), import_id="vfn_Test 123")

        row = self.make_row(
            Typ="Wohnungsanteilskapital",
            Status="einbezahlt",
            **{
                "Person": "101",
                "Datum Beginn": "2020-05-01",
                "Anzahl": "1",
                "Betrag pro Stück": "CHF 123.50",
                "WEF-Guthaben (BVG/3. Säule)": "Nein",
                "Fixe Zuteilung zu Vertrag": "Test 123",
                "Zusatzinfo": "This is only a test!",
            },
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file, import_type="property_shares_vfn")
        importer = ImporterPropertySharesVFN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        share = Share.objects.get(name=address101)
        self.assertEqual(share.name.name, "Test 101")
        self.assertEqual(share.share_type.name, "Wohnungsanteilskapital")
        self.assertEqual(share.payment_state, "bezahlt")
        self.assertEqual(share.payment_date, date(2020, 5, 1))
        self.assertEqual(share.quantity, 1)
        self.assertEqual(share.value, Decimal("123.50"))
        self.assertEqual(share.is_pension_fund, False)
        self.assertEqual(share.attached_to_contract, contract123)
        self.assertEqual(share.note, "This is only a test!")
        self.assertEqual(share.import_id, "vfn_Wohnungsanteilskapital_101_2020-05-01_1_123.50")

    def test_import_share_with_end_date(self):
        """Import a single share of one person with an end date and some other differences."""
        address101 = Address.objects.create(name="Test 101", import_id="vfn_101")
        building1 = Building.objects.create(name="Building 1")

        row = self.make_row(
            Typ="Wohnungsanteilskapital",
            Status="einbezahlt",
            **{
                "Person": "101",
                "Datum Beginn": "2020-05-01",
                "Datum Ende": "2020-12-23",
                "Anzahl": "2",
                "Betrag pro Stück": "CHF 500.00",
                "WEF-Guthaben (BVG/3. Säule)": "Ja",
                "Zuordnung zu Liegenschaft": "Building 1",
            },
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file, import_type="property_shares_vfn")
        importer = ImporterPropertySharesVFN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        share = Share.objects.get(name=address101)
        self.assertEqual(share.share_type.name, "Wohnungsanteilskapital")
        self.assertEqual(share.payment_date, date(2020, 5, 1))
        self.assertEqual(share.repayment_date, date(2020, 12, 23))
        self.assertEqual(share.quantity, 2)
        self.assertEqual(share.value, Decimal("500.00"))
        self.assertEqual(share.is_pension_fund, True)
        self.assertEqual(share.attached_to_building, building1)
        self.assertEqual(share.import_id, "vfn_Wohnungsanteilskapital_101_2020-05-01_2_500.00")

    def test_import_share_without_date(self):
        """Import a share without a date."""
        address101 = Address.objects.create(name="Test 101", import_id="vfn_101")

        row = self.make_row(
            Typ="Wohnungsanteilskapital",
            Status="einbezahlt",
            **{
                "Person": "101",
                "Anzahl": "3",
                "Betrag pro Stück": "CHF 500.00",
            },
        )
        excel_file = self.create_test_excel([row])
        import_job = ImportJob.objects.create(file=excel_file, import_type="property_shares_vfn")
        importer = ImporterPropertySharesVFN(import_job)
        results = importer.process()

        self.assertEqual(results["success_count"], 1)
        self.assertEqual(results["error_count"], 0)

        share1 = Share.objects.get(name=address101)
        self.assertEqual(share1.payment_date, date.today())

    def test_prevent_duplicate_without_override(self):
        """Second import of same ID raises error when override_existing=False."""
        Address.objects.create(name="Test 101", import_id="vfn_101")
        row = self.make_row(
            Typ="Wohnungsanteilskapital",
            Status="einbezahlt",
            **{
                "Person": "101",
                "Datum Beginn": "2020-05-01",
                "Anzahl": "1",
                "Betrag pro Stück": "CHF 123.50",
            },
        )
        excel_file1 = self.create_test_excel([row])
        import_job1 = ImportJob.objects.create(file=excel_file1)
        ImporterPropertySharesVFN(import_job1).process()

        excel_file2 = self.create_test_excel([row])
        import_job2 = ImportJob.objects.create(file=excel_file2, override_existing=False)
        results = ImporterPropertySharesVFN(import_job2).process()

        self.assertEqual(results["error_count"], 1)
        self.assertEqual(results["success_count"], 0)

    def test_override_existing_updates_share(self):
        """With override_existing=True an existing share is updated."""
        address101 = Address.objects.create(name="Test 101", import_id="vfn_101")
        row = self.make_row(
            Typ="Wohnungsanteilskapital",
            Status="einbezahlt",
            **{
                "Person": "101",
                "Datum Beginn": "2020-05-01",
                "Anzahl": "1",
                "Betrag pro Stück": "CHF 123.50",
            },
        )
        excel_file1 = self.create_test_excel([row])
        job1 = ImportJob.objects.create(file=excel_file1)
        ImporterPropertySharesVFN(job1).process()

        row_updated = self.make_row(
            Typ="Wohnungsanteilskapital",
            Status="einbezahlt",
            **{
                "Person": "101",
                "Datum Beginn": "2020-05-01",
                "Datum Ende": "2021-11-18",
                "Anzahl": "1",
                "Betrag pro Stück": "CHF 123.50",
            },
        )
        excel_file2 = self.create_test_excel([row_updated])
        job2 = ImportJob.objects.create(file=excel_file2, override_existing=True)
        results = ImporterPropertySharesVFN(job2).process()

        self.assertEqual(results["success_count"], 1)
        share = Share.objects.get(name=address101)
        self.assertEqual(share.repayment_date, date(2021, 11, 18))

    def test_import_type_registered_in_model(self):
        """The import type 'member_address_shares_vfn' is a valid ImportJob choice."""
        from importer.models import ImportJob

        valid_types = [c[0] for c in ImportJob.IMPORT_TYPE_CHOICES]
        self.assertIn("property_shares_vfn", valid_types)

    def test_missing_address_reference(self):
        """Throw and error if no valid address reference is present."""
        row_data = {
            "Anzahl": "1",
            "Betrag pro Stück": "CHF 123.50",
            "Typ": "TestShare",
            "Datum Beginn": "2020-05-01",
        }
        with self.assertRaises(ValidationError):
            ImporterPropertySharesVFN._build_import_info(row_data)

    def test_address_by_address_id(self):
        """Import a share by address database id."""
        address = Address.objects.create(name="Test", import_id="")
        row_data = {
            "Adress-ID": address.id,
            "Anzahl": "1",
            "Betrag pro Stück": "CHF 123.50",
            "Typ": "TestShare",
            "Datum Beginn": "2020-05-01",
        }
        ret = ImporterPropertySharesVFN._build_import_info(row_data)
        self.assertEqual(ret["address"], address)
        self.assertEqual(ret["import_id"], f"vfn_TestShare_a{address.pk}_2020-05-01_1_123.50")

        # Address-ID takes precedence over other references
        row_data.update({"Mitglied-ID": 1, "Person": "vfn_101"})
        ret = ImporterPropertySharesVFN._build_import_info(row_data)
        self.assertEqual(ret["address"], address)

    def test_address_by_member_id(self):
        """Import a share by member database id."""
        address = Address.objects.create(name="Test", import_id="")
        member = Member.objects.create(name=address, date_join=date(2000, 1, 1))
        row_data = {
            "Mitglied-ID": member.id,
            "Anzahl": "1",
            "Betrag pro Stück": "CHF 123.50",
            "Typ": "TestShare",
            "Datum Beginn": "2020-05-01",
        }
        ret = ImporterPropertySharesVFN._build_import_info(row_data)
        self.assertEqual(ret["address"], address)
        self.assertEqual(ret["import_id"], f"vfn_TestShare_m{member.pk}_2020-05-01_1_123.50")

        # Mitglied-ID takes precedence over Person
        row_data.update({"Person": "vfn_101"})
        ret = ImporterPropertySharesVFN._build_import_info(row_data)
        self.assertEqual(ret["address"], address)

    def test_address_by_person_import_id(self):
        """Import a share by person import id."""
        address = Address.objects.create(name="Test", import_id="vfn_101")
        row_data = {
            "Person": 101,
            "Anzahl": "1",
            "Betrag pro Stück": "CHF 123.50",
            "Typ": "TestShare",
            "Datum Beginn": "2020-05-01",
        }
        ret = ImporterPropertySharesVFN._build_import_info(row_data)
        self.assertEqual(ret["address"], address)
        self.assertEqual(ret["import_id"], "vfn_TestShare_101_2020-05-01_1_123.50")
