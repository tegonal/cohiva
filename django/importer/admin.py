"""
Admin interface for the importer app.
"""

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ImportJob, ImportRecord
from .services import process_import_job


class ImportRecordInline(admin.TabularInline):
    """Inline admin for import records."""

    model = ImportRecord
    extra = 0
    readonly_fields = ("row_number", "data", "error_message", "success", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    """Admin interface for import jobs."""

    list_display = (
        "id",
        "created_at",
        "created_by",
        "import_type",
        "status_badge",
        "records_imported",
        "file_link",
    )
    list_filter = ("status", "import_type", "created_at")
    search_fields = ("id", "created_by__username", "created_by__email")
    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "records_imported",
        "error_message",
        "result_data",
    )
    inlines = [ImportRecordInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "file",
                    "import_type",
                    "status",
                    "created_by",
                )
            },
        ),
        (
            _("Ergebnisse"),
            {
                "fields": (
                    "records_imported",
                    "error_message",
                    "result_data",
                )
            },
        ),
        (
            _("Zeitstempel"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_urls(self):
        """Add custom URLs for processing imports."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:job_id>/process/",
                self.admin_site.admin_view(self.process_import_view),
                name="importer_importjob_process",
            ),
        ]
        return custom_urls + urls

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            "pending": "gray",
            "processing": "blue",
            "completed": "green",
            "failed": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")

    def file_link(self, obj):
        """Display clickable file link."""
        if obj.file:
            # just return the first 30 characters of the file name for display
            file_name = obj.file.name[:30] + "..." if len(obj.file.name) > 30 else obj.file.name
            return format_html('<a href="{}">{}</a>', obj.file.url, file_name)
        return "-"

    file_link.short_description = _("Datei")

    @admin.display(description=_("Import Job ausführen"))
    def process_import_view(self, request, job_id):
        """Process an import job."""
        import_job = self.get_object(request, job_id)

        if import_job is None:
            self.message_user(
                request,
                _("Import-Auftrag nicht gefunden."),
                level=messages.ERROR,
            )
            return redirect("admin:importer_importjob_changelist")

        if import_job.status != "pending":
            self.message_user(
                request,
                _("Import-Auftrag kann nicht verarbeitet werden. Status: {}").format(
                    import_job.get_status_display()
                ),
                level=messages.WARNING,
            )
            return redirect("admin:importer_importjob_change", job_id)

        try:
            results = process_import_job(job_id)
            self.message_user(
                request,
                _("Import erfolgreich verarbeitet: {} Datensätze importiert, {} Fehler").format(
                    results["success_count"], results["error_count"]
                ),
                level=messages.SUCCESS,
            )
        except Exception as e:
            self.message_user(
                request,
                _("Import fehlgeschlagen: {}").format(str(e)),
                level=messages.ERROR,
            )

        return redirect("admin:importer_importjob_change", job_id)

    def save_model(self, request, obj, form, change):
        """Set created_by when creating a new import job."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ImportRecord)
class ImportRecordAdmin(admin.ModelAdmin):
    """Admin interface for import records."""

    list_display = ("id", "job", "row_number", "success", "created_at")
    list_filter = ("success", "job__status", "created_at")
    search_fields = ("job__id",)
    readonly_fields = ("job", "row_number", "data", "error_message", "success", "created_at")

    def has_add_permission(self, request):
        return False
