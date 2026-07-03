from django.conf import settings
from django.contrib import auth
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from geno.models import Address, Building, GenoBase

# TODO: This should be refactored to a more general user role model and moved from the
#       reservation module to cohiva or geno.
from reservation.models import RESERVATIONTYPE_ROLE_CHOICES

UserModel = auth.get_user_model()


class PortalPage(Page):
    subpage_types = ["PortalHelpPage", "PortalPage"]

    class Meta:
        verbose_name = "Portal Seite"
        verbose_name_plural = "Portal Seiten"


class PortalHelpPage(Page):
    parent_page_types = ["PortalPage"]
    subpage_types = ["PortalHelpPageSection"]

    class Meta:
        verbose_name = "Portal Hilfe Seite"
        verbose_name_plural = "Portal Hilfe Seiten"


class PortalHelpPageSection(Page):
    parts = StreamField(
        [
            (
                "abschnitte",
                blocks.StructBlock(
                    [
                        ("frage", blocks.CharBlock()),
                        (
                            "antwort",
                            blocks.StreamBlock(
                                [
                                    (
                                        "abschnitt",
                                        blocks.RichTextBlock(
                                            features=["underline", "link", "document-link"]
                                        ),
                                    ),
                                    ("untertitel", blocks.CharBlock()),
                                    (
                                        "video",
                                        blocks.StructBlock(
                                            [
                                                ("url", blocks.CharBlock()),
                                                ("legende", blocks.CharBlock(required=False)),
                                            ]
                                        ),
                                    ),
                                    (
                                        "einzelbild",
                                        blocks.StructBlock(
                                            [
                                                ("bild", ImageChooserBlock()),
                                                ("legende", blocks.CharBlock(required=False)),
                                            ]
                                        ),
                                    ),
                                    (
                                        "bilder",
                                        blocks.ListBlock(
                                            blocks.StructBlock(
                                                [
                                                    ("bild", ImageChooserBlock()),
                                                    ("legende", blocks.CharBlock(required=False)),
                                                ]
                                            )
                                        ),
                                    ),
                                    ("aufzaehlung", blocks.ListBlock(blocks.CharBlock())),
                                    ("nummerierung", blocks.ListBlock(blocks.CharBlock())),
                                ]
                            ),
                        ),
                    ],
                    template="portal/blocks/hilfe_section.html",
                ),
            )
        ],
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("parts"),
    ]

    parent_page_types = ["PortalHelpPage"]
    subpage_types = []


class TenantAdmin(GenoBase):
    name = models.OneToOneField(
        Address,
        verbose_name="Person",
        on_delete=models.CASCADE,
        related_name="address_tenantadmin",
    )
    buildings = models.ManyToManyField(
        Building, verbose_name="Admin für Gebäude", related_name="building_tenantadmins"
    )
    notes = models.TextField("Bemerkungen", blank=True)
    active = models.BooleanField("Aktiv", default=True)

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    class Meta:
        ordering = ["name"]
        verbose_name = "Admin externer Nutzer:innen"
        verbose_name_plural = "Admins externer Nutzer:innen"

    def list_active_buildings(self):
        return ", ".join([str(b) for b in self.buildings.filter(active=True)])


class OAuthUserStats(models.Model):
    application = models.ForeignKey(
        settings.OAUTH2_PROVIDER_APPLICATION_MODEL, on_delete=models.CASCADE
    )
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    first_login_at = models.DateTimeField(_("First login at"))
    last_seen_at = models.DateTimeField(_("Last token issued at"))

    class Meta:
        unique_together = ("user", "application")
        verbose_name = _("OAuth user stats")
        verbose_name_plural = _("OAuth user stats")

    def __str__(self):
        return _("OAuth stats of user {user} for {app}").format(
            user=self.user, app=self.application.name
        )


class OAuthAppPermissionDenied(Exception):
    """Raised if a user is not authorized to access a specific OAuth application."""


class OAuthAppNoPermissionsConfigured(Exception):
    """Raised if no permission rules have been configured for in the OAuth app settings."""


class OAuthAppSettings(models.Model):
    application = models.OneToOneField(
        settings.OAUTH2_PROVIDER_APPLICATION_MODEL, on_delete=models.CASCADE
    )
    notify_on_first_login = models.BooleanField(
        _("Notify admin about new users"),
        default=False,
        help_text=_("Send a notification email if a user logs in to this app for the first time."),
    )
    notify_email = models.EmailField(
        _("Notification email address"),
        blank=True,
        help_text=_(
            "Email address to send notifications to. If empty, the default admin email will be used."
        ),
    )

    class Meta:
        verbose_name = _("OAuth application settings")
        verbose_name_plural = _("OAuth application settings")

    def __str__(self):
        return _("OAuth application settings for {app}").format(app=self.application.name)

    def authorize(self, user: UserModel):
        rules = OAuthAppPermissionRule.objects.filter(application_settings=self).order_by("order")
        if not rules.exists():
            raise OAuthAppNoPermissionsConfigured
        for rule in rules:
            if rule.match(user):
                if rule.action == "deny":
                    raise OAuthAppPermissionDenied
                elif rule.action == "allow":
                    return
                else:
                    raise ValueError(f"Invalid action: {rule.action}")
        # Deny access if no rule matches
        raise OAuthAppPermissionDenied


PERMISSION_RULE_ACTIONS = (
    ("allow", _("Allow access")),
    ("deny", _("Deny access")),
)


class OAuthAppPermissionRule(models.Model):
    application_settings = models.ForeignKey(
        OAuthAppSettings, on_delete=models.CASCADE, related_name="permissions"
    )
    role = models.CharField(
        _("User role"),
        max_length=30,
        choices=RESERVATIONTYPE_ROLE_CHOICES,
        blank=True,
        help_text=_("Apply rule to users with this role. If left empty it matches ALL users."),
    )
    group = models.ForeignKey(
        auth.models.Group,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        help_text=_("Apply rule to users in this group. If left empty it matches ALL users."),
    )
    role_or_group_must_match = models.BooleanField(
        _("User role OR group must match"),
        default=False,
        help_text=_(
            "When enabled only one of the settings above must match. If disabled, both must match."
        ),
    )
    order = models.IntegerField(
        _("Order"),
        help_text=_("Order of the rule. Rules are applied in order, first match wins."),
    )
    action = models.CharField(
        _("Action"),
        max_length=30,
        choices=PERMISSION_RULE_ACTIONS,
        help_text=_("Action to take when the rule matches."),
    )

    class Meta:
        ordering = ["application_settings", "order"]
        verbose_name = _("OAuth access permission rule")
        verbose_name_plural = _("OAuth access permission rules")
        unique_together = ("application_settings", "order")

    def __str__(self):
        return _("Rule {order} for {app}").format(
            order=self.order, app=self.application_settings.application.name
        )

    def match(self, user: UserModel):
        if not self.role and not self.group:
            # Always match if no role and no group is specified (matches all users)
            return True
        role_matches = (
            self.role in user.address.get_roles() if self.role and user.address else False
        )
        if self.role and not self.group:
            return role_matches
        group_matches = user.groups.filter(pk=self.group.pk).exists() if self.group else False
        if self.group and not self.role:
            return group_matches
        if self.role_or_group_must_match:
            return role_matches or group_matches
        else:
            return role_matches and group_matches
