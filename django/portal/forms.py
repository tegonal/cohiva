import logging
import unicodedata

from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.utils.http import urlencode

import portal.auth as portal_auth
from geno.models import Address
from geno.utils import make_username, send_error_mail, send_info_mail

logger = logging.getLogger("access_portal")

UserModel = get_user_model()


def _unicode_ci_compare(s1, s2):
    """
    Perform case-insensitive comparison of two identifiers, using the
    recommended algorithm from Unicode Technical Report 36, section
    2.11.2(B)(2).
    """
    return (
        unicodedata.normalize("NFKC", s1).casefold()
        == unicodedata.normalize("NFKC", s2).casefold()
    )


class PortalPasswordResetForm(auth_forms.PasswordResetForm):
    def __init__(self, host=None, *args, **kwargs):
        self.host = host
        self.redirect_url = None
        super().__init__(*args, **kwargs)

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset."""
        active_users = []
        logger.info(
            "PortalPasswordResetForm - Requested password reset for email %s on %s."
            % (email, self.host)
        )
        email_field_name = UserModel.get_email_field_name()
        adr = Address.objects.filter(email__iexact=email).filter(active=True)
        for a in adr:
            auth_info = portal_auth.authorize_address(a, "TEST", host=self.host)
            if not auth_info["user_id"]:
                ## Redirect to correct host if user is using the wrong portal site.
                query = urlencode({"email": email, "autosubmit": 1})
                if self.host == settings.PORTAL_SECONDARY_HOST:
                    alt_auth_info = portal_auth.authorize_address(a, "TEST", host=None)
                    other_host_url = f"{settings.BASE_URL}/portal/password_reset/?{query}"
                else:
                    alt_auth_info = portal_auth.authorize_address(
                        a, "TEST", host=settings.PORTAL_SECONDARY_HOST
                    )
                    other_host_url = (
                        f"https://{settings.PORTAL_SECONDARY_HOST}/portal/password_reset/?{query}"
                    )
                warning_txt = f"PortalPasswordResetForm - Address '{a}' (id = {a.id}, email = {a.email}) DENIED: {auth_info['reason']}. Not creating a new user on {self.host}."
                if alt_auth_info["user_id"]:
                    self.redirect_url = other_host_url
                    warning_txt = f"{warning_txt} User is using wrong portal => Redirecting to {self.redirect_url}."
                logger.warning(warning_txt)
                send_error_mail("Unauthorized account activation - %s" % (self.host), warning_txt)
                continue
            ## Address is allowed
            if not a.user:
                ## Create new user
                username = make_username(a)
                if UserModel._default_manager.filter(
                    **{
                        "%s__iexact" % email_field_name: email,
                        "is_active": True,
                    }
                ).count():
                    logger.warning(
                        "User with same email exists already. Can't create new user %s for address %s / email %s on %s."
                        % (username, a, email, self.host)
                    )
                    send_error_mail(
                        "Creating new user failed - %s" % (self.host),
                        "User with same email exists already. Can't create new user %s for address %s / email %s."
                        % (username, a, email),
                    )
                    continue
                logger.info(
                    "PortalPasswordResetForm - Creating new user %s for address %s / email %s on %s."
                    % (username, a, email, self.host)
                )
                try:
                    user = UserModel.objects.create_user(username, a.email)
                    user.first_name = a.first_name
                    user.last_name = a.name
                    user.save()
                    a.user = user
                    a.save()
                    send_info_mail(
                        "Created new user: %s - %s" % (username, self.host),
                        "Created user '%s' based on address '%s' (id = %d, email = %s)."
                        % (username, a, a.id, a.email),
                    )
                except Exception as e:
                    send_error_mail(
                        "Creating new user failed - %s" % (self.host),
                        "Creating user '%s' based on address '%s' (id = %d, email = %s) failed."
                        % (username, a, a.id, a.email),
                    )
                    logger.error(
                        "PortalPasswordResetForm - Creating user %s failed: %s %s"
                        % (username, e, self.host)
                    )
            if a.user and a.user.is_active:
                active_users.append(a.user)

        # if not active_users:
        #    ## Try Django-only users if no users have been found in Address
        #    active_users = UserModel._default_manager.filter(**{
        #        '%s__iexact' % email_field_name: email,
        #        'is_active': True,
        #    })

        users_str = []
        users = ()
        for u in active_users:
            if _unicode_ci_compare(email, getattr(u, email_field_name)):
                users_str.append(u.username)
                users += (u,)
        if users_str:
            logger.info(
                "PortalPasswordResetForm - Sending password reset link for user(s): %s to email %s"
                % (", ".join(users_str), email)
            )
            if len(users_str) > 1:
                logger.warning(
                    "PortalPasswordResetForm - Multiple users %s with the same email address %s!"
                    % (", ".join(users_str), email)
                )
                send_info_mail(
                    "WARNING: Multiple users with same email",
                    "Multiple users %s with the same email address %s!"
                    % (", ".join(users_str), email),
                )
        else:
            logger.warning(
                "PortalPasswordResetForm - No user found for email %s on %s. NOT SENDING PASSWORD RESET EMAIL!"
                % (email, self.host)
            )
            send_info_mail(
                "Password reset for unknown user: %s - %s" % (email, self.host),
                "PortalPasswordReset requested but no user found for email '%s'." % (email),
            )
        return users

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        if settings.DEBUG:
            to_email = settings.TEST_MAIL_RECIPIENT
        if self.host == settings.PORTAL_SECONDARY_HOST:
            from_email = settings.PORTAL_SECONDARY_EMAIL_SENDER
        super().send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name,
        )


class TenantAdminTableFilterForm(forms.Form):
    date_widget = forms.TextInput(attrs={"class": "datepicker"})
    search_widget = forms.TextInput(
        attrs={
            "size": "40",
            "autofocus": "1",
        }
    )

    search = forms.CharField(label="Suche", required=False, widget=search_widget)
    action_options = [
        ("none", "------"),
        ("deactivate", "Ausgewählte Nutzer:innen löschen"),
        ("invite", "Einladungsmail (erneut) an ausgewählte Nutzer:innen verschicken"),
    ]
    action = forms.ChoiceField(choices=action_options, label="Aktion")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TenantAdminEditForm(forms.Form):
    first_name = forms.CharField(label="Vorname", max_length=30)
    name = forms.CharField(label="Name", max_length=30)
    email = forms.EmailField(label="Email")
    # send_invitation = forms.BooleanField(label="Einladung verschicken?", initial=True, required=False)


class TenantAdminUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Datei hochladen",
        help_text="CSV-Datei mit den Spalten 'Name', 'Vorname', 'Email' auswählen.",
    )
    # replace_existing = forms.BooleanField(label="Bisherige Liste komplett ersetzen?", help_text="Mit dieser Option werden existierende Nutzer:innen, welche nicht mehr auf der hochgeladenen Liste sind GELÖSCHT! Falls nicht ausgewählt, werden lediglich neue Nutzer:innen aus der Liste hinzugefügt, welche noch nicht existieren.", required=False)
    # send_invitation = forms.BooleanField(label="Automatisch Einladungsmails für neu hinzugefügte Nutzer:innen verschicken?", required=False)
