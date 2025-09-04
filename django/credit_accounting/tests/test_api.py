# import re
import datetime

# from urllib.parse import quote
# from django.conf import settings
# from django.core import mail
# from django.test import Client
# from geno.models import Address
from credit_accounting.models import Account, Transaction

# from credit_accounting.models import CreditAccountingObject
from .base import CreditAccountingTestCase


class CreditAccountingApiTest(CreditAccountingTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.api_base_url = "/api/v1"

    def test_api_pos_accounts(self):
        params = {"vendor": "invalid", "secret": self.vendors[0].api_secret}
        response = self.client.get(f"{self.api_base_url}/credit_accounting/pos/accounts/", params)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Invalid vendor." in response.content.decode())

        params = {"vendor": self.vendors[0].name, "secret": "invalid"}
        response = self.client.get(f"{self.api_base_url}/credit_accounting/pos/accounts/", params)
        self.assertEqual(response.status_code, 401)
        self.assertEqual("Falsche Anmeldedaten.", response.json()["detail"])

        params = {"vendor": self.vendors[0].name, "secret": self.vendors[0].api_secret}
        response = self.client.get(f"{self.api_base_url}/credit_accounting/pos/accounts/", params)
        # print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "OK")
        self.assertEqual(
            len(data["accounts"]),
            Account.objects.filter(active=True, vendor=self.vendors[0]).count(),
        )
        self.assertEqual(data["accounts"][self.credit_accounts[0].pin]["balance"], 0.0)

    def test_api_pos_transaction(self):
        transaction = {
            "name": "Test",
            "account": self.credit_accounts[0].pin,
            "amount": 123.45,
            "note": "test_api_pos_transaction",
            "date": datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            "id": "tx_001",
        }
        post_data = {"vendor": self.vendors[0].name, "secret": self.vendors[0].api_secret}
        post_data.update(transaction)
        response = self.client.post(
            f"{self.api_base_url}/credit_accounting/pos/transaction/", post_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")

        account = Account.objects.get(id=self.credit_accounts[0].id)
        self.assertEqual(str(account.balance), "123.45")

        response = self.client.post(
            f"{self.api_base_url}/credit_accounting/pos/transaction/", post_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Duplicate")

        post_data["id"] = "tx_002"
        response = self.client.post(
            f"{self.api_base_url}/credit_accounting/pos/transaction/", post_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")

        account = Account.objects.get(id=self.credit_accounts[0].id)
        self.assertEqual(str(account.balance), "246.90")
        self.assertEqual(Transaction.objects.all().count(), 2)
