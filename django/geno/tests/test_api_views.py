from django.test import RequestFactory

import geno.tests.data as geno_testdata
from geno.api_views import QRBill

from .base import GenoAdminTestCase


class GenoQRBillAPIViewsTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)

    def test_get_akonto_qrbill(self):
        self.factory = RequestFactory()
        request = self.factory.post("/geno/qrbill/", {"contract_id": 0})
        view = QRBill()
        view.contract = self.contracts[0]
        view.address = view.contract.get_contact_address()
        view.context = view.address.get_context()
        pdf_file = view.get_akonto_qrbill(request)
        self.assertInPDF(
            pdf_file.file_to_stream,
            [
                "Zahlbar durch\nAnna Muster\nBeispielweg 1\nCH-3000 Bern\n",
                (
                    "Konto / Zahlbar an\n"
                    "CH77 3000 0001 2500 9423 9\n"
                    "Genossenschaft Musterweg\n"
                    "Musterweg 1\n"
                    "CH-3000 Bern\n"
                ),
            ],
        )
        pdf_file.file_to_stream.close()
