from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail

from geno.gnucash import render_qrbill
from geno.models import Address

from .base import CreditAccountingTestCase


def patch_render_qrbill(dummy, context, output_pdf_file, base_pdf_file):
    return render_qrbill(
        None,
        context,
        output_pdf_file,
        base_pdf_file=f"{settings.BASE_DIR}/credit_accounting/templates/credit_accounting/Depot8_Einzahlung.pdf",
    )


class AccountTests(CreditAccountingTestCase):
    @patch("credit_accounting.models.render_qrbill", wraps=patch_render_qrbill)
    def test_notify_user(self, mock_render_qrbill):
        user = User.objects.create(
            last_name="Muster", first_name="Hans", username="testuser", email="test@example.com"
        )
        Address.objects.create(
            name="Muster",
            first_name="Hans",
            email="test@example.com",
            street_name="Musterwg",
            house_number="1",
            city_zipcode="3000",
            city_name="Bern",
            user=user,
        )

        with self.assertRaises(
            ValueError, msg="Unknown notification_name: invalid_notification_name"
        ):
            self.credit_accounts[0].notify_user("invalid_notification_name", user)

        self.credit_accounts[0].notify_user(
            "notification_balance_below_amount", user, context={"threshold": 50.00}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            "Vendor1: Saldolimite unterschritten (Konto V1_Acc1)", mail.outbox[0].subject
        )
        self.assertEqual(settings.COHIVA_APP_EMAIL_SENDER, mail.outbox[0].from_email)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "QR_Rechnung_Vendor1_V1_Acc1.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
