from datetime import date
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse

from geno.models import Address, InvoiceCategory, Member, RegistrationEvent

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
    def test_registration_link_not_found(self, mock_reverse):
        event = RegistrationEvent.objects.create(name="Test Event", publication_type="public")
        self.assertEqual(
            event.registration_link,
            f"[Fehler: Keine URL für '{self.registration_form_viewname}' gefunden]",
        )
