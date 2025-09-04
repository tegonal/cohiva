import os

import jsonc
import select2.fields
from django.conf import settings
from django.db import models
from django.dispatch.dispatcher import receiver
from filer.models.filemodels import File as FilerFile

from geno.models import GenoBase
from geno.utils import send_error_mail


class ReportType(GenoBase):
    name = models.CharField("Name", max_length=50, unique=True)
    description = models.CharField("Beschreibung", max_length=200)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Reporttyp"
        verbose_name_plural = "Reporttypen"


REPORT_STATE_CHOICES = (
    ("new", "Neu"),
    ("pending", "Wird erstellt..."),
    ("generated", "Erstellt"),
    ("generated_dryrun", "Erstellt (Testlauf)"),
    ("invalid", "Ungültig"),
)


class Report(GenoBase):
    name = models.CharField("Name", max_length=80)
    report_type = select2.fields.ForeignKey(
        ReportType, verbose_name="Reporttyp", on_delete=models.CASCADE
    )
    task_id = models.UUIDField("Task-ID", editable=False, blank=True, null=True)
    state = models.CharField("Status", default="new", choices=REPORT_STATE_CHOICES, max_length=30)
    state_info = models.TextField("Statusinfo", blank=True)

    def get_report_config(self):
        data = {}
        ## Assemble import data from ReportInputField / ReportInputData
        for inputdata in ReportInputData.objects.filter(report=self):
            data[inputdata.name.name] = inputdata.get_value()
        return data

    def get_object_actions(self):
        actions = []
        if self.state == "new":
            actions.append((f"/report/configure/{self.pk}/", "Report konfigurieren"))
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
        unique_together = ["name", "report_type"]


REPORT_FIELDTYPE_CHOICES = (
    ("char", "Text"),
    ("int", "Ganzzahl"),
    ("float", "Dezimalzahl"),
    ("date", "Datum"),
    ("bool", "Boolean"),
    ("list_12months_float", "Dezimalzahlen, 12 Monatswerte"),
    ("file", "Datei"),
    ("json", "JSON-Daten"),
)


class ReportInputField(GenoBase):
    name = models.CharField("Name", max_length=80)
    description = models.CharField("Beschreibung", max_length=200, blank=True)
    report_type = select2.fields.ForeignKey(
        ReportType, verbose_name="Reporttyp", on_delete=models.CASCADE
    )
    field_type = models.CharField("Feldtyp", choices=REPORT_FIELDTYPE_CHOICES, max_length=30)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Eingabefeld"
        verbose_name_plural = "Eingabefelder"
        unique_together = ["name", "report_type"]
        ordering = ["report_type", "name"]


class ReportInputData(GenoBase):
    name = select2.fields.ForeignKey(
        ReportInputField, verbose_name="Eingabefeld", on_delete=models.CASCADE
    )
    report = select2.fields.ForeignKey(Report, verbose_name="Report", on_delete=models.CASCADE)
    value = models.TextField(
        "Wert"
    )  ## store lists in value?  Should be able to copy list values from spreadsheet in UI!
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
                return "[NOT FOUND]"
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
    report = select2.fields.ForeignKey(Report, verbose_name="Report", on_delete=models.CASCADE)
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
