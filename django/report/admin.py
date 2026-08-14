import json
from datetime import date

import jsonc
from django import forms
from django.contrib import admin
from unfold.admin import TabularInline

from geno.admin import GenoBaseAdmin
from report.forms import _make_report_input_field
from report.models import (
    Report,
    ReportConfiguration,
    ReportInputData,
    ReportInputField,
    ReportItem,
    ReportItemConfiguration,
    ReportOutput,
)


class ReportInputAdminForm(forms.ModelForm):
    value_field_name = "value"

    class Meta:
        model = None
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_field = self._get_input_field()
        if not input_field:
            return

        field_name = self.get_value_field_name()

        # Transform field values loaded from the model to match the format
        # expected by the form field
        self.initial[field_name] = self._deserialize_value(input_field)
        self.fields[field_name] = _make_report_input_field(input_field)

    def get_value_field_name(self):
        return self.value_field_name

    def _get_input_field(self) -> ReportInputField | None:
        name_id = self._get_name_id()
        if not name_id:
            return None
        try:
            return ReportInputField.objects.get(pk=name_id)
        except (ReportInputField.DoesNotExist, ValueError, TypeError):
            return None

    def _get_name_id(self):
        if self.instance and self.instance.pk and getattr(self.instance, "name_id", None):
            return self.instance.name_id
        return self.data.get("name") or self.initial.get("name")

    def _get_raw_value(self):
        return getattr(self.instance, self.get_value_field_name(), "")

    def _deserialize_value(self, input_field: ReportInputField):
        raw_value = self._get_raw_value()
        if raw_value in (None, ""):
            return ""

        field_type = input_field.field_type
        if field_type == "bool":
            return str(raw_value).lower() in ["true", "1", "yes"]
        if field_type == "date":
            if isinstance(raw_value, date):
                return raw_value
            try:
                return date.fromisoformat(str(raw_value))
            except ValueError:
                return ""
        if field_type == "int":
            try:
                return int(raw_value)
            except (TypeError, ValueError):
                return ""
        if field_type == "float":
            try:
                return float(raw_value)
            except (TypeError, ValueError):
                return ""
        if field_type == "file" and str(raw_value).startswith("filer:"):
            try:
                return int(str(raw_value)[6:])
            except ValueError:
                return ""
        if field_type == "json":
            if isinstance(raw_value, str):
                try:
                    return jsonc.loads(raw_value)
                except Exception:
                    return raw_value
            try:
                return json.loads(json.dumps(raw_value))
            except (TypeError, ValueError):
                return raw_value
        return raw_value

    def _serialize_value(self, value):
        input_field = self._get_input_field()
        if not input_field:
            return "" if value in (None, "") else str(value)

        field_type = input_field.field_type
        if value in (None, ""):
            return ""
        if field_type == "json":
            try:
                return json.dumps(value)
            except (TypeError, ValueError):
                return str(value)
        if field_type == "file":
            return f"filer:{value.pk}" if hasattr(value, "pk") else ""
        if field_type == "bool":
            return "true" if value else "false"
        if isinstance(value, date):
            return value.isoformat()
        return str(value)

    def clean(self):
        cleaned_data = super().clean()
        field_name = self.get_value_field_name()
        if cleaned_data and field_name in cleaned_data:
            cleaned_data[field_name] = self._serialize_value(cleaned_data.get(field_name))
        return cleaned_data


class ReportInputDataAdminForm(ReportInputAdminForm):
    class Meta:
        model = ReportInputData
        fields = "__all__"


class ReportInputFieldForm(ReportInputAdminForm):
    value_field_name = "value_default"

    class Meta:
        model = ReportInputField
        fields = "__all__"

    def _get_input_field(self):
        return self.instance


class ReportInputDataInline(TabularInline):  # oder admin.StackedInline
    model = ReportInputData
    fields = ["description", "value"]
    readonly_fields = ["field_type"]
    form = ReportInputDataAdminForm
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    extra = 0


class ReportItemsInline(TabularInline):  # oder admin.StackedInline
    model = ReportItem
    fields = ["order", "name", "item_category"]
    inlines = [ReportInputDataInline]
    extra = 0


@admin.register(Report)
class ReportAdmin(GenoBaseAdmin):
    model = Report
    fields = [
        "name",
        "report_configuration",
        "state",
        "state_info",
        "comment",
        "object_actions",
        "task_id",
        ("ts_created", "ts_modified"),
        "links",
    ]
    readonly_fields = [
        "task_id",
        "object_actions",
        "ts_created",
        "ts_modified",
        "links",
    ]
    inlines = [ReportItemsInline]
    list_display = ["name", "report_configuration", "state", "task_id", "comment"]
    list_filter = ["report_configuration", "state", "ts_created", "ts_modified"]
    search_fields = ["name", "state_info", "task_id", "comment"]


class ReportInputFieldInline(TabularInline):  # oder admin.StackedInline
    model = ReportInputField
    fields = ["description", "value_default", "active"]
    readonly_fields = ["name", "field_type"]
    form = ReportInputFieldForm
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    extra = 0


class ReportItemConfigurationsInline(TabularInline):  # oder admin.StackedInline
    model = ReportItemConfiguration
    fields = ["order", "name", "item_category"]
    inlines = [ReportInputFieldInline]
    extra = 0


@admin.register(ReportConfiguration)
class ReportConfigurationAdmin(GenoBaseAdmin):
    model = ReportConfiguration
    title = "Report-Konfiguration"
    fields = [
        "name",
        "report_type",
        "buildings",
    ]
    inlines = [ReportItemConfigurationsInline]
    readonly_fields = []
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
    form = ReportInputDataAdminForm
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
