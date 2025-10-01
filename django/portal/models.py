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
        verbose_name = "Nutzeradmin"
        verbose_name_plural = "Nutzeradmins"

    def list_active_buildings(self):
        return ", ".join([str(b) for b in self.buildings.filter(active=True)])
