from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse

from geno.models import (
    Address,
    Building,
    Child,
    Contract,
    InvoiceCategory,
    Member,
    RegistrationEvent,
    RentalUnit,
    Share,
    ShareType,
)

from .base import GenoAdminTestCase


class MemberTests(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_non_overlapping_memberships_allowed(self):
        first_membership = Member.objects.create(
            name=self.addresses[0], date_join=date(2023, 1, 1), date_leave=date(2024, 1, 1)
        )
        second_membership = Member.objects.create(
            name=self.addresses[0], date_join=date(year=2024, month=1, day=2)
        )
        self.assertTrue(first_membership.id)
        self.assertTrue(second_membership.id)
        # Check that is_active() returns the correct value
        self.assertTrue(second_membership.is_active())
        self.assertFalse(first_membership.is_active())
        # Check that the `active` database field returns the correct value
        self.assertTrue(second_membership.active)
        self.assertFalse(first_membership.active)

    def test_overlapping_memberships_not_allowed(self):
        Member.objects.create(
            name=self.addresses[0],
            date_join=date(2023, 1, 1),
            date_leave=date(2024, 1, 1),
            active=False,
        )
        with self.assertRaises(ValidationError):
            Member(
                name=self.addresses[0],
                date_join=date(2023, 6, 1),
                date_leave=date(2023, 12, 31),
                active=True,
            ).clean()

    def test_overlapping_memberships_not_allowed_open_ended(self):
        Member.objects.create(
            name=self.addresses[0], date_join=date(2023, 1, 1), date_leave=None, active=True
        )
        with self.assertRaises(ValidationError):
            Member(
                name=self.addresses[0],
                date_join=date(2024, 1, 1),
                date_leave=date(2025, 1, 1),
                active=True,
            ).clean()

    def test_overlapping_memberships_not_allowed_second_open_ended(self):
        Member.objects.create(
            name=self.addresses[0],
            date_join=date(2023, 1, 1),
            date_leave=date(2024, 1, 1),
            active=False,
        )
        with self.assertRaises(ValidationError):
            Member(
                name=self.addresses[0], date_join=date(2023, 6, 1), date_leave=None, active=True
            ).clean()

    def test_membership_ends_before_it_begins(self):
        constraint_name = "member_date_leave_gte_date_join"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Member.objects.create(
                name=self.addresses[0],
                date_join=date(year=2025, month=1, day=1),
                date_leave=date(2024, 1, 1),
            )


class InvoiceTests(TestCase):
    def test_invoice_reference_id_too_small(self):
        constraint_name = "geno_invoicecategory_reference_id_range"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            InvoiceCategory.objects.create(name="Test", reference_id=0)

    def test_invoice_reference_id_too_big(self):
        constraint_name = "geno_invoicecategory_reference_id_range"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            InvoiceCategory.objects.create(name="Test", reference_id=90)


class AddressTest(TestCase):
    def test_str(self):
        adr = Address(first_name="Hans", name="Muster", email="hans@muster.ch")
        self.assertEqual(str(adr), "Muster, Hans")
        adr.organization = "Orga"
        self.assertEqual(str(adr), "Orga, Hans Muster")

    def test_get_mail_recipient(self):
        settings.TEST_MAIL_RECIPIENT = "debug@cohiva.ch"
        adr1 = Address(first_name="Hans", name="Muster", email="hans@muster.ch")
        adr2 = Address(first_name="Hans", name="Muster", email="hans.muster@example.com")

        self.assertEqual(adr1.get_mail_recipient(), '"Hans Muster" <hans@muster.ch>')
        self.assertEqual(adr2.get_mail_recipient(), '"Hans Muster" <debug@cohiva.ch>')

        settings.DEBUG = True
        self.assertEqual(adr1.get_mail_recipient(), '"Hans Muster" <debug@cohiva.ch>')
        settings.DEBUG = False

    def test_street(self):
        adr = Address(first_name="Hans", name="Muster", email="hans@muster.ch")
        self.assertEqual(adr.street, "")
        adr.po_box = True
        self.assertEqual(adr.street, "Postfach")
        adr.street_name = "Street"
        self.assertEqual(adr.street, "Street, Postfach")
        adr.house_number = "99c"
        self.assertEqual(adr.street, "Street 99c, Postfach")
        adr.po_box = False
        self.assertEqual(adr.street, "Street 99c")
        adr.po_box = True
        adr.street_name = ""
        self.assertEqual(adr.street, "Postfach")
        adr.po_box = False
        self.assertEqual(adr.street, "")
        adr.po_box_number = "123"
        self.assertEqual(adr.street, "")
        adr.po_box = True
        self.assertEqual(adr.street, "Postfach 123")
        adr.street_name = "Street"
        self.assertEqual(adr.street, "Street 99c, Postfach 123")
        adr.po_box = False
        self.assertEqual(adr.street, "Street 99c")

    def test_city(self):
        adr = Address(first_name="Hans", name="Muster", email="hans@muster.ch")
        self.assertEqual(adr.city, "")
        adr.city_zipcode = "D-99999"
        self.assertEqual(adr.city, "")
        adr.city_name = "City"
        self.assertEqual(adr.city, "D-99999 City")
        adr.city_zipcode = ""
        self.assertEqual(adr.city, "City")

    def test_email_lowercase(self):
        adr = Address(first_name="Hans", name="Muster")
        adr.save()
        adr_saved = Address.objects.get(id=adr.id)
        self.assertEqual(adr_saved.email, "")

        adr = Address(first_name="Hans", name="Muster", email="hans@Muster.ch")
        adr.save()
        adr_saved = Address.objects.get(id=adr.id)
        self.assertEqual(adr_saved.email, "hans@muster.ch")

        adr.email2 = "Hans@Muster.CH"
        adr.save()
        adr_saved = Address.objects.get(id=adr.id)
        self.assertEqual(adr_saved.email2, "hans@muster.ch")

    def test_debug_mode_uses_test_recipient(self):
        addr = Address(first_name="Lisa", name="Meier", email="lisa@realmail.com")
        with override_settings(DEBUG=True, TEST_MAIL_RECIPIENT="test@domain.com"):
            result = addr.get_mail_recipient()
            self.assertEqual(result, '"Lisa Meier" <test@domain.com>')

    def test_example_com_uses_test_recipient(self):
        addr = Address(first_name="Anna", name="Musterfrau", email="anna@example.com")
        with override_settings(DEBUG=False, TEST_MAIL_RECIPIENT="test@domain.com"):
            result = addr.get_mail_recipient()
            self.assertEqual(result, '"Anna Musterfrau" <test@domain.com>')

    def test_normal_email_returns_real_address(self):
        addr = Address(first_name="Lisa", name="Meier", email="lisa@realmail.com")
        with override_settings(DEBUG=False, TEST_MAIL_RECIPIENT="test@domain.com"):
            result = addr.get_mail_recipient()
            self.assertEqual(result, '"Lisa Meier" <lisa@realmail.com>')

    def test_is_member_no_membership(self):
        """Address with no membership returns False."""
        adr = Address.objects.create(name="Test")
        self.assertFalse(adr.is_member())

    def test_is_member_open_ended(self):
        """Open-ended memberships: joined long ago and joined this year."""
        adr = Address.objects.create(name="Test")

        # Open-ended, joined long ago
        Member.objects.create(name=adr, date_join=date(2000, 1, 1))
        self.assertTrue(adr.is_member())
        self.assertTrue(adr.is_member(date_mode="last_year"))
        self.assertTrue(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertTrue(adr.is_member(date=date(date.today().year + 1, 1, 2)))

        # Open-ended, joined this year
        Member.objects.all().delete()
        Member.objects.create(name=adr, date_join=date(date.today().year, 1, 1))
        self.assertTrue(adr.is_member())
        self.assertFalse(adr.is_member(date_mode="last_year"))
        self.assertTrue(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertTrue(adr.is_member(date=date(date.today().year + 1, 1, 2)))

    def test_is_member_with_end_date(self):
        """Memberships with a future end date: joined long ago and joined this year."""
        adr = Address.objects.create(name="Test")

        # Future end date, joined long ago
        Member.objects.create(
            name=adr,
            date_join=date(2000, 1, 1),
            date_leave=date(date.today().year + 1, 1, 1),
        )
        self.assertTrue(adr.is_member())
        self.assertTrue(adr.is_member(date_mode="last_year"))
        self.assertFalse(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertFalse(adr.is_member(date=date(date.today().year + 1, 1, 1)))
        self.assertFalse(adr.is_member(date=date(date.today().year + 1, 1, 2)))

        # Future end date, joined this year
        Member.objects.all().delete()
        Member.objects.create(
            name=adr,
            date_join=date(date.today().year, 1, 1),
            date_leave=date(date.today().year + 1, 1, 1),
        )
        self.assertTrue(adr.is_member())
        self.assertFalse(adr.is_member(date_mode="last_year"))
        self.assertFalse(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertFalse(adr.is_member(date=date(date.today().year + 1, 1, 2)))

    def test_is_member_multiple_memberships(self):
        """Multiple memberships including a current open-ended one and a past one."""
        adr = Address.objects.create(name="Test")

        # Current open-ended membership + past membership
        Member.objects.create(name=adr, date_join=date(date.today().year, 1, 1))
        Member.objects.create(name=adr, date_join=date(1995, 1, 1), date_leave=date(1998, 6, 1))

        self.assertTrue(adr.is_member())
        self.assertFalse(adr.is_member(date_mode="last_year"))
        self.assertTrue(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertTrue(adr.is_member(date=date(date.today().year + 1, 1, 2)))
        self.assertTrue(adr.is_member(date=date(1997, 12, 31)))
        self.assertTrue(adr.is_member(date=datetime(1997, 12, 31, 1, 1, 1)))

    def test_is_member_invalid_arguments(self):
        """Invalid arguments raise ValueError."""
        adr = Address.objects.create(name="Test")

        with self.assertRaises(ValueError):
            adr.is_member(date_mode="last_year", date=date(1999, 12, 31))
        with self.assertRaises(ValueError):
            adr.is_member(date=False)
        with self.assertRaises(ValueError):
            adr.is_member(date_mode="_invalid")


class RegistrationEventTest(TestCase):
    registration_form_viewname = "registration-form"

    def test_registration_link(self):
        event = RegistrationEvent(name="Test Event")
        self.assertEqual(event.registration_link, "Bitte zuerst speichern.")
        event.save()
        self.assertEqual(event.registration_link, "[Kein öffentlicher Link]")
        event.publication_type = "public"
        url = settings.BASE_URL + reverse(
            self.registration_form_viewname, kwargs={"registration_id": event.id}
        )
        self.assertEqual(event.registration_link, f"<a href='{url}'>{url}</a>")

    @patch("geno.models.reverse", side_effect=NoReverseMatch())
    def test_registration_link_not_found(self, _mock_reverse):
        event = RegistrationEvent.objects.create(name="Test Event", publication_type="public")
        self.assertEqual(
            event.registration_link,
            f"[Fehler: Keine URL für '{self.registration_form_viewname}' gefunden]",
        )


class GetActiveContractsTests(GenoAdminTestCase):
    """
    Tests for Contract.get_active(date=reference_date) and
    Contract.get_active_in_period(period_start=..., period_end=...).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.D1 = date(2020, 1, 1)  # far past
        cls.D2 = date(2020, 6, 10)  # past
        cls.D3 = date(2020, 6, 15)  # present (reference only)
        cls.D4 = date(2020, 6, 20)  # future
        cls.D5 = date(2020, 12, 31)  # far future

    def _create_contract(self, **kwargs):
        return Contract.objects.create(**kwargs)

    # --------------------------------------------------------------------- #
    # SINGLE DATE
    # --------------------------------------------------------------------- #
    def test_single_date_active_inside_period(self):
        contract = self._create_contract(date=self.D2, date_end=self.D4)
        result = Contract.get_active(date=self.D3)
        self.assertIn(contract, result)

    def test_single_date_active_on_start_boundary(self):
        contract = self._create_contract(date=self.D3, date_end=self.D4)
        result = Contract.get_active(date=self.D3)
        self.assertIn(contract, result)

    def test_single_date_active_on_end_boundary_is_excluded(self):
        contract = self._create_contract(date=self.D2, date_end=self.D3)
        result = Contract.get_active(date=self.D3)
        self.assertNotIn(contract, result)

    def test_single_date_inactive_before_start(self):
        contract = self._create_contract(date=self.D4, date_end=self.D5)
        result = Contract.get_active(date=self.D3)
        self.assertNotIn(contract, result)

    def test_single_date_inactive_after_end(self):
        contract = self._create_contract(date=self.D1, date_end=self.D2)
        result = Contract.get_active(date=self.D3)
        self.assertNotIn(contract, result)

    def test_single_date_active_open_ended(self):
        contract = self._create_contract(date=self.D3, date_end=None)
        result = Contract.get_active(date=self.D5)
        self.assertIn(contract, result)

    def test_single_date_inactive_open_ended_before_start(self):
        contract = self._create_contract(date=self.D4, date_end=None)
        result = Contract.get_active(date=self.D3)
        self.assertNotIn(contract, result)

    # --------------------------------------------------------------------- #
    # SUBCONTRACTS
    # --------------------------------------------------------------------- #
    def test_single_date_excludes_subcontracts_by_default(self):
        main = self._create_contract(date=self.D2, date_end=self.D4)
        sub = self._create_contract(date=self.D2, date_end=self.D4, main_contract=main)
        result = Contract.get_active(date=self.D3)
        self.assertIn(main, result)
        self.assertNotIn(sub, result)

    def test_single_date_includes_subcontracts_when_requested(self):
        main = self._create_contract(date=self.D2, date_end=self.D4)
        sub = self._create_contract(date=self.D2, date_end=self.D4, main_contract=main)
        result = Contract.get_active(date=self.D3, include_subcontracts=True)
        self.assertIn(main, result)
        self.assertIn(sub, result)

    def test_subcontract_alone_is_inactive_when_parent_is_inactive(self):
        main = self._create_contract(date=self.D1, date_end=self.D2)
        sub = self._create_contract(date=self.D2, date_end=self.D4, main_contract=main)
        result = Contract.get_active(date=self.D3, include_subcontracts=True)
        self.assertNotIn(main, result)
        self.assertIn(sub, result)

    # --------------------------------------------------------------------- #
    # DEFAULT DATE CLAMPING
    # --------------------------------------------------------------------- #
    def test_default_date_clamped_to_2021_12_01(self):
        contract = self._create_contract(date=date(2020, 1, 1), date_end=None)

        class MockDate(date):
            @classmethod
            def today(cls):
                return cls(2020, 1, 1)

        with patch("geno.models.datetime.date", MockDate):
            result = Contract.get_active()
            # Because date is clamped to 2021-12-01, the contract is active
            self.assertIn(contract, result)

    # --------------------------------------------------------------------- #
    # DATE RANGE - overlap variations
    # --------------------------------------------------------------------- #
    def test_range_contract_fully_contains_reference(self):
        contract = self._create_contract(date=self.D1, date_end=self.D5)
        result = Contract.get_active_in_period(period_start=self.D2, period_end=self.D4)
        self.assertIn(contract, result)

    def test_range_reference_fully_contains_contract(self):
        contract = self._create_contract(date=self.D2, date_end=self.D4)
        result = Contract.get_active_in_period(period_start=self.D1, period_end=self.D5)
        self.assertIn(contract, result)

    def test_range_reference_overlaps_start_of_contract(self):
        contract = self._create_contract(date=self.D3, date_end=self.D5)
        result = Contract.get_active_in_period(period_start=self.D1, period_end=self.D3)
        self.assertIn(contract, result)

    def test_range_reference_does_not_overlap_start_when_end_is_exclusive(self):
        contract = self._create_contract(date=self.D3, date_end=self.D5)
        result = Contract.get_active_in_period(
            period_start=self.D1, period_end=self.D3, exclude_period_end=True
        )
        self.assertNotIn(contract, result)

    def test_range_reference_overlaps_end_of_contract(self):
        contract = self._create_contract(date=self.D1, date_end=self.D3)
        result = Contract.get_active_in_period(period_start=self.D3, period_end=self.D5)
        self.assertIn(contract, result)

    def test_range_no_overlap_reference_before_contract(self):
        contract = self._create_contract(date=self.D3, date_end=self.D5)
        result = Contract.get_active_in_period(period_start=self.D1, period_end=self.D2)
        self.assertNotIn(contract, result)

    def test_range_no_overlap_reference_after_contract(self):
        contract = self._create_contract(date=self.D1, date_end=self.D2)
        result = Contract.get_active_in_period(period_start=self.D3, period_end=self.D5)
        self.assertNotIn(contract, result)

    def test_range_no_overlap_adjacent_days(self):
        """Contract ends D2, reference starts D3 -> no common day."""
        contract = self._create_contract(date=self.D1, date_end=self.D2)
        result = Contract.get_active_in_period(period_start=self.D3, period_end=self.D4)
        self.assertNotIn(contract, result)

    def test_range_active_open_ended(self):
        contract = self._create_contract(date=self.D4, date_end=None)
        result = Contract.get_active_in_period(period_start=self.D5, period_end=self.D5)
        self.assertIn(contract, result)

    def test_range_inactive_open_ended_before_start(self):
        contract = self._create_contract(date=self.D4, date_end=None)
        result = Contract.get_active_in_period(period_start=self.D1, period_end=self.D2)
        self.assertNotIn(contract, result)

    def test_range_single_day_contract_inside_range(self):
        contract = self._create_contract(date=self.D3, date_end=self.D3)
        result = Contract.get_active_in_period(period_start=self.D2, period_end=self.D4)
        self.assertIn(contract, result)

    def test_range_single_day_reference_overlaps(self):
        contract = self._create_contract(date=self.D2, date_end=self.D4)
        result = Contract.get_active_in_period(period_start=self.D3, period_end=self.D3)
        self.assertIn(contract, result)

    # --------------------------------------------------------------------- #
    # DATE RANGE - subcontracts
    # --------------------------------------------------------------------- #
    def test_range_excludes_subcontracts_by_default(self):
        main = self._create_contract(date=self.D2, date_end=self.D4)
        sub = self._create_contract(date=self.D2, date_end=self.D4, main_contract=main)
        result = Contract.get_active_in_period(period_start=self.D3, period_end=self.D3)
        self.assertIn(main, result)
        self.assertNotIn(sub, result)

    def test_range_includes_subcontracts_when_requested(self):
        main = self._create_contract(date=self.D2, date_end=self.D4)
        sub = self._create_contract(date=self.D2, date_end=self.D4, main_contract=main)
        result = Contract.get_active_in_period(
            period_start=self.D3, period_end=self.D3, include_subcontracts=True
        )
        self.assertIn(main, result)
        self.assertIn(sub, result)

    # --------------------------------------------------------------------- #
    # MIXED / BULK SCENARIOS
    # --------------------------------------------------------------------- #
    def test_range_returns_empty_when_no_contracts_overlap(self):
        c1 = self._create_contract(date=self.D1, date_end=self.D2)
        c2 = self._create_contract(date=self.D4, date_end=self.D5)
        result = list(Contract.get_active(date=self.D3))
        self.assertNotIn(c1, result)
        self.assertNotIn(c2, result)
        self.assertEqual(len(result), 0)

    def test_range_excludes_neighbors_but_keeps_active(self):
        expired = self._create_contract(date=self.D1, date_end=self.D2)
        active = self._create_contract(date=self.D2, date_end=self.D4)
        future = self._create_contract(date=self.D4, date_end=self.D5)
        result = list(Contract.get_active(date=self.D3))
        self.assertNotIn(expired, result)
        self.assertIn(active, result)
        self.assertNotIn(future, result)
        self.assertEqual(len(result), 1)

    def test_range_excluded_when_contracts_create_gap(self):
        first = self._create_contract(date=self.D1, date_end=self.D2)
        second = self._create_contract(date=self.D3, date_end=self.D5)
        result = list(Contract.get_active_in_period(period_start=self.D3, period_end=self.D4))
        self.assertNotIn(first, result)
        self.assertIn(second, result)


class GenoBaseSaveAsCopyTests(TestCase):
    """
    Tests for GenoBase.save_as_copy(), in particular the clearing of
    `import_id` (if the model has that field) that was added alongside
    the pre-existing `name` "[KOPIE]" suffix logic.
    """

    def test_import_id_and_name_are_reset_on_copy(self):
        building = Building.objects.create(name="Building A")
        rental_unit = RentalUnit.objects.create(
            name="A1",
            rental_type="Wohnung",
            building=building,
            import_id="IMPORT-100",
        )
        original_pk = rental_unit.pk

        rental_unit.save_as_copy()

        # The instance now represents the freshly inserted copy.
        self.assertIsNotNone(rental_unit.pk)
        self.assertNotEqual(rental_unit.pk, original_pk)
        self.assertEqual(rental_unit.name, "A1 [KOPIE]")
        self.assertIsNone(rental_unit.import_id)

        # The original row must be left untouched.
        original = RentalUnit.objects.get(pk=original_pk)
        self.assertEqual(original.name, "A1")
        self.assertEqual(original.import_id, "IMPORT-100")

        # The copy was persisted with a cleared import_id.
        copy = RentalUnit.objects.get(pk=rental_unit.pk)
        self.assertIsNone(copy.import_id)
        self.assertEqual(copy.name, "A1 [KOPIE]")

    def test_import_id_cleared_even_when_name_is_not_a_string(self):
        # Child.name is a OneToOneField to Address (not a string), so the
        # "[KOPIE]" suffix logic must not touch it, but import_id must
        # still be cleared independently.
        address = Address.objects.create(name="Test", first_name="Testus")
        share = Share.objects.create(
            name=address,
            share_type=ShareType.objects.create(name="Test"),
            value=1,
            import_id="SHARE-1",
        )

        share.save_as_copy()

        self.assertEqual(share.name, address)
        self.assertIsNone(share.import_id)


class AddressSaveAsCopyTests(TestCase):
    def test_save_as_copy_clears_user_random_id_and_import_id(self):
        user = User.objects.create_user(username="hans", password="secret")
        address = Address.objects.create(
            name="Muster",
            first_name="Hans",
            user=user,
            import_id="ADDR-1",
        )
        original_pk = address.pk
        original_random_id = address.random_id

        address.save_as_copy()

        self.assertIsNotNone(address.pk)
        self.assertNotEqual(address.pk, original_pk)
        self.assertIsNone(address.user)
        self.assertNotEqual(address.random_id, original_random_id)
        self.assertIsNone(address.import_id)
        self.assertEqual(address.name, "Muster [KOPIE]")

        # The original row keeps its user, random_id and import_id.
        original = Address.objects.get(pk=original_pk)
        self.assertEqual(original.user, user)
        self.assertEqual(original.random_id, original_random_id)
        self.assertEqual(original.import_id, "ADDR-1")
        self.assertEqual(original.name, "Muster")

    def test_save_as_copy_without_import_id_still_clears_user_and_random_id(self):
        user = User.objects.create_user(username="anna", password="secret")
        address = Address.objects.create(name="Musterfrau", first_name="Anna", user=user)
        original_random_id = address.random_id

        address.save_as_copy()

        self.assertIsNone(address.user)
        self.assertIsNone(address.import_id)
        self.assertNotEqual(address.random_id, original_random_id)


class ContractSaveAsCopyTests(TestCase):
    def setUp(self):
        building = Building.objects.create(name="Building C")
        self.rental_unit = RentalUnit.objects.create(
            name="C1", rental_type="Wohnung", building=building
        )
        self.contractor = Address.objects.create(name="Muster", first_name="Hans")
        child_address = Address.objects.create(name="Muster", first_name="Kind")
        self.child = Child.objects.create(name=child_address, presence=5.0)

    def test_save_as_copy_preserves_m2m_and_clears_import_id(self):
        contract = Contract.objects.create(date=date(2024, 1, 1), import_id="CONTRACT-1")
        contract.contractors.set([self.contractor])
        contract.children.set([self.child])
        contract.rental_units.set([self.rental_unit])

        original_pk = contract.pk

        contract.save_as_copy()

        self.assertIsNotNone(contract.pk)
        self.assertNotEqual(contract.pk, original_pk)
        self.assertIsNone(contract.import_id)
        self.assertEqual(list(contract.contractors.all()), [self.contractor])
        self.assertEqual(list(contract.children.all()), [self.child])
        self.assertEqual(list(contract.rental_units.all()), [self.rental_unit])

        # The original contract is unaffected and keeps its import_id and
        # its own M2M relations.
        original = Contract.objects.get(pk=original_pk)
        self.assertEqual(original.import_id, "CONTRACT-1")
        self.assertEqual(list(original.contractors.all()), [self.contractor])
        self.assertEqual(list(original.children.all()), [self.child])
        self.assertEqual(list(original.rental_units.all()), [self.rental_unit])


class ShareGetContextTests(TestCase):
    """Tests for Share.get_context() — does NOT cover get_related_shares()."""

    def setUp(self):
        self.address = Address.objects.create(name="Muster", first_name="Hans")
        self.share_type = ShareType.objects.create(
            name="TestType", standard_interest=Decimal("2.50")
        )
        self.building = Building.objects.create(name="Test Building")
        self.rental_unit = RentalUnit.objects.create(
            name="101", rental_type="Wohnung", building=self.building
        )
        self.contract = Contract.objects.create(date=date(2020, 1, 1), date_end=date(2100, 1, 1))
        self.contract.rental_units.set([self.rental_unit])
        self.contract.contractors.set([self.address])

    def test_basic_context_with_all_fields_with_contract(self):
        """All populated fields appear correctly formatted in the context (with contract)."""
        # Only one of building or contract can be attached (DB constraint),
        # here we test an attached contract.
        self._check_all_populated_fields(attached_to_building=False)

    def test_basic_context_with_all_fields_with_building(self):
        """All populated fields appear correctly formatted in the context (with building)."""
        # Only one of building or contract can be attached (DB constraint),
        # here we test an attached building.
        self._check_all_populated_fields(attached_to_building=True)

    def _check_all_populated_fields(self, attached_to_building):
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 6, 15),
            repayment_date=date(2025, 6, 15),
            effective_from=date(2020, 7, 1),
            effective_until=date(2025, 5, 31),
            duration=5,
            quantity=3,
            value=Decimal("1000.00"),
            interest_mode="Manual",
            manual_interest=Decimal("3.75"),
            is_interest_credit=True,
            is_pension_fund=True,
            is_business=True,
            date_due=date(2025, 6, 15),
            note="Test note",
            identifier="AS-001",
            identifier_external="EXT-001",
            attached_to_building=None,
            attached_to_contract=self.contract,
        )
        if attached_to_building:
            share.attached_to_building = self.building
            share.attached_to_contract = None
            share.save()
        ctx = share.get_context()

        self.assertEqual(ctx["share_type"], "TestType")
        self.assertEqual(ctx["quantity"], 3)
        self.assertEqual(ctx["value"], "1'000.00")
        self.assertEqual(ctx["value_total"], "3'000.00")
        self.assertTrue(ctx["is_pension_fund"])
        self.assertTrue(ctx["is_business"])
        self.assertEqual(ctx["date"], "01.07.2020")
        self.assertEqual(ctx["date_end"], "31.05.2025")
        self.assertEqual(ctx["payment_date"], "15.06.2020")
        self.assertEqual(ctx["repayment_date"], "15.06.2025")
        self.assertEqual(ctx["date_due"], "15.06.2025")
        self.assertEqual(ctx["interest"], "3.75")
        self.assertEqual(ctx["interest_mode"], "Manual")
        self.assertEqual(ctx["manual_interest"], "3.75")
        self.assertTrue(ctx["is_interest_credit"])
        self.assertEqual(ctx["duration"], 5)
        self.assertEqual(ctx["note"], "Test note")
        self.assertEqual(ctx["identifier"], "AS-001")
        self.assertEqual(ctx["identifier_external"], "EXT-001")
        if attached_to_building:
            self.assertEqual(ctx["related_building"], "Test Building")
            self.assertEqual(ctx["related_contract"], {})
        else:
            self.assertEqual(ctx["related_building"], "")
            self.assertIn("Vertragsbeginn", ctx["related_contract"])

    def test_null_dates_return_empty_strings(self):
        """When date fields are None, the context contains empty strings."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("500"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["date_end"], "")
        self.assertEqual(ctx["repayment_date"], "")
        self.assertEqual(ctx["date_due"], "")

    def test_interest_mode_standard_uses_share_type_rate(self):
        """Interest value comes from share_type when mode is Standard."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
            interest_mode="Standard",
            manual_interest=Decimal("9.99"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["interest"], "2.50")
        self.assertEqual(ctx["interest_mode"], "Standard")

    def test_interest_mode_manual_uses_manual_rate(self):
        """Interest value comes from manual_interest when mode is Manual."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
            interest_mode="Manual",
            manual_interest=Decimal("4.50"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["interest"], "4.50")

    def test_payment_state_gefordert(self):
        """Future payment date means payment_state is 'gefordert'."""
        future = date.today() + timedelta(days=1)
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=future,
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["payment_state"], "gefordert")

    def test_payment_state_bezahlt(self):
        """Past payment date without repayment means 'bezahlt'."""
        past = date.today() - timedelta(days=1)
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=past,
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["payment_state"], "bezahlt")

    def test_payment_state_zurueckgezahlt(self):
        """Past repayment date means 'zurückgezahlt'."""
        past = date.today() - timedelta(days=1)
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=past - timedelta(days=10),
            repayment_date=past,
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["payment_state"], "zurückgezahlt")

    def test_related_building_present(self):
        """attached_to_building is reflected in related_building."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
            attached_to_building=self.building,
        )
        ctx = share.get_context()

        self.assertEqual(ctx["related_building"], "Test Building")

    def test_related_contract_present(self):
        """attached_to_contract is reflected in related_contract."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
            attached_to_contract=self.contract,
        )
        ctx = share.get_context()

        self.assertIn("Vertragsbeginn", ctx["related_contract"])
        self.assertEqual(ctx["related_contract"]["Vertragsbeginn"], "01.01.2020")

    def test_no_related_building_or_contract(self):
        """When nothing is attached, related fields are empty."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["related_building"], "")
        self.assertEqual(ctx["related_contract"], {})

    def test_include_related_shares_false_by_default(self):
        """By default, related_shares is NOT in the context."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertNotIn("related_shares", ctx)

    @patch.object(Share, "get_related_shares", return_value={"mocked": True})
    def test_include_related_shares_true_adds_key(self, mock_get_related):
        """When include_related_shares=True, the key is present."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
        )
        ctx = share.get_context(include_related_shares=True)

        self.assertIn("related_shares", ctx)
        self.assertEqual(ctx["related_shares"], {"mocked": True})
        mock_get_related.assert_called_once()

    def test_value_total_when_quantity_is_zero(self):
        """When quantity is 0, value_total returns '-' (from the property)."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
            quantity=0,
        )
        ctx = share.get_context()

        self.assertEqual(ctx["value_total"], "-")

    def test_date_fallback_to_payment_date(self):
        """When effective_from is None, date falls back to payment_date."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2019, 3, 10),
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["date"], "10.03.2019")

    def test_date_end_fallback_to_repayment_date(self):
        """When effective_until is None, date_end falls back to repayment_date."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            repayment_date=date(2024, 12, 31),
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["date_end"], "31.12.2024")

    def test_date_end_empty_when_no_repayment_or_effective_until(self):
        """When both effective_until and repayment_date are None, date_end is empty."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        self.assertEqual(ctx["date_end"], "")

    def test_context_keys_are_complete(self):
        """The returned dict contains all expected keys."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type,
            payment_date=date(2020, 1, 1),
            value=Decimal("1000"),
        )
        ctx = share.get_context()

        expected_keys = {
            "share_type",
            "quantity",
            "value",
            "value_total",
            "is_pension_fund",
            "is_business",
            "date",
            "date_end",
            "payment_date",
            "repayment_date",
            "date_due",
            "interest",
            "interest_mode",
            "manual_interest",
            "is_interest_credit",
            "duration",
            "payment_state",
            "note",
            "identifier",
            "identifier_external",
            "related_building",
            "related_contract",
        }
        self.assertTrue(expected_keys.issubset(ctx.keys()))


class ShareGetRelatedSharesTest(TestCase):
    """Tests for Share.get_related_shares()."""

    @classmethod
    def setUpTestData(cls):
        cls.address = Address.objects.create(
            name="Muster", first_name="Hans", email="hans@example.com"
        )
        cls.other_address = Address.objects.create(
            name="Andere", first_name="Anna", email="anna@example.com"
        )
        cls.share_type_a = ShareType.objects.create(name="Anteilschein")
        cls.share_type_b = ShareType.objects.create(
            name="Darlehen verzinst", standard_interest=1.5
        )
        cls.building = Building.objects.create(name="Musterweg 1")

    def test_single_active_share(self):
        """A single active share appears in shares_by_type and totals."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
            quantity=2,
        )
        result = share.get_related_shares()
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 1)
        self.assertEqual(result["total_shares_by_type"][self.share_type_a.name]["quantity"], 2)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "2'000.00"
        )

    def test_no_shares_returns_empty_if_self_not_included(self):
        """When the address has no shares, all share types have empty lists."""
        share = Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
        )
        result = share.get_related_shares(include_self=False)
        self.assertIn("shares_by_type", result)
        self.assertIn("total_shares_by_type", result)
        self.assertEqual(result["shares_pension_fund"], [])
        self.assertEqual(result["total_shares_pension_fund"]["quantity"], 0)
        self.assertEqual(result["total_shares_pension_fund"]["value"], "0.00")
        # All share types should have empty lists and zero totals
        for st_name, shares in result["shares_by_type"].items():
            self.assertEqual(shares, [], f"Expected empty list for {st_name}")
        for st_name, totals in result["total_shares_by_type"].items():
            self.assertEqual(totals["quantity"], 0, f"Expected quantity 0 for {st_name}")
            self.assertEqual(totals["value"], "0.00", f"Expected value 0.00 for {st_name}")

    def test_multiple_shares_same_type(self):
        """Multiple shares of the same type are aggregated in totals."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
            quantity=1,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2001, 1, 1),
            value=500,
            quantity=2,
        )
        # Use any share to call get_related_shares
        share = Share.objects.first()
        result = share.get_related_shares()
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 2)
        self.assertEqual(result["total_shares_by_type"][self.share_type_a.name]["quantity"], 3)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "2'000.00"
        )

    def test_multiple_shares_same_type_self_not_included(self):
        """Multiple shares of the same type are aggregated in totals."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
            quantity=1,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2001, 1, 1),
            value=500,
            quantity=2,
        )
        # Use any share to call get_related_shares
        share = Share.objects.first()
        result = share.get_related_shares(include_self=False)
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 1)
        self.assertEqual(result["total_shares_by_type"][self.share_type_a.name]["quantity"], 2)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "1'000.00"
        )

    def test_multiple_share_types(self):
        """Shares of different types are grouped separately."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_b,
            payment_date=date(2000, 1, 1),
            value=5000,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 1)
        self.assertEqual(len(result["shares_by_type"][self.share_type_b.name]), 1)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "1'000.00"
        )
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_b.name]["value"], "5'000.00"
        )

    def test_pension_fund_shares_separated(self):
        """Pension fund shares appear in both shares_by_type and shares_pension_fund."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
            is_pension_fund=True,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2001, 1, 1),
            value=2000,
            is_pension_fund=False,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 2)
        self.assertEqual(len(result["shares_pension_fund"]), 1)
        self.assertEqual(result["total_shares_pension_fund"]["quantity"], 1)
        self.assertEqual(result["total_shares_pension_fund"]["value"], "1'000.00")

    def test_inactive_shares_excluded(self):
        """Shares with repayment_date in the past are inactive and excluded."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            repayment_date=date(2000, 6, 1),
            value=1000,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=2000,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        # Only the second share is active (no repayment_date)
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 1)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "2'000.00"
        )

    def test_other_address_shares_excluded(self):
        """Shares belonging to a different address are not included."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
        )
        Share.objects.create(
            name=self.other_address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=5000,
        )
        share = Share.objects.filter(name=self.address).first()
        result = share.get_related_shares()
        self.assertEqual(len(result["shares_by_type"][self.share_type_a.name]), 1)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "1'000.00"
        )

    def test_related_building_collected(self):
        """Shares attached to a building collect the building name."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
            attached_to_building=self.building,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        totals = result["total_shares_by_type"][self.share_type_a.name]
        self.assertEqual(totals["related_buildings"], ["Musterweg 1"])

    def test_ordering_by_payment_date(self):
        """Shares are ordered by Coalesce(effective_from, payment_date)."""
        _share_later = Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2005, 1, 1),
            value=500,
        )
        _share_earlier = Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        contexts = result["shares_by_type"][self.share_type_a.name]
        self.assertEqual(contexts[0]["payment_date"], "01.01.2000")
        self.assertEqual(contexts[1]["payment_date"], "01.01.2005")

    def test_ordering_by_effective_from(self):
        """Shares with effective_from override payment_date for ordering."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2005, 1, 1),
            effective_from=date(1999, 1, 1),
            value=500,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        contexts = result["shares_by_type"][self.share_type_a.name]
        # The first share has effective_from=1999, so it should come first
        self.assertEqual(contexts[0]["date"], "01.01.1999")
        self.assertEqual(contexts[1]["date"], "01.01.2000")

    def test_related_contracts_and_rental_units(self):
        """Shares attached to contracts collect contract and rental unit info."""
        rental_unit = RentalUnit.objects.create(
            name="101",
            rental_type="Wohnung",
            building=self.building,
        )
        contract = Contract.objects.create(
            date=date(2000, 1, 1),
        )
        contract.rental_units.set([rental_unit])
        contract.contractors.set([self.address])
        contract.save()
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
            attached_to_contract=contract,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        totals = result["total_shares_by_type"][self.share_type_a.name]
        self.assertEqual(len(totals["related_contracts"]), 1)
        self.assertEqual(len(totals["related_rental_units"]), 1)

    def test_empty_share_type_has_zero_totals(self):
        """Share types with no matching shares still appear with zero totals."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=1000,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        # share_type_b has no shares for this address
        self.assertEqual(result["shares_by_type"][self.share_type_b.name], [])
        self.assertEqual(result["total_shares_by_type"][self.share_type_b.name]["quantity"], 0)
        self.assertEqual(result["total_shares_by_type"][self.share_type_b.name]["value"], "0.00")

    def test_quantity_greater_than_one(self):
        """Totals correctly multiply quantity by value."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_a,
            payment_date=date(2000, 1, 1),
            value=500,
            quantity=3,
        )
        share = Share.objects.first()
        result = share.get_related_shares()
        self.assertEqual(result["total_shares_by_type"][self.share_type_a.name]["quantity"], 3)
        self.assertEqual(
            result["total_shares_by_type"][self.share_type_a.name]["value"], "1'500.00"
        )
