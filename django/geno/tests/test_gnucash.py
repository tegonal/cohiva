import os

from geno.gnucash import build_structured_qrbill_address, create_qrbill, get_book, get_reference_nr
from geno.models import Address

from .base import BaseTestCase, GenoAdminTestCase


class TestGnucash(BaseTestCase):
    def test_open_book(self):
        msg = []
        book = get_book(msg)
        self.assertIsNotNone(book, " ".join(msg))

    ## TODO: Test create_qrbill after moving send-mail code to separate util class

    ## TODO: Test send mail with recipients that include commas, parentheses and utf8 chars
    # https://github.com/anymail/django-anymail/issues/369


class TestQRBill(GenoAdminTestCase):
    def test_build_structured_qrbill_address(self):
        ret = build_structured_qrbill_address({"return": "same if dict"})
        self.assertEqual(ret, {"return": "same if dict"})
        with self.assertRaises(TypeError):
            build_structured_qrbill_address(None)
        adr = Address(
            organization="Org",
            first_name="Hans",
            name="Muster",
            street_name="Musterweg",
            house_number="1",
            city_name="Test",
            city_zipcode="12345",
            country="Schweiz",
        )
        ret = build_structured_qrbill_address(adr)
        self.assertEqual(
            ret,
            {
                "name": "Org",
                "street": adr.street_name,
                "house_num": adr.house_number,
                "pcode": adr.city_zipcode,
                "city": adr.city_name,
                "country": "CH",
            },
        )
        adr.organization = None
        ret = build_structured_qrbill_address(adr)
        self.assertEqual(
            ret,
            {
                "name": "Hans Muster",
                "street": adr.street_name,
                "house_num": adr.house_number,
                "pcode": adr.city_zipcode,
                "city": adr.city_name,
                "country": "CH",
            },
        )

        adr.country = "Deutschland"
        ret = build_structured_qrbill_address(adr)
        self.assertEqual(
            ret,
            {
                "name": "Hans Muster",
                "street": adr.street_name,
                "house_num": adr.house_number,
                "pcode": adr.city_zipcode,
                "city": adr.city_name,
                "country": "DE",
            },
        )

    def test_create_qrbill_address(self):
        ref_number = "999"
        context = {}
        adr = Address(
            organization="Org",
            first_name="Hans",
            name="Muster",
            street_name="Musterweg",
            house_number="1",
            city_name="Berlin",
            city_zipcode="12345",
            country="Deutschland",
        )
        output_filename = "test_create_qrbill.pdf"
        outfile = f"/tmp/{output_filename}"
        if os.path.isfile(outfile):
            os.remove(outfile)
        msg, nsent, recipient = create_qrbill(
            ref_number, adr, context, output_filename, render=True
        )
        self.assertEqual(
            msg[0],
            "Konnte QR-Rechnung nicht erstellen: render_qrbill(): "
            "'qr_amount' not found in context.",
        )

        context["qr_amount"] = "99.99"
        context["qr_extra_info"] = "Extrainfo"
        msg, nsent, recipient = create_qrbill(
            ref_number, adr, context, output_filename, render=True
        )
        self.assertEqual(
            msg[0], "Konnte QR-Rechnung nicht erstellen: The reference number is invalid"
        )

        ref_number = get_reference_nr(self.invoicecategories[0], 999)
        msg, nsent, recipient = create_qrbill(
            ref_number, adr, context, output_filename, render=True
        )
        self.assertEqual(msg, [])
        self.assertEqual(nsent, 0)
        self.assertEqual(recipient, None)
        self.assertInPDF(outfile, "Zahlbar durch\nOrg\nMusterweg 1\nDE-12345 Berlin")
