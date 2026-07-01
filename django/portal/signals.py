import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext as _
from oauth2_provider.models import AccessToken

from .models import OAuthAppSettings, OAuthUserStats

logger = logging.getLogger("access_portal")


@receiver(post_save, sender=AccessToken)
def track_oauth_app_access(sender, instance: AccessToken, created, **kwargs):
    token = instance
    if not token.user or not created:
        return
    try:
        user_info = OAuthUserStats.objects.get(user=token.user, application=token.application)
        is_first = False
    except OAuthUserStats.DoesNotExist:
        user_info = OAuthUserStats(user=token.user, application=token.application)
        is_first = True
    if is_first:
        user_info.first_login_at = timezone.now()
    user_info.last_seen_at = timezone.now()
    user_info.save()

    if is_first:
        _send_first_oauth_login_notification_email(token)


def _send_first_oauth_login_notification_email(token: AccessToken):
    config = OAuthAppSettings.objects.filter(application=token.application).first()
    if not config or not config.notify_on_first_login:
        return
    recipient = config.notify_email
    if not recipient or settings.DEBUG or settings.DEMO:
        recipient = settings.TEST_MAIL_RECIPIENT
    sender = f'"Cohiva {settings.COHIVA_SITE_NICKNAME}" <{settings.GENO_DEFAULT_EMAIL}>'
    subject = _("{site_name} Portal: First login to {app_name}").format(
        site_name=settings.COHIVA_SITE_NICKNAME, app_name=token.application.name
    )
    user_info = f"{token.user.get_full_name() or token.user.username} ({token.user.email})"
    message = _(
        "You receive this email, because you are registered as administrator of the {app_name} "
        "application and a new user has accessed it for the first time: {user_info}."
    ).format(app_name=token.application.name, user_info=user_info)
    try:
        send_mail(subject, message, sender, [recipient])
    except Exception as e:
        logger.error(f"Could not send first login notification email to {recipient}: {e}")
