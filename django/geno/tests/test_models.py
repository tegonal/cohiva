import django
from django.conf import settings
from django.test import TestCase

if django.VERSION < (3, 0):
    from django.db import OperationalError as IntegrityError
else:
    from django.db.utils import IntegrityError
from django.test import override_settings

from geno.models import Address, InvoiceCategory


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
