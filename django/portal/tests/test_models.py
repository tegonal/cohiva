import datetime
from unittest.mock import Mock, patch

from django.conf import settings
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

from portal.models import OAuthAppPermissionRule, OAuthAppSettings, OAuthUserStats
from portal.signals import track_oauth_app_access

from .base import PortalTestCase


class PortalOAuthModelsTest(PortalTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.app = Application.objects.create(name="TestApp")
        cls.user = cls.users["renter"].user

    def test_oauth_user_stats(self):
        self._simulate_login(reset_stats=True)

        user_stats = OAuthUserStats.objects.filter(user=self.user, application=self.app).first()
        self.assertIsNotNone(user_stats)
        self.assertEqual(user_stats.user, self.user)
        self.assertEqual(user_stats.application, self.app)
        self.assertIsNotNone(user_stats.first_login_at)
        self.assertIsNotNone(user_stats.last_seen_at)

        # Make sure that subsequent logins update the last_seen_at but not the first_login_at
        previous_last_seen = user_stats.last_seen_at
        previous_first_login = user_stats.first_login_at
        self._simulate_login()
        user_stats.refresh_from_db()
        self.assertGreater(user_stats.last_seen_at, previous_last_seen)
        self.assertEqual(user_stats.first_login_at, previous_first_login)

    def test_notify_on_first_login(self):
        # No email if no app settings
        self._simulate_login(reset_stats=True)
        self.assertEmailSent(0)

        # No email with default app settings
        app_settings = OAuthAppSettings.objects.create(application=self.app)
        self._simulate_login(reset_stats=True)
        self.assertEmailSent(0)

        # Email to default admin address
        app_settings.notify_on_first_login = True
        app_settings.save()
        self._simulate_login(reset_stats=True)
        self.assertEmailSent(1, recipient_or_list=settings.ADMINS[0][1])

        # No new email on the second login
        self._simulate_login()
        self.assertEmailSent(1)

    def test_notify_on_first_login_custom_address(self):
        OAuthAppSettings.objects.create(
            application=self.app, notify_on_first_login=True, notify_email="custom@example.test"
        )
        self._simulate_login(reset_stats=True)
        self.assertEmailSent(1, recipient_or_list="custom@example.test")

    def test_notify_on_first_login_custom_address_debug_mode(self):
        with self.settings(DEBUG=True):
            OAuthAppSettings.objects.create(
                application=self.app,
                notify_on_first_login=True,
                notify_email="custom@example.test",
            )
            self._simulate_login(reset_stats=True)
            self.assertEmailSent(1, recipient_or_list=settings.TEST_MAIL_RECIPIENT)

    def _simulate_login(self, reset_stats=False):
        if reset_stats:
            OAuthUserStats.objects.filter(user=self.user, application=self.app).delete()
        token = AccessToken(
            user=self.user,
            application=self.app,
            token=f"testtoken {timezone.now()}",
            expires=timezone.now() + datetime.timedelta(hours=1),
            scope="read write",
        )
        token.save()

    def test_oauth_user_stats_no_user(self):
        token = AccessToken(user=None, application=self.app)
        track_oauth_app_access(sender=AccessToken, instance=token, created=True)
        self.assertEqual(OAuthUserStats.objects.count(), 0)

    def test_oauth_user_stats_no_application(self):
        token = AccessToken(user=self.user, application=None)
        track_oauth_app_access(sender=AccessToken, instance=token, created=True)
        self.assertEqual(OAuthUserStats.objects.count(), 0)

    def test_oauth_user_stats_not_created(self):
        token = AccessToken(user=self.user, application=self.app)
        track_oauth_app_access(sender=AccessToken, instance=token, created=False)
        self.assertEqual(OAuthUserStats.objects.count(), 0)

    @patch("portal.signals._update_oauth_user_stats", side_effect=Exception("Test exception"))
    @patch("portal.signals.logger.error")
    def test_oauth_user_stats_exception(self, error_logger: Mock, _mock_exception: Mock):
        token = AccessToken(user=self.user, application=self.app)
        track_oauth_app_access(sender=AccessToken, instance=token, created=True)
        self.assertEqual(OAuthUserStats.objects.count(), 0)
        error_logger.assert_called_once()

    @patch("portal.signals.send_mail", side_effect=Exception("Test send_mail exception"))
    @patch("portal.signals.logger.error")
    def test_oauth_user_stats_send_mail_exception(self, error_logger: Mock, _mock_exception: Mock):
        OAuthAppSettings.objects.create(
            application=self.app, notify_on_first_login=True, notify_email="custom@example.test"
        )
        self._simulate_login(reset_stats=True)
        self.assertEqual(OAuthUserStats.objects.count(), 1)
        error_logger.assert_called_once()

    def test_model_str(self):
        stats = OAuthUserStats(application=self.app, user=self.user)
        self.assertTrue(len(str(stats)))
        app_settings = OAuthAppSettings(application=self.app)
        self.assertTrue(len(str(app_settings)))
        rule = OAuthAppPermissionRule(order=10, application_settings=app_settings)
        self.assertTrue(len(str(rule)))
