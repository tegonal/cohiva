from .base import ReservationTestCase


class ReservationViewsTest(ReservationTestCase):
    # @classmethod
    # def setUpTestData(cls):
    #    super().setUpTestData()
    #    geno_testdata.create_users(cls)

    def test_views_status200(self):
        # logged_in = self.client.login(username='superuser', password='secret')
        # self.assertTrue(logged_in)
        paths = [
            #'sync/ical/',
            "send_report_emails/",
            "cron_maintenance/",
        ]
        for path in paths:
            response = self.client.get(f"/reservation/{path}")
            if response.status_code != 200:
                redirect = getattr(response, "url", None)
                print(f"FAILED PATH: /reservation/{path} [{response.status_code}] => {redirect}")
            self.assertEqual(response.status_code, 200)
