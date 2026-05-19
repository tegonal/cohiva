import os

import jsonc
from django.conf import settings
from django.db import models
from django.dispatch.dispatcher import receiver
from filer.models.filemodels import File as FilerFile

from geno.models import GenoBase
from geno.utils import send_error_mail

from report.nk.cost_config import REPORT_ITEM_CATEGORY, NkTotalCostConfig
from report.nk.cost_config import get_costs_from_config
from report.nk.cost_config import CostConfigFieldTypes

REPORT_STATE_CHOICES = (
    ("new", "Neu"),
    ("pending", "Wird erstellt..."),
    ("generated", "Erstellt"),
    ("generated_dryrun", "Erstellt (Testlauf)"),
    ("invalid", "Ungültig"),
)

REPORT_TYPE_CHOICES = (
    ("NK", "Nebenkostenabrechnung"),
)

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
)

def _match_CostConfigFieldTypes_with_REPORT_FIELDTYPE_CHOICES_values(ccft: CostConfigFieldTypes):
    match ccft:
        case CostConfigFieldTypes.INPUT_KEY:
            return "char"
        case CostConfigFieldTypes.STRING:
            return "char"
        case CostConfigFieldTypes.STRING_LIST:
            return "char"
        case CostConfigFieldTypes.BOOL:
            return "bool"
        case CostConfigFieldTypes.MEASUREMENT_SOURCES: # to be refactored, set of fields
            return "char"
        case CostConfigFieldTypes.VEWA_CATEGORY: # eum dropdown
            return "char"
        # case CostConfigFieldTypes.FLOAT:
        #     return "float"
        # case CostConfigFieldTypes.INT:
        #     return "int"
        # case CostConfigFieldTypes.DATE:
        #     return "date"
        # case CostConfigFieldTypes.LIST_12MONTHS_FLOAT: # don't implement for now, json type used
        #     return "list_12months_float"
        # case CostConfigFieldTypes.FILE:
        #     return "file"
        # case CostConfigFieldTypes.JSON:
        #     return "json"
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
        new_report_configuration = super().save_as_copy()
        old_report_configuration = ReportConfiguration.objects.get(id=old_report_configuration_id)
        for report_item_configuration in ReportItemConfiguration.objects.filter(report_configuration=old_report_configuration):
            new_report_item_configuration = report_item_configuration.save_as_copy()
            new_report_item_configuration.report_configuration = new_report_configuration
            new_report_item_configuration.save()

    class Meta:
        verbose_name = "Report-Konfiguration"
        verbose_name_plural = "Report-Konfigurationen"

class Report(GenoBase):
    name = models.CharField("Name", max_length=80)
    report_configuration = models.ForeignKey(ReportConfiguration, verbose_name="Report-Konfiguration", on_delete=models.CASCADE, default=1)
    task_id = models.UUIDField("Task-ID", editable=False, blank=True, null=True)
    state = models.CharField("Status", default="new", choices=REPORT_STATE_CHOICES, max_length=30)
    state_info = models.TextField("Statusinfo", blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and self.pk:
            # copy configuration from ReportConfiguration
            if self.report_configuration:
                for report_item_configuration in ReportItemConfiguration.objects.filter(report_configuration=self.report_configuration):
                    report_item = ReportItem.objects.create(
                        name=report_item_configuration.name,
                        item_category=report_item_configuration.item_category,
                        report_configuration=self,
                    )
                    for report_input_field in ReportInputField.objects.filter(item_configuration=report_item_configuration):
                        ReportInputData.objects.create(
                            name=report_input_field,
                            description=report_input_field.description,
                            field_type=report_input_field.field_type,
                            report=self,
                            item=report_item,
                            value=report_input_field.value_default,
                        )

    def get_report_config(self):
        data = {}
        ## Assemble import data from ReportInputField / ReportInputData
        for inputdata in ReportInputData.objects.filter(report=self):
            data[inputdata.name.name] = inputdata.get_value()
        return data

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
        unique_together = ["name", "report_configuration"]

# REPORT_ITEM_CATEGORY = (
    # ("NkTotalCost", "Gesamtkosten mit einfacher Verteilung (Fläche, Volumen, Faktor)"),
    # ("NkMonthlyCost", "Monatliche Kosten mit einfacher Verteilung (Fläche, Volumen, Faktor)"),
    # ("NkTotalEnergyCost", "Gesamtkosten mit einfacher Verteilung (Verbrauch)"),
    # ("NkPerRentalUnitCost", "Kosten pro Mietobjekt mit Verteilung (pro Mieteinheit, Peson, Fixum)"),
    # ("NkCostZEVStromallmend", "Stromallmend: ZEV-Kosten"),
    # ("NkCostVEWA", "VEWA: Verbrauchsabhängige Energie- und Wasserkostenabrechnung"),
# )

class ReportItemConfiguration(GenoBase):
    name = models.CharField("Element-Bezeichnung", max_length=80)
    item_category = models.CharField("Element-Kategorie", choices=REPORT_ITEM_CATEGORY, max_length=60)
    report_configuration = models.ForeignKey(ReportConfiguration, verbose_name="Report-Konfiguration", related_name="report_configuration",
                                           on_delete=models.CASCADE, default=1)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        previous_item_category = None
        if not is_new and self.pk:
            previous_item_category = (
                ReportItemConfiguration.objects.filter(pk=self.pk)
                .values_list("item_category", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if is_new or previous_item_category != self.item_category:
            self.ensure_base_input_fields(previous_item_category)

    def ensure_base_input_fields(self, previous_item_category):
        if previous_item_category != self.item_category:
            for existing_repot_input_field in ReportInputField.objects.filter(item_configuration=self.id):
                existing_repot_input_field.delete()
        # create new ReportInputField based on config

        for cost in get_costs_from_config():
            if cost.config and cost.config["name"] == self.item_category and cost.config["config"]:
                configuration = cost.config

                if configuration.get("config"):
                    for field in configuration.get("config").get_fields():
                        default_val = ""
                        if field.key not in ("class", "name", "bezeichnung"):
                            if hasattr(configuration, field.key) and configuration[field.key] is not None:
                                default_val = configuration[field.key]
                            ReportInputField.objects.create(
                                name=field.key,
                                description=field.key,
                                item_configuration=self,
                                field_type=_match_CostConfigFieldTypes_with_REPORT_FIELDTYPE_CHOICES_values(field.type),
                                active=True,
                                value_default=default_val,
                            )


    def save_as_copy(self):
        old_report_item_configuration_id = self.id
        new_report_item_configuration = super().save_as_copy()
        old_report_item_configuration = ReportItemConfiguration.objects.get(id=old_report_item_configuration_id)
        for repot_input_field in ReportInputField.objects.filter(item_configuration=old_report_item_configuration):
            new_repot_input_field = repot_input_field.save_as_copy()
            new_repot_input_field.report_configuration = new_report_item_configuration
            new_repot_input_field.save()

    class Meta:
        verbose_name = "Report-Element"
        verbose_name_plural = "Report-Elemente"
        unique_together = ["name", "item_category"]
        ordering = ["item_category", "name"]

class ReportItem(GenoBase):
    name = models.CharField("Element-Bezeichnung", max_length=80)
    item_category = models.CharField("Element-Kategorie", choices=REPORT_ITEM_CATEGORY, max_length=60)
    report_configuration = models.ForeignKey(Report, verbose_name="Report-Konfiguration", related_name="report",
                                           on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = "Report-Element"
        verbose_name_plural = "Report-Elemente"
        unique_together = ["name", "item_category"]
        ordering = ["item_category", "name"]


class ReportInputField(GenoBase):
    name = models.CharField("Name", max_length=80)
    description = models.CharField("Beschreibung", max_length=200, blank=True)
    item_configuration = models.ForeignKey(ReportItemConfiguration, verbose_name="Report-Element", related_name="report_item_configuration", on_delete=models.CASCADE, default=1)
    field_type = models.CharField("Feldtyp", choices=REPORT_FIELDTYPE_CHOICES, max_length=60)
    active = models.BooleanField("Aktiv", default=True)
    value_default = models.CharField("Standardwert", blank=True, max_length=6000)

    class Meta:
        verbose_name = "Eingabefeld"
        verbose_name_plural = "Eingabefelder"
        unique_together = ["name", "item_configuration"]
        ordering = ["item_configuration", "name"]


class ReportInputData(GenoBase):
    name = models.ForeignKey(
        ReportInputField, verbose_name="Eingabefeld", on_delete=models.CASCADE
    )
    description = models.CharField("Beschreibung", max_length=200, blank=True)
    field_type = models.CharField("Feldtyp", choices=REPORT_FIELDTYPE_CHOICES, max_length=60)
    report = models.ForeignKey(Report, verbose_name="Report", on_delete=models.CASCADE)
    item = models.ForeignKey(ReportItem, verbose_name="Report-Element",
                                           related_name="report_item",
                                           on_delete=models.CASCADE, default=1)
    value = models.CharField("Wert", blank=True, max_length=6000)  ## store lists in value?  Should be able to copy list values from spreadsheet in UI!
    # index/date/key instead of storing lists in value?

    class Meta:
        verbose_name = "Eingabewert"
        verbose_name_plural = "Eingabewerte"
        unique_together = ["name", "report"]

    def __str__(self):
        if self.name:
            return f"{self.name}"
        else:
            return "[Unbekannt]"

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
        unique_together = ["name", "report"]


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
