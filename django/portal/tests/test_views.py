from .base import PortalTestCase


class PortalViewsTest(PortalTestCase):
    # @classmethod
    # def setUpTestData(cls):
    #    super().setUpTestData()
    #    geno_testdata.create_users(cls)

    def test_views_status200(self):
        # self.client.login(username='superuser', password='secret')
        # self.assertTrue(login)
        paths = [
            "login/",
            "logout/",
            "password_change/",
            "password_change/done/",
            "password_reset/",
            "password_reset/done/",
            #'reset/<uidb64>/<token>/',
            "reset/done/",
            #'me/',
            "tenant-admin/",
            "tenant-admin/1/change/",
            "tenant-admin/add/",
            "tenant-admin/upload/",
            # TODO: Requires session 'tenant-admin/upload/commit/',
            # TODO: Requires RC-config 'tenant-admin/maintenance/',
            # TODO: Requires RC-config 'cron_maintenance/',
            # TODO: API 'rocket_chat_webhook/test/',
            # TODO: API 'rocket_chat_webhook/new_user/',
            # TODO: API 'rocket_chat_webhook/autorespond/',
            # TODO Content 'home/',
        ]
        for path in paths:
            response = self.client.get(f"/portal/{path}")
            if response.status_code != 200:
                redirect = getattr(response, "url", None)
                print(f"FAILED PATH: /portal/{path} [{response.status_code}] => {redirect}")
            self.assertEqual(response.status_code, 200)
            if path in ("login/", "logout/"):
                logged_in = self.client.login(username="tenantadmin1", password="secret")
                self.assertTrue(logged_in)
