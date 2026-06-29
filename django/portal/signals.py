from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from oauth2_provider.models import AccessToken

from .models import OAuthAppFirstLogin


@receiver(post_save, sender=AccessToken)
def notify_on_first_oauth_login(sender, instance, created, **kwargs):
    if not created:
        return
    # skip client-credentials or tokens without a user
    if not instance.user:
        return
    # filter for the Seafile application only
    config = settings.FIRST_OAUTH_LOGIN_NOTIFICATION_EMAIL
    if not config:
        return
    notification_email = config.get(instance.application.client_id)
    if not notification_email:
        return

    _obj, is_first = OAuthAppFirstLogin.objects.get_or_create(
        user=instance.user,
        application=instance.application,
    )
    if is_first:
        print("TODO: send notification email")
        # send_notification_email(
        #    recipient=notification_email,
        #    subject=f"New {instance.application.name} user from SSO",
        #    message=f"User {instance.user.get_full_name()} ({instance.user.email}) "
        #    f"accessed Seafile for the first time.",
        # )
