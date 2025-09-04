import select2.fields
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from geno.models import Address, Building, GenoBase


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
    name = select2.fields.OneToOneField(
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
        verbose_name = "Nutzeradmin"
        verbose_name_plural = "Nutzeradmins"

    def list_active_buildings(self):
        return ", ".join([str(b) for b in self.buildings.filter(active=True)])


# class PortalTemplates(GenoBase):
#    name = models.CharField('Name', max_length=100)  # e.g. portal_invitation_subject, portal_invitation, portal_invitation_existing_user
#    building = select2.fields.ForeignKey(Building, verbose_name='Vorlage für Gebäude')
#    template = select2.fields.ForeignKey(ContentTemplate, verbose_name="Vorlage")
#
#    class Meta
#        unique_together(name,building)
#        verbose_name = "Portal Vorlagen"
# class PortalConfig(GenoBase):
#    name = models.CharField('Name', max_length=100)  # e.g. portal_invitation_subject, portal_invitation, portal_invitation_existing_user
#    building = select2.fields.ForeignKey(Building, verbose_name='Konfiguration für Gebäude')
#    value = models.TextField('Wert')
#    active = models.BooleanField('Aktiv', default=True)
#
#    class Meta:
#        unique_together(name,building,active)
#        verbose_name = "Portal Konfiguration"
#
#    @classmethod
#    def get_config_value(cls, name, building, default_value=None):
#        try:
#            obj = cls.objects.get(name=name, building=building, active=True)
#            return obj.value
#        except cls.DoesNotExist:
#            return default_value
