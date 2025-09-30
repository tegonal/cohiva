from django.contrib import admin

from geno.admin import GenoBaseAdmin
from report.models import Report, ReportInputData, ReportInputField, ReportOutput, ReportType


@admin.register(ReportType)
class ReportTypeAdmin(GenoBaseAdmin):
    model = ReportType
    fields = [
        "name",
        "description",
        "active",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "active"]
    list_filter = ["active"]
    search_fields = ["name", "description", "comment"]


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
        "object_actions",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    list_display = ["name", "report_type", "state", "task_id", "comment"]
    list_filter = ["report_type", "state", "ts_created", "ts_modified"]
    search_fields = ["name", "state_info", "task_id", "comment"]


@admin.register(ReportInputField)
class ReportInputFieldAdmin(GenoBaseAdmin):
    model = ReportInputField
    fields = [
        "name",
        "description",
        "report_type",
        "field_type",
        "active",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "report_type", "field_type", "active"]
    list_filter = ["report_type", "field_type", "active"]
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
    search_fields = ["name", "report__name", "value", "comment"]


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
