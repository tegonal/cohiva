"""
Models for the importer app.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ImportJob(models.Model):
    """Track import jobs and their status."""

    STATUS_CHOICES = [
        ("pending", _("Ausstehend")),
        ("processing", _("In Bearbeitung")),
        ("completed", _("Abgeschlossen")),
        ("failed", _("Fehlgeschlagen")),
    ]

    IMPORT_TYPE_CHOICES = [
        ("member_address", _("Mitglieder und Adressen")),
        ("tenant_property", _("Mieter und Liegenschaften")),
    ]

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Aktualisiert am"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Erstellt von"),
    )
    import_type = models.CharField(
        max_length=20,
        choices=IMPORT_TYPE_CHOICES,
        default="member_address",
        verbose_name=_("Import-Typ"),
    )
    file = models.FileField(upload_to="imports/%Y/%m/", verbose_name=_("Excel-Datei"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    records_imported = models.IntegerField(default=0, verbose_name=_("Importierte Datensätze"))
    error_message = models.TextField(blank=True, verbose_name=_("Fehlermeldung"))
    result_data = models.JSONField(null=True, blank=True, verbose_name=_("Ergebnisdaten"))

    class Meta:
        verbose_name = _("Import-Auftrag")
        verbose_name_plural = _("Import-Aufträge")
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Import Job {self.id} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
        )


class ImportRecord(models.Model):
    """Track individual records from an import."""

    job = models.ForeignKey(
        ImportJob,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name=_("Import-Auftrag"),
    )
    row_number = models.IntegerField(verbose_name=_("Zeilennummer"))
    data = models.JSONField(verbose_name=_("Daten"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Erstellt am"))
    error_message = models.TextField(blank=True, verbose_name=_("Fehlermeldung"))
    success = models.BooleanField(default=False, verbose_name=_("Erfolgreich"))

    class Meta:
        verbose_name = _("Import-Datensatz")
        verbose_name_plural = _("Import-Datensätze")
        ordering = ["job", "row_number"]

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} Row {self.row_number} from Job {self.job.id}"
