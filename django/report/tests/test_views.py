# from django.conf import settings

from .base import ReportTestCase


class ReportViewsTest(ReportTestCase):
    def test_views_status200(self):
        logged_in = self.client.login(username="superuser", password="secret")
        self.assertTrue(logged_in)
        paths = [
            # "test_celery/",
            # "test_celery_nobackend/",
            "configure/1/",
            "output/1/",
            # TODO: Needsdata "output/1/download/all/",
            # TODO: Needsdata "output/1/download/1/",
            # TODO: "output/1/regenerate/1/",
            # TODO: "delete_output/1/",
            # TODO: "generate/1/",
            # TODO: "generate_dryrun/1/",
        ]
        for path in paths:
            response = self.client.get(f"/report/{path}")
            if response.status_code != 200:
                redirect = getattr(response, "url", None)
                print(f"FAILED PATH: /report/{path} [{response.status_code}] => {redirect}")
            self.assertEqual(response.status_code, 200)
