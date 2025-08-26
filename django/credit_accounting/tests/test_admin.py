# import re
import datetime
from decimal import Decimal

# from django.conf import settings
# from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

# from django.test import Client
from django.template import loader

# from urllib.parse import quote
from django.urls import reverse

from credit_accounting.models import Account, Transaction

# from geno.models import Address
from geno.gnucash import get_reference_nr

# from credit_accounting.models import CreditAccountingObject
from .base import CreditAccountingTestCase


class CreditAccountingAdminTest(CreditAccountingTestCase):
    # @classmethod
    # def setUpTestData(cls):
    #    super().setUpTestData()
    #    cls.api_base_url = "/api/v1"

    def test_views_status200(self):
        logged_in = self.client.login(username="superuser", password="secret")
        self.assertTrue(logged_in)
        paths = [
            "",
            "add/",
            "upload/",
            "accounts/",
            "accounts/add/",
            f"accounts/edit/{self.credit_accounts[0].id}/",
            f"accounts/qrbill/{self.credit_accounts[0].id}/",
            "login_required/",
            "report/",
            "report/salesbyaccount/",
        ]
        for path in paths:
            response = self.client.get(f"/credit_accounting/{path}")
            self.assertEqual(response.status_code, 200)

    def generate_camt053_data(self):
        template = loader.get_template("geno/camt053_demo_data.xml")
        context = {"payments": []}
        date = datetime.date.today().strftime("%Y-%m-%d")
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        comment = "Test Einzahlung"
        amount = 100
        for account in Account.objects.all():
            info = {}
            info["iban"] = "CH6431961000004421557"
            info["refnr"] = get_reference_nr(
                "app", account.pk, extra_id1=1, app_name="credit_accounting"
            ).replace(" ", "")
            info["transaction_id"] = f"TEST_{info['refnr']}_{ts}"
            info["date"] = date
            info["comment"] = comment
            info["amount"] = format(amount, ".2f")
            info["debtor_name"] = str(account.name)
            amount += 50
            context["payments"].append(info)
        return template.render(context)

    def test_transaction_upload_view(self):
        logged_in = self.client.login(username="superuser", password="secret")
        self.assertTrue(logged_in)

        url = reverse("transaction-upload")

        ## No file
        response = self.client.post(url)
        self.assertContains(
            response, '<li class="error">Konnte Datei nicht hochladen.</li>', html=True
        )

        ## Invalid file
        invalid_file = SimpleUploadedFile(
            "invalid_upload.xml", b"INVALID CONTENT", content_type="application/xml"
        )
        response = self.client.post(url, {"file": invalid_file})
        self.assertContains(
            response,
            '<li class="error">Konnte Datei nicht verarbeiten: SEPA parser error',
            html=False,
        )

        ## Test data
        camt053_data = self.generate_camt053_data()
        camt053_file = SimpleUploadedFile(
            "camt053_upload.xml", str.encode(camt053_data), content_type="application/xml"
        )
        response = self.client.post(url, {"file": camt053_file})
        self.assertContains(
            response, '<b class="success">5 Buchungen wurden importiert:</b>', html=True
        )

        self.assertEqual(Transaction.objects.filter(account__vendor=self.vendors[0]).count(), 3)
        self.assertEqual(Transaction.objects.filter(account__vendor=self.vendors[1]).count(), 2)
        acc = Account.objects.get(id=self.credit_accounts[2].id)
        self.assertEqual(acc.balance, Decimal(200))
