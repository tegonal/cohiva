from django.contrib import admin

from geno.admin import GenoBaseAdmin
from report.models import Report, ReportInputData, ReportInputField, ReportOutput, ReportType


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
    my_search_fields = ["name", "description", "comment"]
    search_fields = my_search_fields


admin.site.register(ReportType, ReportTypeAdmin)


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
    my_search_fields = ["name", "state_info", "task_id", "comment"]
    search_fields = my_search_fields


admin.site.register(Report, ReportAdmin)


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
    my_search_fields = ["name", "description", "comment"]
    search_fields = my_search_fields


admin.site.register(ReportInputField, ReportInputFieldAdmin)


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
    my_search_fields = ["name", "report__name", "value", "comment"]
    search_fields = my_search_fields


admin.site.register(ReportInputData, ReportInputDataAdmin)


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
    my_search_fields = ["name", "report__name", "value", "comment"]
    search_fields = my_search_fields


admin.site.register(ReportOutput, ReportOutputAdmin)
