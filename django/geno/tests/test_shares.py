from .base import GenoAdminTestCase


class ShareTest(GenoAdminTestCase):
    def test_share_overview(self):
        response = self.client.get("/geno/share/overview/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Summe CHF: 40'500.00", response.content.decode())
