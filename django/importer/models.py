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
        ("pending", _("Pending")),
        ("processing", _("Processing")),
        ("completed", _("Completed")),
        ("failed", _("Failed")),
    ]

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    file = models.FileField(upload_to="imports/%Y/%m/", verbose_name=_("Excel file"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    records_imported = models.IntegerField(default=0, verbose_name=_("Records imported"))
    error_message = models.TextField(blank=True, verbose_name=_("Error message"))
    result_data = models.JSONField(
        null=True, blank=True, verbose_name=_("Result data")
    )

    class Meta:
        verbose_name = _("Import Job")
        verbose_name_plural = _("Import Jobs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Import Job {self.id} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ImportRecord(models.Model):
    """Track individual records from an import."""

    job = models.ForeignKey(
        ImportJob,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name=_("Import job"),
    )
    row_number = models.IntegerField(verbose_name=_("Row number"))
    data = models.JSONField(verbose_name=_("Data"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    error_message = models.TextField(blank=True, verbose_name=_("Error message"))
    success = models.BooleanField(default=False, verbose_name=_("Success"))

    class Meta:
        verbose_name = _("Import Record")
        verbose_name_plural = _("Import Records")
        ordering = ["job", "row_number"]

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} Row {self.row_number} from Job {self.job.id}"

