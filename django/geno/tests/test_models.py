from datetime import date
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse

from geno.models import (
    Address,
    BankAccount,
    Building,
    Child,
    Contract,
    InvoiceCategory,
    Member,
    RegistrationEvent,
    RentalUnit,
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

    def test_import_id_already_none_stays_none(self):
        building = Building.objects.create(name="Building B")
        rental_unit = RentalUnit.objects.create(
            name="B1", rental_type="Wohnung", building=building
        )
        self.assertIsNone(rental_unit.import_id)

        rental_unit.save_as_copy()

        self.assertIsNotNone(rental_unit.pk)
        self.assertIsNone(rental_unit.import_id)

    def test_model_without_import_id_field_is_unaffected(self):
        # BankAccount has no `import_id` field at all, so the
        # `hasattr(self, "import_id")` check must simply be skipped
        # without raising an error.
        account = BankAccount.objects.create(
            iban="CH00 0000 0000 0000 0000 0", account_holders="Hans Muster"
        )
        original_pk = account.pk

        account.save_as_copy()

        self.assertIsNotNone(account.pk)
        self.assertNotEqual(account.pk, original_pk)
        self.assertFalse(hasattr(account, "import_id"))
        self.assertEqual(account.iban, "CH00 0000 0000 0000 0000 0")

    def test_import_id_cleared_even_when_name_is_not_a_string(self):
        # Child.name is a OneToOneField to Address (not a string), so the
        # "[KOPIE]" suffix logic must not touch it, but import_id must
        # still be cleared independently. save() is mocked out to isolate
        # the attribute mutations from the OneToOneField uniqueness
        # constraint on `name`, which would otherwise reject a second row
        # pointing at the same Address.
        address = Address.objects.create(name="Kind", first_name="Klein")
        child = Child.objects.create(name=address, presence=5.0, import_id="CHILD-1")

        with patch.object(Child, "save"):
            child.save_as_copy()

        self.assertEqual(child.name, address)
        self.assertIsNone(child.import_id)


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

    def test_save_as_copy_without_import_id_leaves_it_none(self):
        contract = Contract.objects.create(date=date(2024, 2, 1))
        contract.contractors.set([self.contractor])

        contract.save_as_copy()

        self.assertIsNone(contract.import_id)
        self.assertEqual(list(contract.contractors.all()), [self.contractor])
