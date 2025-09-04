from django.conf import settings

from geno.models import Address
from geno.utils import make_username, send_error_mail, send_info_mail

from .base import BaseTestCase


class TestUtils(BaseTestCase):
    def test_send_error_mail(self):
        send_error_mail("Test", "Error message", Exception("Test-Exception"))
        self.assertEmailSent(
            1,
            f"{settings.EMAIL_SUBJECT_PREFIX}ERROR: Test",
            "Error message\n\nException:\nTest-Exception",
            settings.ADMINS[0][1],
        )

    def test_send_info_mail(self):
        send_info_mail("Test", "Info message")
        self.assertEmailSent(
            1, f"{settings.EMAIL_SUBJECT_PREFIX}INFO: Test", "Info message", settings.ADMINS[0][1]
        )

    def test_make_username(self):
        adr = Address()
        self.assertEqual(make_username(adr), None)

        adr.save()
        self.assertEqual(make_username(adr), f"adr{adr.id}")

        adr = Address(name="Müller", first_name="")
        self.assertEqual(make_username(adr), "mueller")

        adr = Address(name="", first_name="Hans")
        self.assertEqual(make_username(adr), "hans")

        adr = Address(organization="Org", name="", first_name="")
        self.assertEqual(make_username(adr), "org")

        adr = Address(organization="Org", name="Müller", first_name="Hans")
        self.assertEqual(make_username(adr), "hans.mueller.org")

        adr = Address(name="Müller", first_name="Hans")
        self.assertEqual(make_username(adr), "hans.mueller")

        adr = Address(name="Müller", first_name="Hans Rudolf")
        self.assertEqual(make_username(adr), "hans.mueller")

        adr = Address(name="Müller", first_name="Hans-Rudolf")
        self.assertEqual(make_username(adr), "hansrudolf.mueller")

        adr = Address(name="Müller (123)", first_name="Hans (234)")
        self.assertEqual(make_username(adr), "hans.mueller123")

        adr = Address(name="Mü+ll-er", first_name="Ha_ns")
        self.assertEqual(make_username(adr), "hans.mueller")

        self.UserModel.objects.create(username="hans.mueller")
        suffix = 2
        while suffix < 20:
            self.assertEqual(make_username(adr), f"hans.mueller{suffix}")
            self.UserModel.objects.create(username=f"hans.mueller{suffix}")
            suffix += 1
        with self.assertRaisesRegex(RuntimeError, r"^Too many equal usernames"):
            make_username(adr)
