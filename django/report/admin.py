from django.contrib import admin

from geno.admin import GenoBaseAdmin

from report.models import Report, ReportConfiguration, ReportInputData, ReportInputField, ReportOutput
from unfold.admin import TabularInline


@admin.register(Report)
class ReportAdmin(GenoBaseAdmin):
    model = Report
    fields = [
        "name",
        "report_type",
        "state",
        "state_info",
        "comment",
        "object_actions",
        "task_id",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "task_id",
        "report_type",
        "object_actions",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    list_display = ["name", "report_type", "state", "task_id", "comment"]
    list_filter = ["report_type", "state", "ts_created", "ts_modified"]
    search_fields = ["name", "state_info", "task_id", "comment"]

class ReportItemsInline(TabularInline):  # oder admin.StackedInline
    model = ReportConfiguration.report_items.rel.related_model
    fields = ["name", "item_category"]
    extra = 1

@admin.register(ReportConfiguration)
class ReportConfigurationAdmin(GenoBaseAdmin):
    model = ReportConfiguration
    title = "Report-Konfiguration"
    fields = [
        "name",
        "report_type",
        "buildings",
    ]
    inlines = [ReportItemsInline]
    readonly_fields = [ ]
    list_display = ["name", "report_type"]

    prevent_add_permission = ["buildings"]


@admin.register(ReportInputField)
class ReportInputFieldAdmin(GenoBaseAdmin):
    model = ReportInputField
    fields = [
        "name",
        "description",
        "item_configuration",
        "field_type",
        "active",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "item_configuration", "field_type", "active"]
    list_filter = ["item_configuration", "field_type", "active"]
    search_fields = ["name", "description", "comment"]


@admin.register(ReportInputData)
class ReportInputDataAdmin(GenoBaseAdmin):
    model = ReportInputData
    fields = [
        "name",
        "report",
        "value",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "report", "value"]
    list_filter = ["report"]
    search_fields = ["name__name", "report__name", "value", "comment"]
    autocomplete_fields = ["name", "report"]


@admin.register(ReportOutput)
class ReportOutputAdmin(GenoBaseAdmin):
    model = ReportOutput
    fields = [
        "name",
        "group",
        "report",
        "output_type",
        "value",
        "regeneration_json",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "group", "report", "output_type", "value"]
    list_filter = ["group", "report", "output_type"]
    search_fields = ["name", "report__name", "value", "comment"]
    autocomplete_fields = ["report"]
