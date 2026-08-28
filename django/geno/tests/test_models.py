from datetime import date, datetime
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse

from geno.models import Address, Contract, InvoiceCategory, Member, RegistrationEvent

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

    def test_is_member(self):
        adr = Address.objects.create(name="Test")
        self.assertFalse(adr.is_member())

        m1 = Member.objects.create(name=adr, date_join=date(2000, 1, 1))
        self.assertTrue(adr.is_member())
        self.assertTrue(adr.is_member(date_mode="last_year"))
        self.assertTrue(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertTrue(adr.is_member(date=date(date.today().year + 1, 1, 2)))

        m1.date_leave = date(date.today().year + 1, 1, 1)
        m1.save()
        self.assertTrue(adr.is_member())
        self.assertTrue(adr.is_member(date_mode="last_year"))
        self.assertFalse(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertFalse(adr.is_member(date=date(date.today().year + 1, 1, 2)))

        m1.date_join = date(date.today().year, 1, 1)
        m1.save()
        self.assertTrue(adr.is_member())
        self.assertFalse(adr.is_member(date_mode="last_year"))
        self.assertFalse(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertFalse(adr.is_member(date=date(date.today().year + 1, 1, 2)))

        m1.date_leave = None
        m1.save()
        self.assertTrue(adr.is_member())
        self.assertFalse(adr.is_member(date_mode="last_year"))
        self.assertTrue(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertTrue(adr.is_member(date=date(date.today().year + 1, 1, 2)))

        Member.objects.create(name=adr, date_join=date(1995, 1, 1), date_leave=date(1998, 6, 1))
        self.assertTrue(adr.is_member())
        self.assertFalse(adr.is_member(date_mode="last_year"))
        self.assertTrue(adr.is_member(date_mode="end_date"))
        self.assertFalse(adr.is_member(date=date(1999, 12, 31)))
        self.assertTrue(adr.is_member(date=date(date.today().year + 1, 1, 2)))
        self.assertTrue(adr.is_member(date=date(1997, 12, 31)))
        self.assertTrue(adr.is_member(date=datetime(1997, 12, 31, 1, 1, 1)))

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
