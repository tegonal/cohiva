"""
Admin interface for the importer app.
"""

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from geno.admin import GenoBaseAdmin

from .models import ImportJob, ImportRecord
from .services import process_import_job


class ImportRecordInline(admin.TabularInline):
    model = ImportRecord
    extra = 0
    readonly_fields = ("row_number", "data", "error_message", "success")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ImportJob)
class ImportJobAdmin(GenoBaseAdmin):
    list_display = [
        "id",
        "name",
        "import_type",
        "status_badge",
        "records_imported",
        "file_link",
        "override_existing",
    ]
    list_filter = ["status", "import_type"]
    search_fields = ["id", "name"]
    readonly_fields = [
        "records_imported",
        "error_message",
        "result_data",
    ]
    inlines = [ImportRecordInline]

    fieldsets = (
        (
            _("Konfiguration"),
            {
                "fields": (
                    "name",
                    "file",
                    "import_type",
                    "override_existing",
                    "status",
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
                ),
            },
        ),
    )

    @admin.display(description=_("Status"))
    def status_badge(self, obj):
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
            obj.get_status_display(),
        )

    @admin.display(description=_("Datei"))
    def file_link(self, obj):
        if obj.file:
            # just return the first 30 characters of the file name for display
            file_name = obj.file.name[:30] + "..." if len(obj.file.name) > 30 else obj.file.name
            return format_html(
                '<a href="{}" title="{}">{}</a>', obj.file.url, obj.file.name, file_name
            )
        return "-"

    @admin.display(description=_("Import Job ausführen"))
    def call_process_import_job(self, request, queryset):
        for import_job in queryset:
            import_job = self.get_object(request, import_job.id)

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
                return redirect("admin:importer_importjob_change", import_job.id)

            try:
                results = process_import_job(import_job.id)
                self.message_user(
                    request,
                    _(
                        "Import erfolgreich verarbeitet: {} Datensätze importiert, {} Fehler"
                    ).format(results["success_count"], results["error_count"]),
                    level=messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request,
                    _("Import fehlgeschlagen: {}").format(str(e)),
                    level=messages.ERROR,
                )

            return redirect("admin:importer_importjob_change", import_job.id)

    actions = [call_process_import_job]


@admin.register(ImportRecord)
class ImportRecordAdmin(GenoBaseAdmin):
    list_display = ["id", "job", "row_number", "success"]
    list_filter = ["success", "job__status"]
    search_fields = [
        "job__id",
    ]
    readonly_fields = ["job", "row_number", "data", "error_message", "success"]

    def has_add_permission(self, request):
        return False
