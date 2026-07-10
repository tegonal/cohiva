import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext as _
from oauth2_provider.models import AccessToken

from cohiva.utils.settings import get_admin_recipients

from .models import OAuthAppSettings, OAuthUserStats

logger = logging.getLogger("access_portal")


@receiver(post_save, sender=AccessToken)
def track_oauth_app_access(sender, instance: AccessToken, created, **kwargs):
    token = instance
    if not token.user or not token.application or not created:
        return
    try:
        is_first = _update_oauth_user_stats(token)
    except Exception as e:
        logger.error(
            "Error updating OAuth user stats for "
            f"{token.user.username} and {token.application.name}: {e}"
        )
        return
    if is_first:
        try:
            _send_first_oauth_login_notification_email(token)
        except Exception as e:
            logger.error(
                "Error sending first login notification email for "
                f"{token.user.username} and {token.application.name}: {e}"
            )


def _update_oauth_user_stats(token: AccessToken) -> bool:
    now = timezone.now()
    try:
        with transaction.atomic():
            user_info, is_first = OAuthUserStats.objects.get_or_create(
                user=token.user,
                application=token.application,
                defaults={"first_login_at": now, "last_seen_at": now},
            )
            if not is_first:
                user_info.last_seen_at = now
                user_info.save(update_fields=["last_seen_at"])
    except IntegrityError:
        # Lost the race to another concurrent login; treat as not-first.
        is_first = False
        OAuthUserStats.objects.filter(user=token.user, application=token.application).update(
            last_seen_at=now
        )
    return is_first


def _send_first_oauth_login_notification_email(token: AccessToken):
    config = OAuthAppSettings.objects.filter(application=token.application).first()
    if not config or not config.notify_on_first_login:
        return
    recipients = [config.notify_email] if config.notify_email else None
    if not recipients:
        recipients = get_admin_recipients()
    if settings.DEBUG or settings.DEMO:
        recipients = [settings.TEST_MAIL_RECIPIENT]
    sender = f'"Cohiva {settings.COHIVA_SITE_NICKNAME}" <{settings.GENO_DEFAULT_EMAIL}>'
    subject = _("{site_name} Portal: First login to {app_name}").format(
        site_name=settings.COHIVA_SITE_NICKNAME, app_name=token.application.name
    )
    user_info = f"{token.user.get_full_name() or token.user.username} ({token.user.email})"
    message = _(
        "You receive this email, because you are registered as administrator of the {app_name} "
        "application and a new user has accessed it for the first time: {user_info}."
    ).format(app_name=token.application.name, user_info=user_info)
    send_mail(subject, message, sender, recipients)
