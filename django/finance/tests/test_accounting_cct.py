from unittest.mock import ANY, Mock, call, patch

from django.conf import settings
from django.test import TestCase

from finance.accounting import (
    Account,
    AccountingManager,
    CashctrlBook,
)


class CashctrlBookTestCase(TestCase):

    cohiva_test_endpoint = "https://cohiva-test.cashctrl123.com/api/v1/"
    endpoint_is_mocked = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AccountingManager.default_backend_label = "cashctrl_test"
        cls.account1 = Account("TestAccount CashCtrl1", "43000")
        cls.account2 = Account("TestAccount CashCtrl2", "10220")
        cls.account3 = Account("TestAccount CashCtrl3", "47400")

    @staticmethod
    def fetch_account_responses(url, **kw):
        if "journal/read.json" in str(url):
            return Mock(json=lambda: {"success":True,"data":{"id":801,"created":"2025-11-04 18:04:50.0","createdBy":"API:jAYc","lastUpdated":"2025-11-04 18:04:50.0","lastUpdatedBy":"API:jAYc","creditId":1237,"debitId":1477,"items":[],"attachments":[],"allocations":[],"type":"MANUAL","dateAdded":"2025-11-04 18:07:00.0","title":"Test CashCtrl add_transaction","notes":"Added through API","amount":100,"currencyRate":1,"accountIds":"[\"1237\",\"1477\"]","itemsIndex":"","itemsCount":0,"attachmentCount":0,"allocationCount":0,"taxedItems":[],"defaultCurrencyAmount":100,"defaultCurrencyTaxAmount":0,"netAmount":100,"defaultCurrencyNetAmount":100,"associates":[],"taxAmount":0}}, status_code=200)
        elif "account/list.json" in str(url):
            if "43000" in str(url):
                return Mock(json=lambda: {"success": True,"data":[{'accountClass': 'EXPENSE', 'allocationCount': 0, 'attachmentCount': 0, 'categoryDisplay': 'Liegenschaftsaufwand', 'categoryId': 412, 'costCenterIds': None, 'costCenterNumbers': None, 'created': '2025-10-22 15:18:30.0', 'createdBy': 'API:jAYc', 'currencyCode': 'CHF', 'currencyId': None, 'custom': None, 'defaultCurrencyEndAmount': 300, 'defaultCurrencyOpeningAmount': 0, 'endAmount': 300, 'id': 1477, 'isBankAccount': False, 'isInSalaryType': False, 'isInactive': False, 'lastUpdated': '2025-10-22 15:18:30.0', 'lastUpdatedBy': 'API:jAYc', 'name': 'Unterhalt und Reparatur', 'notes': None, 'number': '43000', 'openingAmount': 0, 'targetDisplay': None, 'targetMax': None, 'targetMin': None, 'taxId': None, 'taxName': None}]}, status_code=200)
            elif "10220" in str(url):
                return Mock(json=lambda: {"success": True,"data":[{'accountClass': 'ASSET', 'allocationCount': 0, 'attachmentCount': 0, 'categoryDisplay': 'Liquide Mittel', 'categoryId': 372, 'costCenterIds': None, 'costCenterNumbers': None, 'created': '2025-10-22 15:16:07.0', 'createdBy': 'API:jAYc', 'currencyCode': 'CHF', 'currencyId': None, 'custom': None, 'defaultCurrencyEndAmount': 300, 'defaultCurrencyOpeningAmount': 0, 'endAmount': 300, 'id': 1237, 'isBankAccount': False, 'isInSalaryType': False, 'isInactive': False, 'lastUpdated': '2025-10-22 15:16:07.0', 'lastUpdatedBy': 'API:jAYc', 'name': 'ABS XXXZZZ', 'notes': None, 'number': '10220', 'openingAmount': 0, 'targetDisplay': None, 'targetMax': None, 'targetMin': None, 'taxId': None, 'taxName': None}]}, status_code=200)
            elif "47400" in str(url):
                return Mock(json=lambda: {"success": True,"data":[{'accountClass': 'EXPENSE', 'allocationCount': 0, 'attachmentCount': 0, 'categoryDisplay': 'Büro- & Verwaltungsaufwand', 'categoryId': 415, 'costCenterIds': None, 'costCenterNumbers': None, 'created': '2025-10-22 15:18:41.0', 'createdBy': 'API:jAYc', 'currencyCode': 'CHF', 'currencyId': None, 'custom': None, 'defaultCurrencyEndAmount': -600, 'defaultCurrencyOpeningAmount': 0, 'endAmount': -600, 'id': 1497, 'isBankAccount': False, 'isInSalaryType': False, 'isInactive': False, 'lastUpdated': '2025-10-22 15:18:41.0', 'lastUpdatedBy': 'API:jAYc', 'name': 'Telefon', 'notes': None, 'number': '47400', 'openingAmount': 0, 'targetDisplay': None, 'targetMax': None, 'targetMin': None, 'taxId': None, 'taxName': None}]}, status_code=200)
            return Exception("Unknown account number in URL")

    @staticmethod
    def fetch_transaction_responses(url, **kw):
        return Mock(json=lambda: {"success": True,"data":[{}]}, status_code=200)

    @classmethod
    def tearDownClass(cls):
        AccountingManager.default_backend_label = settings.FINANCIAL_ACCOUNTING_DEFAULT_BACKEND
        super().tearDownClass()

    def test_get_book(self):
        messages = []
        with AccountingManager(messages) as book:
            self.assertTrue(isinstance(book, CashctrlBook))
            self.assertEqual(len(messages), 0)

    @patch("finance.accounting.cashctrl.requests.get")
    @patch("finance.accounting.cashctrl.requests.post")
    def test_add_transaction(self, mock_post, mock_get):
        messages = []
        with AccountingManager(messages) as book:
            # configure fake responses
            mock_get.return_value.raise_for_status.side_effect = None
            mock_get.side_effect = self.fetch_account_responses

            mock_post.return_value.json.return_value = {
                "success": True,
                "message": "Buchung gespeichert",
                "insertId": 700,
            }
            mock_post.return_value.raise_for_status.side_effect = None

            transaction_id = book.add_transaction(
                100.00, self.account1, self.account2, "2026-01-01", "Test CashCtrl add_transaction", autosave=False
            )
            self.assertTrue(transaction_id.startswith("cct_"))
            self.assertEqual("cct_0_700", transaction_id)
            book.save()

            # verify that the API was called
            mock_get.assert_has_calls([
                call(f"{self.cohiva_test_endpoint}account/list.json?filter=%5B%7B%22comparison%22%3A+%22eq%22%2C+%22field%22%3A+%22number%22%2C+%22value%22%3A+%2243000%22%7D%5D", auth=ANY),
                call(f"{self.cohiva_test_endpoint}account/list.json?filter=%5B%7B%22comparison%22%3A+%22eq%22%2C+%22field%22%3A+%22number%22%2C+%22value%22%3A+%2210220%22%7D%5D", auth=ANY)
            ])
            called_url = mock_post.call_args[0][0]
            assert f"{self.cohiva_test_endpoint}journal/create.json?amount%3D100.0%26creditId%3D1237%26debitId%3D1477%26title%3DTest%2BCashCtrl%2Badd_transaction" in called_url

    @patch("finance.accounting.cashctrl.requests.get")
    @patch("finance.accounting.cashctrl.requests.post")
    def test_add_transaction_no_commit(self, mock_post, mock_get):
        messages = []
        with AccountingManager(messages) as book:
            # configure fake responses
            mock_get.return_value.raise_for_status.side_effect = None
            mock_get.side_effect = self.fetch_account_responses

            mock_post.return_value.json.return_value = {
                "success": True,
                "message": "Buchung gespeichert",
                "insertId": 801,
            }
            mock_post.return_value.raise_for_status.side_effect = None

            transaction_id = book.add_transaction(
                100.00, self.account1, self.account2, "2026-01-01", "Test CashCtrl add_transaction_no_commit", autosave=False
            )

            self.assertTrue(transaction_id.startswith("cct_"))
            self.assertEqual("cct_0_801", transaction_id)
            mock_post.reset_mock()
            book.close()

            # verify that the API was called
            mock_post.assert_called_once_with(f"{self.cohiva_test_endpoint}journal/delete.json?ids=801", data='null', headers={'Content-Type': 'application/json'}, auth=ANY)

    @patch("finance.accounting.cashctrl.requests.get")
    @patch("finance.accounting.cashctrl.requests.post")
    def test_delete_transaction(self, mock_post, mock_get):
        messages = []
        with AccountingManager(messages) as book:
            # configure fake responses
            mock_get.return_value.raise_for_status.side_effect = None
            mock_get.side_effect = self.fetch_account_responses

            mock_post.return_value.json.return_value = {
                "success": True,
                "message": "Buchung gespeichert",
                "insertId": 995,
            }
            mock_post.return_value.raise_for_status.side_effect = None

            transaction_id = book.add_transaction(
                300.00, self.account2, self.account3, "2026-02-01", "Test CashCtrl delete_transaction"
            )
            self.assertTrue(transaction_id.startswith("cct_"))

            book.save()
            mock_post.reset_mock()

            book.delete_transaction(transaction_id, autosave=False)

            # verify that the API was not(!) called
            mock_post.assert_not_called()  # not yet called

            book.save()

            # verify that the API was called
            mock_post.assert_called_once_with(
                f"{self.cohiva_test_endpoint}journal/delete.json?ids=801", data='null', headers={'Content-Type': 'application/json'}, auth=ANY
            )

