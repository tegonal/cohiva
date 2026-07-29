import datetime
import gettext
from collections.abc import Callable

import pycountry
from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from stdnum import iban as iban_util
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

import geno.settings as geno_settings
from cohiva.utils.countries import normalize_country_code
from geno.exporter import ExportXlsMixin
from geno.models import (
    Address,
    BankAccount,
    Building,
    Child,
    ContentTemplate,
    ContentTemplateOption,
    ContentTemplateOptionType,
    Contract,
    Document,
    DocumentType,
    GenericAttribute,
    Invoice,
    InvoiceCategory,
    LookupTable,
    Member,
    MemberAttribute,
    MemberAttributeType,
    Registration,
    RegistrationEvent,
    RegistrationSlot,
    RentalUnit,
    Share,
    ShareType,
    Tenant,
    TenantsView,
)


@admin.display(description="Ausgewählte Objekte kopieren")
def copy_objects(modeladmin, request, queryset):
    count = 0
    for obj in queryset:
        try:
            obj.save_as_copy()
            count += 1
        except:
            if settings.DEBUG:
                raise
            messages.error(request, "Objekte dieses Typs können nicht kopiert werden.")
            return
    messages.success(request, f"{count} Objekt(e) kopiert.")


class ShareStateFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "payment_state"

    def __init__(self, request, params, model, model_admin):
        self.state = model._meta.get_field("payment_state")
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        states = [("gefordert", "gefordert"),
                  ("bezahlt", "bezahlt"),
                  ("beendet", "beendet")]
        return states

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(state=value)
        return queryset


class BooleanFieldDefaultTrueListFilter(admin.BooleanFieldListFilter):
    """
    Filter a boolean field `active`.
    Default: only True (active) records.
    When ‘All’ is chosen the URL will contain ?active=all (never removed).
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.lookup_val is None:
            self.lookup_val = True
        elif self.lookup_val in ("1", "0"):
            self.lookup_val = bool(int(self.lookup_val))
        # Add the model name to the label if the filter uses a boolean field of a related object.
        if field.model and field.model != model:
            self.title = f"{self.title} ({field.model._meta.verbose_name.title()})"

    def choices(self, changelist):
        if self.lookup_val == "all":
            selected = "all"
        elif self.lookup_val:
            selected = "1"
        else:
            selected = "0"
        yield from [
            {
                "selected": selected == "all",
                "query_string": changelist.get_query_string({self.lookup_kwarg: "all"}),
                "display": "Alle",
            },
            {
                "selected": selected == "1",
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: "1"},
                ),
                "display": "Aktive",
            },
            {
                "selected": selected == "0",
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: "0"},
                ),
                "display": "Inaktive",
            },
        ]

    def queryset(self, request, queryset):
        if self.lookup_val == "all":
            return queryset
        else:
            return queryset.filter(**{self.lookup_kwarg: self.lookup_val})


## Base admin class
class GenoBaseAdmin(ModelAdmin, ExportXlsMixin):
    model = None
    view_on_site = False
    save_as = True
    save_on_top = True
    actions = ["export_as_xls", copy_objects]

    # Add custom admin JS (focus handling for select2 focus)
    class Media:
        js = ("geno/js/select2-focus.js",)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        module_name = self.__module__
        class_name = type(self).__name__
        ## Apply custom admin config
        if (
            hasattr(settings, "COHIVA_ADMIN_FIELDS")
            and module_name in settings.COHIVA_ADMIN_FIELDS
        ):
            self._overwrite_admin_config(settings.COHIVA_ADMIN_FIELDS.get(module_name))
        if (
            hasattr(settings, "COHIVA_HIDE_ADMIN_FIELDS")
            and module_name in settings.COHIVA_HIDE_ADMIN_FIELDS
        ):
            self._remove_admin_fields(
                settings.COHIVA_HIDE_ADMIN_FIELDS.get(module_name).get(class_name, [])
            )

    @classmethod
    def _overwrite_admin_config(cls, config: dict[str, list | tuple]) -> None:
        for attr in (
            "fields",
            "fieldsets",
            "readonly_fields",
            "search_fields",
            "autocomplete_fields",
            "list_display",
            "list_filter",
        ):
            setting_name = f"{cls.__name__}.{attr}"
            if setting_name in config:
                setattr(cls, attr, config[setting_name])

    @classmethod
    def _remove_admin_fields(cls, fields_to_remove: list[str]) -> None:
        def filter_fields(field_list: list) -> list:
            filtered_list = []
            for f in field_list:
                if isinstance(f, str) and f in fields_to_remove:
                    continue
                filtered_list.append(f)
            return filtered_list

        if not fields_to_remove:
            return

        cls._remove_admin_fields_from_fields(filter_fields)
        cls._remove_admin_fields_from_fieldsets(filter_fields)
        cls._remove_admin_fields_from_attributes(
            filter_fields, ("search_fields", "list_display", "list_filter")
        )

    @classmethod
    def _remove_admin_fields_from_fields(cls, filter_func: Callable[[list], list]) -> None:
        """Remove fields from the fields attribute of the class, if present.

        The fields attribute is a list/tuple that contains field names or
        field name groups (lists/tuples of strings).
        """
        if hasattr(cls, "fields") and isinstance(cls.fields, (list, tuple)):
            filtered_fields = []
            for field in cls.fields:
                if isinstance(field, str) and not filter_func([field]):
                    continue
                if isinstance(field, (list, tuple)):
                    filtered_subset = filter_func(field)
                    if filtered_subset:
                        filtered_fields.append(tuple(filtered_subset))
                else:
                    filtered_fields.append(field)
            cls.fields = filtered_fields

    @classmethod
    def _remove_admin_fields_from_fieldsets(cls, filter_func: Callable[[list], list]) -> None:
        """Remove fields from the fieldsets attribute of the class, if present.

        The fieldsets attribute is a list/tuple of fieldsets of the form
          ( "Fieldset label", {"fields": ("field 1", "field 2")} )
        """
        if hasattr(cls, "fieldsets") and isinstance(cls.fieldsets, (list, tuple)):
            for fieldset in cls.fieldsets:
                if (
                    isinstance(fieldset, (list, tuple))
                    and len(fieldset) > 1
                    and isinstance(fieldset[1], dict)
                    and "fields" in fieldset[1]
                ):
                    filtered_fields = []
                    for field in fieldset[1].get("fields", []):
                        if isinstance(field, str):
                            if filter_func([field]):
                                filtered_fields.append(field)
                        elif isinstance(field, (list, tuple)):
                            filtered_subset = filter_func(list(field))
                            if filtered_subset:
                                filtered_fields.append(tuple(filtered_subset))
                        else:
                            filtered_fields.append(field)
                    fieldset[1]["fields"] = filtered_fields

    @classmethod
    def _remove_admin_fields_from_attributes(
        cls, filter_func: Callable[[list], list], attributes: tuple[str, ...]
    ) -> None:
        """
        Remove fields from the attributes listed in the attributes parameter, if present.

        The attribute must be a list/tuple of field names or lists/tuples with the field name
        as the first element.
        """
        for attr in attributes:
            fields = getattr(cls, attr, [])
            if isinstance(fields, (list, tuple)):
                filtered_fields = []
                for field in getattr(cls, attr):
                    field_name = None
                    if isinstance(field, str):
                        field_name = field
                    elif (
                        isinstance(field, (list, tuple))
                        and len(field)
                        and isinstance(field[0], str)
                    ):
                        field_name = field[0]
                    if field_name and not filter_func([field_name]):
                        continue
                    filtered_fields.append(field)
                setattr(cls, attr, filtered_fields)


@admin.display(description="Anrede auf 'Herr' setzen")
def set_title_mr(modeladmin, request, queryset):
    queryset.update(title="Herr")


@admin.display(description="Anrede auf 'Frau' setzen")
def set_title_mrs(modeladmin, request, queryset):
    queryset.update(title="Frau")


class CountryFilter(admin.SimpleListFilter):
    parameter_name = "country"

    def __init__(self, request, params, model, model_admin):
        self.title = model._meta.get_field("country").verbose_name
        self.de_trans = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["de"])
        org_country = settings.GENO_ORG_INFO.get("country", "")
        self.org_country_code = normalize_country_code(org_country)
        super().__init__(request, params, model, model_admin)

    def get_country_name(self, country_code):
        if not country_code:
            return ""
        iso_country_code = str(country_code).strip().upper()
        # Get a country name when the country code is ISO-compliant
        country = pycountry.countries.get(alpha_2=iso_country_code)
        return self.de_trans.gettext(country.name) if country else country_code

    def lookups(self, request, model_admin):
        options = []

        if self.org_country_code:
            org_country_name = self.get_country_name(self.org_country_code)
            options.append((self.org_country_code, org_country_name))
            options.append(("NOT_ORG_COUNTRY", f"Nicht {org_country_name}"))

        used_countries = (
            model_admin.model.objects.exclude(country__isnull=True)
            .exclude(country__exact="")
            .values_list("country", flat=True)
            .distinct()
            .order_by("country")
        )

        remaining_countries = [
            (code, self.get_country_name(code))
            for code in used_countries
            if code != self.org_country_code
        ]
        remaining_countries.sort(key=lambda item: item[1])
        options.extend(remaining_countries)

        return options

    def queryset(self, request, queryset):
        value = self.value()

        if value == "NOT_ORG_COUNTRY" and self.org_country_code:
            return queryset.exclude(country=self.org_country_code)
        elif value:
            return queryset.filter(country=value)

        return queryset


@admin.register(Address)
class AddressAdmin(GenoBaseAdmin):
    model = Address
    fields = [
        "organization",
        ("name", "first_name"),
        ("title", "formal"),
        "extra",
        ("street_name", "house_number", "po_box", "po_box_number"),
        ("city_zipcode", "city_name", "country"),
        ("telephone", "mobile", "telephoneOffice", "telephoneOffice2"),
        ("email", "email2", "website"),
        "date_birth",
        "hometown",
        "occupation",
        "ahv_number",
        ("bankaccount", "interest_action"),
        "paymentslip",
        "ignore_in_lists",
        "login_permission",
        "active",
        "comment",
        ("carddav_href", "carddav_etag", "carddav_syncts"),
        ("ts_created", "ts_modified"),
        ("import_id", "random_id"),
        "user",
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "ts_created",
        "ts_modified",
        "import_id",
        "random_id",
        "object_actions",
        "links",
        "backlinks",
        "carddav_href",
        "carddav_etag",
        "carddav_syncts",
    ]
    list_display = [
        "list_name",
        "organization",
        "name",
        "first_name",
        "city_zipcode",
        "city_name",
        "telephone",
        "email",
        "ts_created",
        "ts_modified",
        "comment",
    ]
    list_filter = [
        "title",
        ("active", BooleanFieldDefaultTrueListFilter),
        "formal",
        "paymentslip",
        "interest_action",
        "ignore_in_lists",
        "login_permission",
        "po_box",
        CountryFilter,
        "ts_created",
        "ts_modified",
    ]
    search_fields = [
        "organization",
        "name",
        "first_name",
        "extra",
        "street_name",
        "city_name",
        "country",
        "telephone",
        "mobile",
        "email",
        "email2",
        "occupation",
        "comment",
    ]
    autocomplete_fields = ["user"]
    actions = GenoBaseAdmin.actions + [set_title_mr, set_title_mrs]
    actions_list = [
        "export_address_list",
        {
            "title": _("Weitere Aktionen"),
            "items": ["export_adit"],
            # "variant": ActionVariant.PRIMARY,
        },
    ]

    def get_search_results(self, request, queryset, search_term):
        # Remove commas from the search term to allow hits for terms in the
        # form "Last Name, First Name".
        search_term = search_term.replace(",", " ")
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            # Add an integer search "ranking" according to the field that the
            # search term matches on.
            queryset = queryset.annotate(
                _search_rank=Case(
                    When(
                        Q(name__icontains=search_term)
                        | Q(first_name__icontains=search_term)
                        | Q(organization__icontains=search_term),
                        then=Value(0),
                    ),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by("_search_rank", "name", "first_name", "organization")
        return queryset, use_distinct

    @action(
        description=_("Export"),
        permissions=["geno.canview_member"],
        icon="download",
        # variant=ActionVariant.PRIMARY,
    )
    def export_address_list(self, request):
        return redirect(reverse("geno:address_export"))

    @action(
        description=_("Export ADIT"),
        permissions=["geno.canview_member", "geno.adit"],
        icon="doorbell",
    )
    def export_adit(self, request):
        return redirect(reverse("geno:generic-export", args=("adit",)))


@admin.display(description="Als '%s' markieren" % geno_settings.MEMBER_FLAGS[1])
def mark_flag_01(modeladmin, request, queryset):
    queryset.update(flag_01=True)


@admin.display(description="Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[1])
def unmark_flag_01(modeladmin, request, queryset):
    queryset.update(flag_01=False)


@admin.display(description="Als '%s' markieren" % geno_settings.MEMBER_FLAGS[2])
def mark_flag_02(modeladmin, request, queryset):
    queryset.update(flag_02=True)


@admin.display(description="Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[2])
def unmark_flag_02(modeladmin, request, queryset):
    queryset.update(flag_02=False)


@admin.display(description="Als '%s' markieren" % geno_settings.MEMBER_FLAGS[3])
def mark_flag_03(modeladmin, request, queryset):
    queryset.update(flag_03=True)


@admin.display(description="Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[3])
def unmark_flag_03(modeladmin, request, queryset):
    queryset.update(flag_03=False)


@admin.display(description="Als '%s' markieren" % geno_settings.MEMBER_FLAGS[4])
def mark_flag_04(modeladmin, request, queryset):
    queryset.update(flag_04=True)


@admin.display(description="Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[4])
def unmark_flag_04(modeladmin, request, queryset):
    queryset.update(flag_04=False)


@admin.display(description="Als '%s' markieren" % geno_settings.MEMBER_FLAGS[5])
def mark_flag_05(modeladmin, request, queryset):
    queryset.update(flag_05=True)


@admin.display(description="Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[5])
def unmark_flag_05(modeladmin, request, queryset):
    queryset.update(flag_05=False)


@admin.display(description="Email Versand an ausgewählte Mitglieder")
def member_send_membermail(modeladmin, request, queryset):
    request.session["members"] = []
    members_processed = []
    for member in queryset:
        if member.pk not in members_processed:
            request.session["members"].append(
                {"id": member.pk, "member": str(member), "extra_info": "", "member_type": "member"}
            )
            members_processed.append(member.pk)
    return HttpResponseRedirect("/geno/member/send_mail/select/")


class MemberAttributeTabularInline(TabularInline):
    model = MemberAttribute
    fields = ["date", "value", "attribute_type", "comment"]
    tab = True


@admin.register(Member)
class MemberAdmin(GenoBaseAdmin):
    inlines = [MemberAttributeTabularInline]  # model = Member
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "date_join",
                    "date_leave",
                ),
            },
        ),
        (
            "Kategorien",
            {
                "fields": ("flag_01", "flag_02", "flag_03", "flag_04", "flag_05"),
                "classes": ["tab"],
            },
        ),
        ("Zusatzinfos", {"fields": ("notes", "ts_created", "ts_modified"), "classes": ["tab"]}),
        ("Verknüpfungen", {"fields": ("links", "backlinks"), "classes": ["tab"]}),
        ("Aktionen", {"fields": ("object_actions",), "classes": ["tab"]}),
    )
    readonly_fields = [
        "active",
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
    list_display = ["name", "date_join", "date_leave"]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
        "flag_01",
        "flag_02",
        "flag_03",
        "flag_04",
        "flag_05",
        "date_join",
        "date_leave",
    ]
    search_fields = ["name__organization", "name__name", "name__first_name", "notes"]
    autocomplete_fields = ["name"]
    actions = GenoBaseAdmin.actions + [
        mark_flag_01,
        unmark_flag_01,
        mark_flag_02,
        unmark_flag_02,
        mark_flag_03,
        unmark_flag_03,
        mark_flag_04,
        unmark_flag_04,
        mark_flag_05,
        unmark_flag_05,
        member_send_membermail,
    ]


@admin.register(Child)
class ChildAdmin(GenoBaseAdmin):
    model = Child
    fields = [
        "name",
        ("presence", "age"),
        "parents",
        "notes",
        "import_id",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["age", "import_id", "ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "presence", "parents", "age"]
    list_filter = ["presence", ("name__active", BooleanFieldDefaultTrueListFilter)]
    search_fields = ["name__name", "name__first_name", "parents", "notes"]
    autocomplete_fields = ["name"]


@admin.register(Building)
class BuildingAdmin(GenoBaseAdmin):
    model = Building
    fields = [
        "name",
        "description",
        ("street_name", "house_number"),
        ("city_zipcode", "city_name", "country"),
        "egid",
        ("value_insurance", "value_build"),
        "accounting_postfix",
        "team",
        "active",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "active"]
    list_filter = [("active", BooleanFieldDefaultTrueListFilter)]
    search_fields = ["name", "description", "team"]


@admin.register(Tenant)
class TenantAdmin(GenoBaseAdmin):
    model = Tenant
    fields = [
        "name",
        "building",
        "key_number",
        "invitation_date",
        "notes",
        "active",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "building", "key_number", "active"]
    list_filter = [
        "building__name",
        ("active", BooleanFieldDefaultTrueListFilter),
        ("building__active", BooleanFieldDefaultTrueListFilter),
    ]
    search_fields = ["name__name", "name__first_name", "building__name", "key_number", "notes"]
    autocomplete_fields = ["name", "building"]


@admin.register(MemberAttributeType)
class MemberAttributeTypeAdmin(GenoBaseAdmin):
    model = MemberAttributeType
    fields = ["name", "description"]
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


@admin.display(description='Attribut-Wert auf "Bezahlt" setzen')
def mark_paid(modeladmin, request, queryset):
    queryset.update(value="Bezahlt", date=datetime.date.today())


@admin.display(description='Attribut-Wert auf "Rechnung geschickt" setzen')
def mark_billed(modeladmin, request, queryset):
    queryset.update(value="Rechnung geschickt", date=datetime.date.today())


@admin.display(description='Attribut-Wert auf "Mahnung geschickt" setzen')
def mark_reminder(modeladmin, request, queryset):
    queryset.update(value="Mahnung geschickt", date=datetime.date.today())


@admin.display(description="Email Versand an ausgewählte Mitglieder")
def member_attribute_send_membermail(modeladmin, request, queryset):
    request.session["members"] = []
    members_processed = []
    for att in queryset:
        member = att.member
        if member.pk not in members_processed:
            request.session["members"].append(
                {"id": member.pk, "member": str(member), "extra_info": "", "member_type": "member"}
            )
            members_processed.append(member.pk)
    return HttpResponseRedirect("/geno/member/send_mail/select/")


@admin.register(MemberAttribute)
class MemberAttributeAdmin(GenoBaseAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "attribute_type":
            kwargs["queryset"] = MemberAttributeType.objects.order_by("-name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    model = MemberAttribute
    fields = [
        "member",
        "attribute_type",
        "date",
        "value",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["member", "attribute_type", "date", "value"]
    list_filter = [
        "attribute_type",
        "value",
        "member__flag_01",
        "member__flag_02",
        "member__flag_03",
        "member__flag_04",
        "member__flag_05",
        "date",
    ]
    search_fields = [
        "member__name__organization",
        "member__name__name",
        "member__name__first_name",
        "attribute_type__name",
        "value",
        "comment",
    ]
    autocomplete_fields = ["member", "attribute_type"]
    actions = GenoBaseAdmin.actions + [
        mark_billed,
        mark_paid,
        mark_reminder,
        member_attribute_send_membermail,
    ]


@admin.register(ShareType)
class ShareTypeAdmin(GenoBaseAdmin):
    model = ShareType
    fields = ["name", "description", "standard_interest"]
    list_display = ["name", "description", "standard_interest"]
    list_filter = ["standard_interest"]
    search_fields = ["name", "description"]


@admin.display(description='Als "bezahlt" markieren')
def share_mark_paid(modeladmin, request, queryset):
    queryset.update(state="bezahlt", date=datetime.date.today())


@admin.display(description='Als "gefordert" markieren')
def share_mark_billed(modeladmin, request, queryset):
    queryset.update(state="gefordert", date=datetime.date.today())


@admin.display(description="Laufzeit löschen")
def share_delete_duration(modeladmin, request, queryset):
    queryset.update(duration=None)


@admin.display(description="Laufzeit auf 5 Jahre setzen")
def share_set_duration5(modeladmin, request, queryset):
    queryset.update(duration=5)


@admin.display(description="Laufzeit auf 10 Jahre setzen")
def share_set_duration10(modeladmin, request, queryset):
    queryset.update(duration=10)


@admin.display(description=("Datum Ende auf 31.12. des Vorjahres (=Jahresende) setzen"))
def share_set_end_endofyear(modeladmin, request, queryset):
    queryset.update(repayment_date=datetime.date(datetime.datetime.now().year - 1, 12, 31))


@admin.display(description=("Datum Ende auf 31.12. vor ZWEI Jahren (=Jahresende) setzen"))
def share_set_end_endofyear2(modeladmin, request, queryset):
    queryset.update(repayment_date=datetime.date(datetime.datetime.now().year - 2, 12, 31))


@admin.display(description="Zinsatz-Modus auf «Standard» setzen.")
def share_set_interest_mode_standard(modeladmin, request, queryset):
    queryset.update(interest_mode="Standard")


@admin.display(description="Email Versand an ausgewählte Mitglieder")
def share_send_membermail(modeladmin, request, queryset):
    request.session["members"] = []
    members_processed = []
    addresses_processed = []
    for share in queryset:
        adr = share.name
        try:
            member = Member.objects.get(name=adr)
            if member.pk not in members_processed:
                request.session["members"].append(
                    {
                        "id": member.pk,
                        "member": str(member),
                        "extra_info": "",
                        "member_type": "member",
                    }
                )
                members_processed.append(member.pk)
        except Member.DoesNotExist:
            if adr.pk not in addresses_processed:
                request.session["members"].append(
                    {"id": adr.pk, "member": str(adr), "extra_info": "", "member_type": "address"}
                )
                addresses_processed.append(adr.pk)

    return HttpResponseRedirect("/geno/member/send_mail/select/")


@admin.register(Share)
class ShareAdmin(GenoBaseAdmin):
    model = Share
    fields = [
        "name",
        "share_type",
        "payment_state",
        ("payment_date", "repayment_date"),
        ("duration", "date_due"),
        "quantity",
        ("value", "value_total", "is_interest_credit", "is_pension_fund", "is_business"),
        "attached_to_contract",
        "attached_to_building",
        "note",
        ("interest", "interest_mode", "manual_interest"),
        ("identifier", "identifier_external"),
        "comment",
        "import_id",
        ("ts_created", "ts_modified"),
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "value_total",
        "interest",
        "import_id",
        "active",
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
    list_display = [
        "name",
        "share_type",
        "payment_state",
        "payment_date",
        "repayment_date",
        "duration",
        "date_due",
        "quantity",
        "value",
        "interest",
        "manual_interest",
        "is_interest_credit",
        "is_pension_fund",
    ]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
        "share_type",
        "interest_mode",
        # TODO: allow filtering for "beendet" status regardless of whether it is a state option
        ShareStateFilter,
        "is_interest_credit",
        "is_pension_fund",
        "is_business",
        "payment_date",
        "repayment_date",
        "duration",
        "date_due",
        "quantity",
        "value",
    ]
    search_fields = [
        "name__organization",
        "name__name",
        "name__first_name",
        "share_type__name",
        "value",
        "comment",
        "note",
        "identifier",
    ]
    autocomplete_fields = ["name", "share_type", "attached_to_contract", "attached_to_building"]
    actions = GenoBaseAdmin.actions + [
        share_mark_paid,
        share_mark_billed,
        share_set_duration5,
        share_set_duration10,
        share_delete_duration,
        share_set_end_endofyear,
        share_set_end_endofyear2,
        share_set_interest_mode_standard,
        share_send_membermail,
    ]
    actions_list = [
        "export_shares",
        "export_shares_endofyear",
    ]

    @action(
        description=_("Export"),
        permissions=["geno.canview_share"],
        icon="download",
        # variant=ActionVariant.PRIMARY,
    )
    def export_shares(self, request):
        return redirect(reverse("geno:share-export") + "?aggregate=yes")

    @action(
        description=_("Export per Ende Vorjahr"),
        permissions=["geno.canview_share"],
        icon="clock_arrow_down",
        # variant=ActionVariant.PRIMARY,
    )
    def export_shares_endofyear(self, request):
        return redirect(reverse("geno:share-export") + "?aggregate=yes&jahresende=yes")


@admin.register(DocumentType)
class DocumentTypeAdmin(GenoBaseAdmin):
    model = DocumentType
    fields = [
        "name",
        "description",
        "templates",
        "active",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "active"]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
    ]
    search_fields = [
        "name",
        "description",
        "templates__name",
    ]
    filter_horizontal = ["templates"]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        invalid = obj.templates.exclude(template_type="OpenDocument")
        if invalid.exists():
            names = ", ".join(invalid.values_list("name", flat=True))
            obj.templates.remove(*invalid)
            self.message_user(
                request,
                f"Folgende Vorlagen sind kein OpenDocument-Typ und wurden entfernt: {names}",
                level=messages.WARNING,
            )


@admin.register(Document)
class DocumentAdmin(GenoBaseAdmin):
    model = Document
    fields = [
        "name",
        "doctype",
        "data",
        "content_type",
        "comment",
        ("ts_created", "ts_modified"),
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "content_type",
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
    list_display = ["name", "doctype", "content_type", "ts_created", "ts_modified"]
    search_fields = ["name", "comment"]
    list_filter = ["doctype", "ts_created", "ts_modified", "content_type"]
    autocomplete_fields = ["doctype"]


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = "__all__"

    def clean_iban(self):
        value = self.cleaned_data.get("iban")
        if not value:
            return value
        if not iban_util.is_valid(value):
            raise forms.ValidationError("Invalid IBAN format.")
        return value


@admin.register(BankAccount)
class BankAccountAdmin(GenoBaseAdmin):
    model = BankAccount
    form = BankAccountForm
    fields = [
        "iban",
        "financial_institution",
        "account_holders",
        "comment",
        ("ts_created", "ts_modified"),
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
    list_display = [
        "iban_display",
        "financial_institution",
        "account_holders",
        "ts_created",
        "ts_modified",
    ]
    search_fields = ["iban", "financial_institution"]
    list_filter = ["ts_created", "ts_modified"]

    @admin.display(description="IBAN")
    def iban_display(self, obj):
        if obj.iban:
            return obj.iban
        elif obj.comment:
            return f"(leer) [{obj.comment}]"
        else:
            return "(leer)"


@admin.register(Registration)
class RegistrationAdmin(GenoBaseAdmin):
    model = Registration
    fields = [
        "name",
        "first_name",
        "email",
        "slot",
        "notes",
        ("check1", "check2", "check3", "check4", "check5"),
        "text1",
        "text2",
        "text3",
        "text4",
        "text5",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = [
        "name",
        "first_name",
        "email",
        "telephone",
        "slot",
        "ts_created",
        "ts_modified",
    ]
    ordering = ("-slot__name", "-ts_modified")
    search_fields = ["name", "first_name", "email", "slot__event__name"]
    list_filter = [
        ("slot__event__active", BooleanFieldDefaultTrueListFilter),
        "check1",
        "check2",
        "check3",
        "check4",
        "check5",
        "slot__event",
        "slot",
    ]
    autocomplete_fields = ["slot"]


@admin.register(RegistrationSlot)
class RegistrationSlotAdmin(GenoBaseAdmin):
    model = RegistrationSlot
    fields = [
        "event",
        "name",
        "alt_text",
        "max_places",
        "is_backup_for",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "event", "alt_text", "max_places", "is_backup_for"]
    ordering = ("-name",)
    search_fields = ["alt_text", "event__name", "comment"]
    list_filter = ["event", "max_places"]
    autocomplete_fields = ["event", "is_backup_for"]


class RegistrationSlotInline(TabularInline):
    model = RegistrationSlot
    fields = ["name", "alt_text", "max_places", "is_backup_for", "comment"]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "is_backup_for":
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(event__exact=request._obj_)
            else:
                field.queryset = field.queryset.none()
        return field


@admin.register(RegistrationEvent)
class RegistrationEventAdmin(GenoBaseAdmin):
    model = RegistrationEvent
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "confirmation_mail_sender",
                    "confirmation_mail_text",
                    ("publication_type", "active"),
                    ("publication_start", "publication_end"),
                    "show_counter",
                )
            },
        ),
        (
            "Anmeldeformular",
            {
                "fields": (
                    ("enable_notes", "enable_telephone"),
                    "check1_label",
                    "check2_label",
                    "check3_label",
                    "check4_label",
                    "check5_label",
                    "text1_label",
                    "text2_label",
                    "text3_label",
                    "text4_label",
                    "text5_label",
                ),
                "classes": ["tab"],
            },
        ),
        (
            "Zusatzinfos",
            {
                "fields": ("registration_link", "comment", "ts_created", "ts_modified"),
                "classes": ["tab"],
            },
        ),
        ("Verknüpfungen", {"fields": ("links", "backlinks"), "classes": ["tab"]}),
    )
    readonly_fields = ["registration_link", "ts_created", "ts_modified", "links", "backlinks"]
    list_display = [
        "name",
        "registration_link",
        "confirmation_mail_sender",
        "active",
        "ts_created",
    ]
    ordering = ("-active", "-ts_created")
    list_editable = ["active"]
    search_fields = ["name", "description", "confirmation_mail_sender", "comment"]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
        "confirmation_mail_sender",
        "publication_type",
        "publication_start",
        "publication_end",
        "ts_created",
    ]

    inlines = [RegistrationSlotInline]

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)


@admin.decorators.register(RentalUnit)
class RentalUnitAdmin(GenoBaseAdmin):
    fields = [
        "name",
        ("label", "label_short"),
        ("rental_type", "rooms", "min_occupancy"),
        ("building", "floor"),
        ("area", "area_balcony", "area_add"),
        ("height", "volume"),
        "billing_period",
        ("rent_netto", "nk", "nk_flat", "nk_electricity"),
        ("rent_netto_per_month", "nk_per_month", "nk_flat_per_month", "nk_electricity_per_month"),
        ("rent_total", "rent_total_per_month"),
        ("share", "depot"),
        ("internal_nr", "ewid"),
        "note",
        "svg_polygon",
        "description",
        "status",
        "adit_serial",
        "active",
        "comment",
        "import_id",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "rent_total",
        "rent_total_per_month",
        "rent_netto_per_month",
        "nk_per_month",
        "nk_flat_per_month",
        "nk_electricity_per_month",
        "import_id",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    list_display = [
        "name",
        "label",
        "rental_type",
        "building",
        "rooms",
        "floor",
        "area",
        "area_add",
        "rent_netto",
        "nk",
        "nk_flat",
        "share",
        "status",
        "comment",
    ]
    search_fields = [
        "name",
        "label",
        "description",
        "building__name",
        "rental_type",
        "note",
        "comment",
        "rentalunit_contracts__contractors__name",
        "rentalunit_contracts__contractors__organization",
        "rentalunit_contracts__contractors__first_name",
    ]
    list_filter = [
        "rental_type",
        "rooms",
        "building__name",
        "floor",
        "status",
        "billing_period",
        ("active", BooleanFieldDefaultTrueListFilter),
    ]
    autocomplete_fields = ["building"]


@admin.display(description='Als "angeboten" markieren')
def contract_mark_offered(modeladmin, request, queryset):
    queryset.update(state="angeboten")


@admin.display(description='Als "unterzeichnet" markieren')
def contract_mark_signed(modeladmin, request, queryset):
    queryset.update(state="unterzeichnet")


@admin.display(description='Als "geküdigt" markieren')
def contract_mark_canceled(modeladmin, request, queryset):
    queryset.update(state="gekuendigt")


@admin.display(description='Als "ungültig" markieren')
def contract_mark_invalid(modeladmin, request, queryset):
    queryset.update(state="ungueltig")


@admin.display(description="Vertragsbeginn auf 1. des letzten Monats setzten")
def contract_set_startdate_lastmonth(modeladmin, request, queryset):
    new_date = datetime.date.today().replace(day=1) - relativedelta(months=1)
    queryset.update(date=new_date)


@admin.display(description="Vertragsbeginn auf 1. dieses Monats setzten")
def contract_set_startdate_thismonth(modeladmin, request, queryset):
    new_date = datetime.date.today().replace(day=1)
    queryset.update(date=new_date)


@admin.display(description="Vertragsbeginn auf 1. des nächsten Monats setzten")
def contract_set_startdate_nextmonth(modeladmin, request, queryset):
    new_date = datetime.date.today().replace(day=1) + relativedelta(months=1)
    queryset.update(date=new_date)


@admin.display(description="Start Sollstellung auf 1. des letzten Monats setzten")
def contract_set_billingstart_lastmonth(modeladmin, request, queryset):
    new_date = datetime.date.today().replace(day=1) - relativedelta(months=1)
    queryset.update(billing_date_start=new_date)


@admin.display(description="Start Sollstellung auf 1. dieses Monats setzten")
def contract_set_billingstart_thismonth(modeladmin, request, queryset):
    new_date = datetime.date.today().replace(day=1)
    queryset.update(billing_date_start=new_date)


@admin.display(description="Start Sollstellung auf 1. des nächsten Monats setzten")
def contract_set_billingstart_nextmonth(modeladmin, request, queryset):
    new_date = datetime.date.today().replace(day=1) + relativedelta(months=1)
    queryset.update(billing_date_start=new_date)


@admin.display(description="Vertragsende auf Ende des letzten Monats setzten")
def contract_set_enddate_lastmonth(modeladmin, request, queryset):
    new_date = datetime.date.today() - relativedelta(months=1) + relativedelta(day=31)
    queryset.update(date_end=new_date)


@admin.display(description="Vertragsende auf Ende dieses Monats setzten")
def contract_set_enddate_thismonth(modeladmin, request, queryset):
    new_date = datetime.date.today() + relativedelta(day=31)
    queryset.update(date_end=new_date)


@admin.display(description="Vertragsende auf Ende des nächsten Monats setzten")
def contract_set_enddate_nextmonth(modeladmin, request, queryset):
    new_date = datetime.date.today() + relativedelta(months=1) + relativedelta(day=31)
    queryset.update(date_end=new_date)


@admin.display(description="Ende Sollstellung auf Ende des letzten Monats setzten")
def contract_set_billingend_lastmonth(modeladmin, request, queryset):
    new_date = datetime.date.today() - relativedelta(months=1) + relativedelta(day=31)
    queryset.update(billing_date_end=new_date)


@admin.display(description="Ende Sollstellung auf Ende dieses Monats setzten")
def contract_set_billingend_thismonth(modeladmin, request, queryset):
    new_date = datetime.date.today() + relativedelta(day=31)
    queryset.update(billing_date_end=new_date)


@admin.display(description="Ende Sollstellung auf Ende des nächsten Monats setzten")
def contract_set_billingend_nextmonth(modeladmin, request, queryset):
    new_date = datetime.date.today() + relativedelta(months=1) + relativedelta(day=31)
    queryset.update(billing_date_end=new_date)


class ContractAdminModelForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = "__all__"

    def clean_main_contact(self):
        main_contact = self.cleaned_data.get("main_contact")
        contractors = self.cleaned_data.get("contractors")
        if main_contact and main_contact not in contractors.all():
            raise forms.ValidationError(
                "Kontaktperson/Hauptmieter*in muss Vertragspartner*in sein."
            )
        return main_contact

    def clean_rental_units(self):
        # only rental units of same building are allowed
        rental_units = self.cleaned_data.get("rental_units")
        buildings = set()
        for ru in rental_units.all():
            buildings.add(ru.building)
        if len(buildings) > 1:
            raise forms.ValidationError(
                "Es dürfen nur Mietobjekte aus derselben Liegenschaft gewählt werden."
            )
        return rental_units


class VertragstypFilter(admin.SimpleListFilter):
    title = "Vertragstyp"
    parameter_name = "main_contract"

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            ("hv", "Hauptvertrag"),
            ("uv", "Untervertrag"),
        )

    def queryset(self, request, queryset):
        # apply the filter to the queryset
        if self.value() == "hv":
            return queryset.filter(main_contract=None)
        if self.value() == "uv":
            return queryset.filter(main_contract__isnull=False)


@admin.register(Contract)
class ContractAdmin(GenoBaseAdmin):
    form = ContractAdminModelForm
    fields = [
        "main_contract",
        "contractors",
        "main_contact",
        "rental_units",
        "children",
        "payment_state",
        ("date", "date_end", "date_since"),
        ("billing_date_start", "billing_date_end"),
        ("rent_reduction", "rent_reservation"),
        "share_reduction",
        "send_qrbill",
        "billing_contract",
        "bankaccount",
        "note",
        "comment",
        ("ts_created", "ts_modified"),
        "import_id",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "active",
        "import_id",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    list_display = ["label_with_badge", "state", "date", "date_end", "note", "comment"]
    search_fields = [
        "contractors__name",
        "contractors__first_name",
        "contractors__organization",
        "children__name__name",
        "children__name__first_name",
        "rental_units__building__name",
        "rental_units__name",
        "note",
        "comment",
    ]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
        VertragstypFilter,
        "state",
        "rental_units__building",
        "rental_units__rental_type",
        "date",
        "date_end",
        "billing_date_start",
        "billing_date_end",
        "send_qrbill",
    ]
    autocomplete_fields = [
        "contractors",
        "main_contact",
        "rental_units",
        "children",
        "billing_contract",
    ]
    actions = GenoBaseAdmin.actions + [
        contract_mark_signed,
        contract_mark_offered,
        contract_mark_canceled,
        contract_mark_invalid,
        contract_set_billingstart_nextmonth,
        contract_set_billingstart_thismonth,
        contract_set_billingstart_lastmonth,
        contract_set_startdate_nextmonth,
        contract_set_startdate_thismonth,
        contract_set_startdate_lastmonth,
        contract_set_billingend_nextmonth,
        contract_set_billingend_thismonth,
        contract_set_billingend_lastmonth,
        contract_set_enddate_nextmonth,
        contract_set_enddate_thismonth,
        contract_set_enddate_lastmonth,
    ]
    filter_horizontal = ["contractors", "children", "rental_units"]
    actions_list = [
        "contract_report",
    ]
    actions_detail = []

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        response = super().changeform_view(request, object_id, form_url, extra_context)

        if object_id and hasattr(response, "context_data"):
            try:
                contract = self.model.objects.get(pk=object_id)
            except self.model.DoesNotExist:
                return response

            dropdown_items = []

            if request.user.has_perm("geno.add_contract"):
                dropdown_items.append(
                    {
                        "title": str(_("Untervertrag hinzufügen")),
                        "path": reverse("admin:geno_contract_add") + f"?main_contract={object_id}",
                        "icon": "splitscreen_add",
                        "attrs": {},
                    }
                )

            for action_tuple in contract.get_object_actions():
                dropdown_items.append(
                    {
                        "title": action_tuple[1],
                        "path": action_tuple[0],
                        "icon": "file_save",
                        "attrs": {},
                    }
                )

            if dropdown_items:
                response.context_data["actions_detail"] = [
                    {
                        "title": str(_("Aktionen")),
                        "path": None,
                        "icon": None,
                        "variant": ActionVariant.PRIMARY,
                        "method_name": "contract_actions",
                        "items": dropdown_items,
                    }
                ]

        return response

    @display(
        description="Vertrag",
    )
    def label_with_badge(self, contract):
        uv_str = ""
        if contract.main_contract:
            uv_str = "Untervertrag"
        return format_html("{}", contract.__str__()) + (
            format_html(
                '<span class="leading-[18px] ml-2 p-1 relative rounded-xs text-center text-[11px] whitespace-nowrap uppercase min-w-[18px] bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-400">{}</span>',
                uv_str,
            )
            if uv_str
            else ""
        )

    @action(
        description=_("Report Pflichtanteile/Belegung"),
        permissions=["geno.rental_contracts", "geno.canview_share"],
        icon="download",
        # variant=ActionVariant.PRIMARY,
    )
    def contract_report(self, request):
        return redirect(reverse("geno:contract-report"))


# class ResidentListAdmin(GenoBaseAdmin):
#    model = Contract
#    actions_list = [
#        "export_address_list",
#    ]
#
#    @action(
#        description=_("Export"),
#        permissions=["geno.canview_member"],
#        icon="download",
#        # variant=ActionVariant.PRIMARY,
#    )
#    def export_address_list(self, request):
#        return redirect(reverse("geno:address_export"))
#
#    # def get_urls(self):
#    #    print("get urls")
#    #    view = self.admin_site.admin_view(ResidentListView.as_view(model_admin=self))
#    #    return super().get_urls() + [path("resident-list", view, name="resident-list")]


@admin.display(description='Als "NICHT konsolidiert" markieren')
def invoice_revert_consolidation(modeladmin, request, queryset):
    queryset.update(consolidated=False)


@admin.register(InvoiceCategory)
class InvoiceCategoryAdmin(GenoBaseAdmin):
    model = InvoiceCategory
    fields = [
        "name",
        "reference_id",
        "linked_object_type",
        "email_template",
        ("income_account", "income_account_building_based"),
        "building_based_cost_center",
        ("receivables_account", "receivables_account_building_based"),
        "note",
        "manual_allowed",
        "active",
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = [
        "name",
        "reference_id",
        "linked_object_type",
        "income_account",
        "receivables_account",
        "manual_allowed",
        "active",
    ]
    search_fields = [
        "name",
        "income_account",
        "receivables_account",
        "note",
        "reference_id",
        "comment",
    ]

    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
        "manual_allowed",
        "linked_object_type",
    ]
    autocomplete_fields = ["email_template"]


class InvoiceAdminModelForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = "__all__"

    def clean(self):
        person = self.cleaned_data.get("person")
        contract = self.cleaned_data.get("contract")
        if person and contract:
            raise forms.ValidationError(
                "Bitte entweder Person oder Vertrag angeben. Beides gleichzeitig ist nicht möglich."
            )
        if not person and not contract:
            raise forms.ValidationError(
                "Es muss eine Person oder einen Vertrag ausgewählt werden."
            )
        return self.cleaned_data


@admin.register(Invoice)
class InvoiceAdmin(GenoBaseAdmin):
    model = Invoice
    form = InvoiceAdminModelForm
    fields = [
        "name",
        "invoice_category",
        "invoice_type",
        "person",
        ("date", "amount", "consolidated"),
        ("contract", "year", "month"),
        "is_additional_invoice",
        "active",
        ("transaction_id", "reference_nr"),
        "additional_info",
        ("fin_transaction_ref", "fin_account", "fin_account_receivables"),
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "consolidated",
        "transaction_id",
        "reference_nr",
        "additional_info",
        "fin_transaction_ref",
        "fin_account",
        "fin_account_receivables",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    list_display = [
        "name",
        "invoice_category",
        "invoice_type",
        "person_or_contract",
        "year",
        "month",
        "date",
        "amount",
    ]
    search_fields = [
        "name",
        "person__first_name",
        "person__name",
        "person__organization",
        "comment",
        "contract__contractors__name",
        "contract__contractors__first_name",
        "contract__contractors__organization",
        "contract__rental_units__name",
    ]
    list_filter = [
        "invoice_type",
        "invoice_category",
        "consolidated",
        "year",
        "month",
        "is_additional_invoice",
    ]
    autocomplete_fields = ["invoice_category", "person", "contract"]
    actions = GenoBaseAdmin.actions + [invoice_revert_consolidation]

    @admin.display(description="Person/Vertrag")
    def person_or_contract(self, obj):
        if obj.contract:
            return str(obj.contract)
        else:
            return str(obj.person)


@admin.register(TenantsView)
class TenantsViewAdmin(GenoBaseAdmin):
    fields = [
        "bu_name",
        "ru_name",
        "ru_label",
        "ru_type",
        "ru_floor",
        "ru_rooms",
        "ru_area",
        "organization",
        "ad_name",
        "ad_first_name",
        "ad_title",
        "ad_email",
        "active",
        "c_issubcontract",
        "c_ischild",
        "c_age",
        "presence",
        "ad_date_birth",
        "ad_city",
        "ad_street",
        "ad_tel1",
        "ad_tel2",
        "p_hometown",
        "p_occupation",
        "p_membership_date",
    ]

    readonly_fields = [
        "bu_name",
        "ru_name",
        "ru_label",
        "ru_type",
        "ru_floor",
        "ru_rooms",
        "ru_area",
        "organization",
        "ad_name",
        "ad_first_name",
        "ad_title",
        "ad_email",
        "active",
        "c_issubcontract",
        "c_ischild",
        "c_age",
        "presence",
        "ad_date_birth",
        "ad_city",
        "ad_street",
        "ad_tel1",
        "ad_tel2",
        "p_hometown",
        "p_occupation",
        "p_membership_date",
    ]

    list_display = [
        "bu_name",
        "ru_name",
        "ru_label",
        "ru_type",
        "ru_floor",
        "ru_rooms",
        "ru_area",
        "organization",
        "ad_name",
        "ad_first_name",
        "ad_title",
        "ad_email",
        "active",
        "c_issubcontract",
        "c_ischild",
        "c_age",
        "presence",
        "ad_date_birth",
        "ad_city",
        "ad_street",
        "ad_tel1",
        "ad_tel2",
        "p_hometown",
        "p_occupation",
        "p_membership_date",
    ]

    my_search_fields = [
        "bu_name",
        "ru_name",
        "ru_label",
        "ru_type",
        "ru_floor",
        "ru_rooms",
        "ru_area",
        "organization",
        "ad_name",
        "ad_first_name",
        "ad_title",
        "ad_email",
        "c_age",
        "presence",
        "ad_date_birth",
        "ad_city",
        "ad_street",
        "ad_tel1",
        "ad_tel2",
        "p_hometown",
        "p_occupation",
        "p_membership_date",
    ]
    list_filter = [
        "bu_name",
        "ru_type",
        "ru_floor",
        "active",
        "c_ischild",
        "c_issubcontract",
    ]
    search_fields = my_search_fields
    list_display_links = None
    actions = ["export_as_xls"]

    actions_list = [
        "download_resident_list_units",
    ]

    @action(
        description=_("Mietobjektspiegel"),
        permissions=["geno.rental_objects"],
        icon="download",
    )
    def download_resident_list_units(self, request):
        return redirect(reverse("geno:resident-list-units"))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    ordering = ("-bu_name", "-ru_name")


@admin.register(LookupTable)
class LookupTableAdmin(GenoBaseAdmin):
    model = LookupTable
    fields = ["name", "lookup_type", "value", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "lookup_type", "value", "ts_modified"]
    search_fields = ["name", "value"]
    list_filter = ["lookup_type"]


@admin.register(ContentTemplate)
class ContentTemplateAdmin(GenoBaseAdmin):
    model = ContentTemplate
    fields = [
        "name",
        "template_type",
        "text",
        "file",
        "template_context",
        "manual_creation_allowed",
        "active",
        ("ts_created", "ts_modified"),
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "template_type", "active", "ts_created", "ts_modified"]
    search_fields = ["name", "text"]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
        "template_type",
        "manual_creation_allowed",
        "template_context",
        "ts_created",
        "ts_modified",
    ]
    autocomplete_fields = ["template_context"]
    filter_horizontal = ["template_context"]

    class Media:
        js = ("geno/js/content_template_admin.js",)


@admin.register(ContentTemplateOption)
class ContentTemplateOptionAdmin(GenoBaseAdmin):
    model = ContentTemplateOption
    fields = ["name", "value", "comment", "ts_created", "ts_modified"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "value", "comment", "ts_created", "ts_modified"]
    search_fields = ["name", "value", "comment"]
    list_filter = ["name", "ts_created", "ts_modified"]
    autocomplete_fields = ["name"]


@admin.register(ContentTemplateOptionType)
class ContentTemplateOptionTypeAdmin(GenoBaseAdmin):
    model = ContentTemplateOption
    fields = ["name", "description", "comment", "ts_created", "ts_modified"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "comment", "ts_created", "ts_modified"]
    search_fields = ["name", "description", "comment"]
    list_filter = ["ts_created", "ts_modified"]


@admin.register(GenericAttribute)
class GenericAttributeAdmin(GenoBaseAdmin):
    model = GenericAttribute
    fields = [
        "name",
        "value",
        "date",
        ("content_type", "object_id"),
        "comment",
        ("ts_created", "ts_modified"),
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "value", "date", "content_type", "ts_created", "ts_modified"]
    search_fields = ["name", "comment", "value"]
    list_filter = ["name", "ts_created", "ts_modified", "content_type"]


## Unregister default admin classes and re-register with unfold classes to provide the correct
## styling.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
