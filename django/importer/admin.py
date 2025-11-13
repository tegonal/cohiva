"""
Admin interface for the importer app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ImportJob, ImportRecord


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
        "status_badge",
        "records_imported",
        "file_link",
    )
    list_filter = ("status", "created_at")
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
                    "status",
                    "created_by",
                )
            },
        ),
        (
            _("Results"),
            {
                "fields": (
                    "records_imported",
                    "error_message",
                    "result_data",
                )
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

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
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")

    def file_link(self, obj):
        """Display clickable file link."""
        if obj.file:
            return format_html('<a href="{}">{}</a>', obj.file.url, obj.file.name)
        return "-"

    file_link.short_description = _("File")

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

