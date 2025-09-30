from datetime import timedelta

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db import models
from django.forms import TextInput
from django.utils import timezone

from geno.admin import GenoBaseAdmin

from .forms import ReportLogEntryInlineFormset
from .models import (
    Report,
    ReportCategory,
    ReportLogEntry,
    ReportPicture,
    ReportType,
    Reservation,
    ReservationObject,
    ReservationPrice,
    ReservationType,
    ReservationUsageType,
)


class FutureDateFilter(SimpleListFilter):
    title = "Datum"
    parameter_name = "resdate"

    def lookups(self, request, model_admin):
        return [
            ("7d", "Nächste 7 Tage"),
            ("30d", "Nächste 30 Tage"),
            ("future", "Alle zukünftigen"),
            ("today", "Heute"),
            ("-7d", "Letzte 7 Tage"),
            ("-30d", "Letzte 30 Tage"),
            ("past", "Alle vergangenen"),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        range_start = None
        range_end = None
        if self.value() == "future":
            return queryset.exclude(date_end__lt=today)
        if self.value() == "past":
            return queryset.exclude(date_start__gt=today)
        if self.value() == "today":
            range_start = today
            range_end = today + timedelta(days=1)
        if self.value() == "-7d":
            range_start = today - timedelta(days=7)
            range_end = today + timedelta(days=1)
        if self.value() == "-30d":
            range_start = today - timedelta(days=30)
            range_end = today + timedelta(days=1)
        if self.value() == "7d":
            range_start = today
            range_end = today + timedelta(days=8)
        if self.value() == "30d":
            range_start = today
            range_end = today + timedelta(days=31)

        if range_start and range_end:
            return queryset.exclude(date_end__lt=range_start).exclude(date_start__gt=range_end)


@admin.register(Reservation)
class ReservationAdmin(GenoBaseAdmin):
    model = Reservation
    fields = [
        "name",
        "contact",
        "date_start",
        "date_end",
        "state",
        "summary",
        "usage_type",
        "remark",
        "key_number",
        ("key_back", "billed"),
        "is_auto_blocker",
        "flink_id",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "contact_text",
        "additional_information",
        "flink_id",
        "flink_user_id",
        "is_auto_blocker",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    list_display = [
        "name",
        "contact",
        "date_start",
        "date_end",
        "state",
        "key_number",
        "key_back",
        "billed",
        "ts_modified",
    ]
    list_editable = ["key_number", "key_back", "billed"]
    list_filter = [
        "name__reservation_type",
        "name",
        FutureDateFilter,
        "state",
        "key_back",
        "billed",
        "usage_type",
        "is_auto_blocker",
    ]
    search_fields = [
        "name__name",
        "contact__name",
        "contact__first_name",
        "contact__organization",
        "contact_text",
        "summary",
        "remark",
        "key_number",
        "additional_information",
    ]

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "10"})},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["summary"].widget.attrs["style"] = "width: 40em;"
        return form


@admin.register(ReservationObject)
class ReservationObjectAdmin(GenoBaseAdmin):
    model = ReservationObject
    fields = [
        "name",
        "reservation_type",
        "short_description",
        "description",
        "image",
        "usage_types",
        "cost",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "reservation_type", "short_description", "cost"]
    list_filter = ["reservation_type", "usage_types"]
    search_fields = ["name", "short_description", "description"]

    filter_horizontal = ["usage_types"]


@admin.register(ReservationType)
class ReservationTypeAdmin(GenoBaseAdmin):
    model = ReservationType
    fields = [
        "name",
        "required_role",
        "fixed_time",
        "default_time_start",
        "default_time_end",
        "summary_required",
        "confirmation_email_template",
        "confirmation_email_sender",
        "color",
        "active",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "required_role", "active", "color"]
    list_filter = ["active", "required_role"]
    search_fields = ["name"]


class ReservationPriceInline(admin.TabularInline):
    model = ReservationPrice
    fields = [
        "name",
        "priority",
        ("time_unit", "duration_min", "duration_max"),
        ("cost", "cost_type"),
    ]


#    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
#        field = super(ReservationPriceInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
#        if db_field.name == 'is_backup_for':
#            if request._obj_ is not None:
#                field.queryset = field.queryset.filter(event__exact = request._obj_)
#            else:
#                field.queryset = field.queryset.none()
#        return field


@admin.register(ReservationPrice)
class ReservationPriceAdmin(GenoBaseAdmin):
    model = ReservationPrice
    fields = [
        "name",
        "usage_type",
        "priority",
        ("time_unit", "duration_min", "duration_max"),
        ("cost", "cost_type"),
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "usage_type", "priority", "cost"]
    list_filter = ["usage_type", "cost_type"]
    search_fields = ["name", "usage_type__label", "usage_type__name"]


@admin.register(ReservationUsageType)
class ReservationUsageTypeAdmin(GenoBaseAdmin):
    model = ReservationUsageType
    fields = ["name", "label", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "label"]
    list_filter = []
    search_fields = ["name", "label"]

    inlines = [ReservationPriceInline]


@admin.register(ReportCategory)
class ReportCategoryAdmin(GenoBaseAdmin):
    model = ReportCategory
    fields = ["name", "report_type", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "report_type"]
    list_filter = ["report_type"]
    search_fields = ["name"]


@admin.register(ReportType)
class ReportTypeAdmin(GenoBaseAdmin):
    model = ReportType
    fields = ["name", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name"]
    list_filter = []
    search_fields = ["name"]


@admin.register(ReportPicture)
class ReportPictureAdmin(GenoBaseAdmin):
    model = ReportPicture
    fields = ["name", "image", "report", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "image", "report"]
    list_filter = ["report__status"]
    search_fields = ["name"]


class ReportPictureInline(admin.TabularInline):
    model = ReportPicture
    fields = ["name", "image"]
    extra = 0


@admin.register(ReportLogEntry)
class ReportLogEntryAdmin(GenoBaseAdmin):
    model = ReportLogEntry
    fields = ["name", "text", "user", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "text", "user", "ts_modified"]
    list_filter = []
    search_fields = ["name__name", "text"]


class ReportLogEntryInline(admin.TabularInline):
    model = ReportLogEntry
    formset = ReportLogEntryInlineFormset
    fields = ["text"]
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset


@admin.register(Report)
class ReportAdmin(GenoBaseAdmin):
    model = Report
    fields = [
        "name",
        "report_type",
        "category",
        "rental_unit",
        "contact",
        "contact_text",
        "text",
        "report_date",
        ("status", "status_date"),
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["status_date", "ts_created", "ts_modified", "links", "backlinks"]
    list_display = [
        "id",
        "name",
        "category",
        "rental_unit",
        "contact",
        "report_date",
        "status_date",
        "status",
    ]
    list_filter = [
        "status",
        "report_type",
        "category",
        "status",
        "rental_unit",
        "report_date",
        "status_date",
    ]
    search_fields = [
        "id",
        "name",
        "contact__name",
        "contact__first_name",
        "contact_text",
        "rental_unit__name",
        "text",
    ]

    inlines = [ReportPictureInline, ReportLogEntryInline]
