import os

import jsonc
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _
from filer.models.filemodels import File as FilerFile

from cohiva.utils.models import get_next_number
from geno.models import GenoBase
from geno.utils import send_error_mail
from report.generator import ReportGeneratorConfigItem
from report.nk.cost_config import (
    REPORT_ITEM_CATEGORY,
    CostConfigFieldTypes,
    get_enum_value,
    get_report_item_config,
)

REPORT_STATE_CHOICES = (
    ("new", "Neu"),
    ("pending", "Wird erstellt..."),
    ("generated", "Erstellt"),
    ("generated_dryrun", "Erstellt (Testlauf)"),
    ("invalid", "Ungültig"),
)

REPORT_TYPE_CHOICES = (("NK", "Nebenkostenabrechnung"),)

REPORT_FIELDTYPE_CHOICES = (
    ("char", "Text"),
    ("int", "Ganzzahl"),
    ("float", "Dezimalzahl"),
    ("date", "Datum"),
    ("bool", "Boolean"),
    ("list_12months_float", "Dezimalzahlen, 12 Monatswerte"),
    ("file", "Datei"),
    ("json", "JSON-Daten"),
    ("buildingIds", "Liegenschaften"),
    ("enum_vewa_category", "VEWA Kategorie"),
    ("enum_monthly_weights", "Verteilschlssel nach Monat"),
    ("enum_section_weights", "Verteilschlüssel nach Objekttyp"),
    ("enum_object_weights", "Verteilschlüssel nach Objekt"),
)


def _match_CostConfigFieldTypes_with_REPORT_FIELDTYPE_CHOICES_values(ccft: CostConfigFieldTypes):
    match ccft:
        # case CostConfigFieldTypes.INPUT_KEY:
        #    return "char"
        case CostConfigFieldTypes.STRING:
            return "char"
        # case CostConfigFieldTypes.STRING_LIST:
        #    return "char"
        case CostConfigFieldTypes.BOOL:
            return "bool"
        # case CostConfigFieldTypes.MEASUREMENT_SOURCES:  # to be refactored, set of fields
        #    return "char"
        case CostConfigFieldTypes.VEWA_CATEGORY:  # enum dropdown
            return "enum_vewa_category"
        case CostConfigFieldTypes.MONTHLY_WEIGHTS:  # enum dropdown
            return "enum_monthly_weights"
        case CostConfigFieldTypes.SECTION_WEIGHTS:  # enum dropdown
            return "enum_section_weights"
        case CostConfigFieldTypes.OBJECT_WEIGHTS:  # enum dropdown
            return "enum_object_weights"
        case CostConfigFieldTypes.FLOAT:
            return "float"
        case CostConfigFieldTypes.INT:
            return "int"
        case CostConfigFieldTypes.DATE:
            return "date"
        # case CostConfigFieldTypes.LIST_12MONTHS_FLOAT: # don't implement for now, json type used
        #     return "list_12months_float"
        case CostConfigFieldTypes.FILE:
            return "file"
        case CostConfigFieldTypes.JSON:
            return "json"
        # case CostConfigFieldTypes.BUILDINGIDS: # unused since configured on report
        #     return "buildingIds"
        case _:
            raise ValueError(f"Unbekannter CostConfigFieldTypes-Wert: {ccft}")


class ReportConfiguration(GenoBase):
    name = models.CharField("Name", max_length=80)
    report_type = models.CharField("Reporttyp", choices=REPORT_TYPE_CHOICES, max_length=30)
    buildings = models.ManyToManyField("geno.Building", verbose_name="Liegenschaften", blank=True)

    def save_as_copy(self):
        old_report_configuration_id = self.id
        super().save_as_copy()
        old_report_configuration = ReportConfiguration.objects.get(id=old_report_configuration_id)
        for report_item_configuration in ReportItemConfiguration.objects.filter(
            report_configuration=old_report_configuration
        ):
            report_item_configuration.save_as_copy()
            report_item_configuration.report_configuration = self
            report_item_configuration.save()

    class Meta:
        verbose_name = "Report-Konfiguration"
        verbose_name_plural = "Report-Konfigurationen"


class Report(GenoBase):
    name = models.CharField("Name", max_length=80)
    report_configuration = models.ForeignKey(
        ReportConfiguration,
        verbose_name="Report-Konfiguration",
        on_delete=models.CASCADE,
        default=1,
    )
    show_full_config = models.BooleanField("Expert:innen-Konfiguration anzeigen", default=False)
    task_id = models.UUIDField("Task-ID", editable=False, blank=True, null=True)
    state = models.CharField("Status", default="new", choices=REPORT_STATE_CHOICES, max_length=30)
    state_info = models.TextField("Statusinfo", blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.pk:
            # copy configuration from ReportConfiguration
            if self.report_configuration:
                for report_item_configuration in ReportItemConfiguration.objects.filter(
                    report_configuration=self.report_configuration
                ):
                    report_item = ReportItem.objects.create(
                        name=report_item_configuration.name,
                        item_category=report_item_configuration.item_category,
                        order=report_item_configuration.order,
                        report=self,
                    )
                    for report_input_field in ReportInputField.objects.filter(
                        item_configuration=report_item_configuration
                    ):
                        ReportInputData.objects.create(
                            name=report_input_field,
                            description=report_input_field.description,
                            field_type=report_input_field.field_type,
                            report=self,
                            item=report_item,
                            value=report_input_field.value_default,
                            order=report_input_field.order,
                            show=report_input_field.show,
                        )

    def get_report_config(self) -> list[ReportGeneratorConfigItem]:
        config = []
        for report_item in ReportItem.objects.filter(report=self):
            # print(f"{report_item.name} [{report_item.item_category}]")
            for item in get_report_item_config():
                if item.config["name"] == report_item.item_category:
                    config_class = item.config["config"]
                    config_obj = config_class.build(
                        item.config, ReportInputData.objects.filter(item=report_item, report=self)
                    )
                    config_obj.set_name(report_item.name)
                    config.append(ReportGeneratorConfigItem(report_item, config_obj))
                    break
        # pprint(config)
        return config

    def get_object_actions(self):
        actions = []
        if self.state == "new":
            actions.append((f"/report/generate_dryrun/{self.pk}/", "Report erzeugen (Testlauf)"))
            actions.append((f"/report/generate/{self.pk}/", "Report erzeugen"))
        elif self.state != "pending":
            actions.append((f"/report/output/{self.pk}/", "Resultate anzeigen"))
            actions.append((f"/report/delete_output/{self.pk}/?init=1", "Alle Resultate LÖSCHEN!"))
        return actions

    def save_as_copy(self):
        self.task_id = None
        self.state = "new"
        self.state_info = ""
        old_report_id = self.id
        super().save_as_copy()
        old_report = Report.objects.get(id=old_report_id)
        for input_data in ReportInputData.objects.filter(report=old_report):
            input_data.report = self
            input_data.save_as_copy()

    def reset(self):
        self.state = "new"
        self.state_info = ""
        self.task_id = None
        self.save()

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        constraints = [
            UniqueConstraint(fields=["name", "report_configuration"], name="unique_report"),
        ]


# REPORT_ITEM_CATEGORY = (
# ("NkTotalCost", "Gesamtkosten mit einfacher Verteilung (Fläche, Volumen, Faktor)"),
# ("NkMonthlyCost", "Monatliche Kosten mit einfacher Verteilung (Fläche, Volumen, Faktor)"),
# ("NkTotalEnergyCost", "Gesamtkosten mit einfacher Verteilung (Verbrauch)"),
# ("NkPerRentalUnitCost", "Kosten pro Mietobjekt mit Verteilung (pro Mieteinheit, Peson, Fixum)"),
# ("NkCostZEVStromallmend", "Stromallmend: ZEV-Kosten"),
# ("NkCostVEWA", "VEWA: Verbrauchsabhängige Energie- und Wasserkostenabrechnung"),
# )


def get_next_report_item_configuration_order_number():
    return get_next_number("report", "ReportItemConfiguration", "order", 10)


class ReportItemConfiguration(GenoBase):
    name = models.CharField("Element-Bezeichnung", max_length=80)
    item_category = models.CharField(
        "Element-Kategorie", choices=REPORT_ITEM_CATEGORY, max_length=60
    )
    report_configuration = models.ForeignKey(
        ReportConfiguration,
        verbose_name="Report-Konfiguration",
        on_delete=models.CASCADE,
        default=1,
    )
    order = models.IntegerField(
        _("Order"),
        help_text=_("Order of the item in the report."),
        default=get_next_report_item_configuration_order_number,
    )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_item_category = None
        if not is_new and self.pk:
            old_item_category = (
                ReportItemConfiguration.objects.filter(pk=self.pk)
                .values_list("item_category", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if is_new or old_item_category != self.item_category:
            self.ensure_base_input_fields(old_item_category)

    def ensure_base_input_fields(self, old_item_category):
        configuration = None
        old_fields = []
        for item in get_report_item_config():
            if item.config and item.config["config"]:
                if item.config["name"] == self.item_category:
                    configuration = item.config
                elif item.config["name"] == old_item_category:
                    old_configuration = item.config
                    if old_configuration.get("config"):
                        for field in old_configuration.get("config").get_fields():
                            if field.key not in ("class", "name", "bezeichnung"):
                                old_fields.append(field.key)

        if configuration and configuration.get("config"):
            for field in configuration.get("config").get_fields():
                if field.key not in ("class", "name", "bezeichnung"):
                    if field.key in old_fields:
                        old_fields.remove(field.key)
                    else:
                        default_val = configuration.get(field.key)
                        if default_val is None:
                            default_val = ""
                        ReportInputField.objects.create(
                            name=field.key,
                            description=str(field),
                            item_configuration=self,
                            field_type=_match_CostConfigFieldTypes_with_REPORT_FIELDTYPE_CHOICES_values(
                                field.type
                            ),
                            show=field.show,
                            value_default=default_val,
                        )

        # Delete fields from old item category, that are not present in the new category
        for old_field in old_fields:
            old = ReportInputField.objects.filter(item_configuration=self, name=old_field)
            old.delete()

    def save_as_copy(self):
        old_report_item_configuration_id = self.id
        super().save_as_copy()
        old_report_item_configuration = ReportItemConfiguration.objects.get(
            id=old_report_item_configuration_id
        )
        for report_input_field in ReportInputField.objects.filter(
            item_configuration=old_report_item_configuration
        ):
            report_input_field.save_as_copy()
            report_input_field.report_configuration = self
            report_input_field.save()

    class Meta:
        verbose_name = "Report-Element-Konfiguration"
        verbose_name_plural = "Report-Element-Konfigurationen"
        ordering = ["report_configuration", "order", "item_category", "name"]
        constraints = [
            UniqueConstraint(
                fields=["name", "item_category", "report_configuration"],
                name="unique_report_configuration_item",
            ),
            ## Don't enforce a unique order, at least until we have a better UI for changing it.
            # UniqueConstraint(
            #    fields=["name", "item_category", "report_configuration", "order"],
            #    name="unique_report_configuration_item_order",
            # ),
        ]


def get_next_report_item_order_number():
    return get_next_number("report", "ReportItem", "order", 10)


class ReportItem(GenoBase):
    name = models.CharField("Element-Bezeichnung", max_length=80)
    item_category = models.CharField(
        "Element-Kategorie", choices=REPORT_ITEM_CATEGORY, max_length=60
    )
    report = models.ForeignKey(
        Report,
        verbose_name="Report",
        on_delete=models.CASCADE,
        default=1,
    )
    order = models.IntegerField(
        _("Order"),
        help_text=_("Order of the item in the report."),
        default=get_next_report_item_order_number,
    )

    class Meta:
        verbose_name = "Report-Element"
        verbose_name_plural = "Report-Elemente"
        ordering = ["report", "order", "item_category", "name"]
        constraints = [
            UniqueConstraint(
                fields=["name", "item_category", "report"], name="unique_report_item"
            ),
            ## Don't enforce a unique order, at least until we have a better UI for changing it.
            # UniqueConstraint(
            #    fields=["name", "item_category", "report", "order"],
            #    name="unique_report_item_order",
            # ),
        ]


def get_next_report_input_field_order_number():
    return get_next_number("report", "ReportInputField", "order", 10)


class ReportInputField(GenoBase):
    name = models.CharField("Name", max_length=80)
    description = models.CharField("Beschreibung", max_length=200, blank=True)
    item_configuration = models.ForeignKey(
        ReportItemConfiguration,
        verbose_name="Report-Element",
        on_delete=models.CASCADE,
        default=1,
    )
    field_type = models.CharField("Feldtyp", choices=REPORT_FIELDTYPE_CHOICES, max_length=60)
    show = models.BooleanField(
        "Anzeigen",
        default=False,
        help_text=(
            "Falls aktiv, wird das Eingabefeld für die Erstellung des Reports angezeigt, "
            "andernfalls wird der Standardwert von hier verwendet."
        ),
    )
    value_default = models.CharField("Standardwert", blank=True, max_length=6000)
    order = models.IntegerField(
        _("Order"),
        help_text=_("Order of the field."),
        default=get_next_report_input_field_order_number,
    )

    def __str__(self):
        return f"{self.name} [{self.get_field_type_display()}]"

    class Meta:
        verbose_name = "Eingabefeld"
        verbose_name_plural = "Eingabefelder"
        ordering = ["item_configuration", "order", "name"]
        constraints = [
            UniqueConstraint(
                fields=["name", "item_configuration"], name="unique_report_input_field"
            ),
        ]


class ReportInputData(GenoBase):
    name = models.ForeignKey(
        ReportInputField, verbose_name="Eingabefeld", on_delete=models.CASCADE
    )
    description = models.CharField("Beschreibung", max_length=200, blank=True)
    field_type = models.CharField("Feldtyp", choices=REPORT_FIELDTYPE_CHOICES, max_length=60)
    report = models.ForeignKey(Report, verbose_name="Report", on_delete=models.CASCADE)
    item = models.ForeignKey(
        ReportItem,
        verbose_name="Report-Element",
        on_delete=models.CASCADE,
        default=1,
    )
    value = models.CharField(
        "Wert", blank=True, max_length=6000
    )  ## store lists in value?  Should be able to copy list values from spreadsheet in UI!
    # index/date/key instead of storing lists in value?
    order = models.IntegerField(
        _("Order"),
        help_text=_("Order of the field."),
        default=50,
    )
    show = models.BooleanField(
        "Anzeigen", default=False, help_text="Falls aktiv, wird das Eingabefeld angezeigt."
    )

    class Meta:
        verbose_name = "Eingabewert"
        verbose_name_plural = "Eingabewerte"
        ordering = ["report", "name__item_configuration", "order", "description"]
        constraints = [
            UniqueConstraint(fields=["name", "report"], name="unique_report_input_data"),
        ]

    def __str__(self):
        if self.name:
            return f"{self.name}"
        else:
            return "(Unbekannt)"

    def get_value(self):
        if self.name.field_type == "file" and self.value.startswith("filer:"):
            try:
                filer_file = FilerFile.objects.get(id=int(self.value[6:]))
                return filer_file.path
            except FilerFile.DoesNotExist:
                return f"[FEHLT: Datei für «{self.name.name}» mit ID {self.value}]"
        if self.name.field_type == "bool":
            return self.value.lower() in ["true", "1", "yes"]
        if self.name.field_type == "int":
            return int(self.value)
        if self.name.field_type == "float":
            return float(self.value)
        if self.name.field_type == "date":
            raise RuntimeError("Input field type 'date' not implemented yet")
        if self.name.field_type == "json":
            if self.value == "":
                return []
            return jsonc.loads(self.value)
        if self.name.field_type.startswith("enum_"):
            return get_enum_value(self.name.field_type, self.value)
        return self.value


REPORT_OUTPUTTYPE_CHOICES = (
    ("pdf", "PDF Datei"),
    ("csv", "CSV Datei"),
    ("ods", "ODS Datei"),
    ("json", "JSON Datei"),
    ("png", "PNG Datei"),
    ("text", "Text"),
)


## e.g. Celery generated output
class ReportOutput(GenoBase):
    name = models.CharField("Name", max_length=200)
    group = models.CharField("Gruppe", max_length=80, blank=True)
    report = models.ForeignKey(Report, verbose_name="Report", on_delete=models.CASCADE)
    output_type = models.CharField("Feldtyp", choices=REPORT_OUTPUTTYPE_CHOICES, max_length=30)
    value = models.TextField("Wert")
    regeneration_json = models.TextField("JSON-Daten für neues Erzeugen", blank=True)

    def get_filename(self):
        if self.report and self.value and self.output_type != "text":
            return settings.SMEDIA_ROOT + f"/report/{self.report.id}/{self.value}"
        return None

    class Meta:
        verbose_name = "Reportoutput"
        verbose_name_plural = "Reportoutputs"
        constraints = [
            UniqueConstraint(fields=["name", "report"], name="unique_report_output"),
        ]


@receiver(models.signals.post_delete, sender=ReportOutput)
def _delete_report_output_file(sender, instance, *args, **kwargs):
    filename = instance.get_filename()
    if filename:
        try:
            os.remove(filename)
        except OSError as error:
            send_error_mail(
                "Konnte Report-Output nicht löschen",
                f"ID: {instance.id}\nDatei: {filename}",
                error,
            )


@receiver(models.signals.post_delete, sender=ReportOutput)
def _reset_report_if_all_output_deleted(sender, instance, *args, **kwargs):
    report = instance.report
    if ReportOutput.objects.filter(report=report).count() == 0:
        report.reset()
