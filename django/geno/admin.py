import datetime

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from stdnum import iban as iban_util
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action
from unfold.enums import ActionVariant

import geno.settings as geno_settings
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

copy_objects.short_description = "Ausgewählte Objekte kopieren"

class BooleanFieldDefaultTrueListFilter(admin.BooleanFieldListFilter):
    """
    Filter a boolean field `active`.
    Default: only True (active) records.
    When ‘All’ is chosen the URL will contain ?active=all (never removed).
    """
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        # Determine the parameter name used in the URL.
        # Support `field_path` (e.g. parent__active), the field name,
        # and common variants with '.' vs '__' (e.g. parent.active).
        candidates = []
        if field_path:
            candidates.append(field_path)
        try:
            candidates.append(self.field.name)
        except Exception:
            pass

        # Add common variants
        variants = set(candidates)
        for c in list(candidates):
            variants.add(c.replace(".", "__"))
            variants.add(c.replace("__", "."))
        candidates = list(variants)

        lookup_param = None
        for c in candidates:
            if c in self.used_parameters:
                lookup_param = c
                break

        # Fallback to field_path or field name
        if lookup_param is None:
            lookup_param = field_path or getattr(self.field, "name", "")

        self.field.name = lookup_param

        try:
            val = self.used_parameters.get(self.field.name)
            if val == "all":
                self.lookup_val = "all"
            elif val == "0":
                self.lookup_val = "0"
            else:
                self.lookup_val = "1"
        except Exception:
            self.lookup_val = "1"

    def choices(self, changelist):
        yield from [
            {
                "selected": self.lookup_val == "all",
                "query_string": changelist.get_query_string(
                    {self.field.name: "all"}, remove=[self.field.name]
                ),
                "display": "Alle",
            },
            {
                "selected": self.lookup_val == "1",
                "query_string": changelist.get_query_string(
                    {self.field.name: "1"}, remove=[self.field.name]
                ),
                "display": "Aktive",
            },
            {
                "selected": self.lookup_val == "0",
                "query_string": changelist.get_query_string(
                    {self.field.name: "0"}, remove=[self.field.name]
                ),
                "display": "Inaktive",
            },
        ]

    def queryset(self, request, queryset):
        # Normalize lookup to Django filter lookup syntax (use `__` separators).
        lookup = (self.field.name or getattr(self.field, "name", "")).replace(".", "__")
        if self.lookup_val == "1":
            return queryset.filter(**{lookup: True})
        elif self.lookup_val == "0":
            return queryset.filter(**{lookup: False})
        else:
            return queryset

    def expected_parameters(self):
        return [self.field.name]


## Base admin class
class GenoBaseAdmin(ModelAdmin, ExportXlsMixin):
    model = None
    view_on_site = False
    save_as = True
    save_on_top = True
    actions = ["export_as_xls", copy_objects]

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        ## Load custom admin config
        module_name = self.__module__
        if (
            hasattr(settings, "COHIVA_ADMIN_FIELDS")
            and module_name in settings.COHIVA_ADMIN_FIELDS
        ):
            class_name = type(self).__name__
            for attr in ("fields", "readonly_fields", "list_display", "list_filter"):
                setting_name = f"{class_name}.{attr}"
                if setting_name in settings.COHIVA_ADMIN_FIELDS[module_name]:
                    setattr(self, attr, settings.COHIVA_ADMIN_FIELDS[module_name][setting_name])

@admin.display(description="Anrede auf 'Herr' setzen")
def set_title_mr(modeladmin, request, queryset):
    queryset.update(title="Herr")


@admin.display(description="Anrede auf 'Frau' setzen")
def set_title_mrs(modeladmin, request, queryset):
    queryset.update(title="Frau")


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
        ("bankaccount", "interest_action"),
        "paymentslip",
        "ignore_in_lists",
        "login_permission",
        "active",
        "comment",
        ("carddav_href", "carddav_etag", "carddav_syncts"),
        ("ts_created", "ts_modified"),
        ("gnucash_id", "import_id", "random_id"),
        "user",
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "ts_created",
        "ts_modified",
        "import_id",
        "gnucash_id",
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
        "country",
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
    readonly_fields = ["ts_created", "ts_modified", "object_actions", "links", "backlinks"]
    list_display = ["name", "date_join", "date_leave"]
    list_filter = [
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
        "ts_created",
        "ts_modified",
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
        "team",
        "active",
        "ts_created",
        "ts_modified",
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
    list_filter = ["building__name", ("active", BooleanFieldDefaultTrueListFilter)]
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
        "ts_created",
        "ts_modified",
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
    queryset.update(date_end=datetime.date(datetime.datetime.now().year - 1, 12, 31))


@admin.display(description=("Datum Ende auf 31.12. vor ZWEI Jahren (=Jahresende) setzen"))
def share_set_end_endofyear2(modeladmin, request, queryset):
    queryset.update(date_end=datetime.date(datetime.datetime.now().year - 2, 12, 31))


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
        "state",
        ("date", "date_end"),
        ("duration", "date_due"),
        "quantity",
        ("value", "value_total", "is_interest_credit", "is_pension_fund", "is_business"),
        "attached_to_contract",
        "attached_to_building",
        "note",
        ("interest", "interest_mode", "manual_interest"),
        "comment",
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "value_total",
        "interest",
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
    list_display = [
        "name",
        "share_type",
        "state",
        "date",
        "date_end",
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
        "share_type",
        "interest_mode",
        "state",
        "is_interest_credit",
        "is_pension_fund",
        "is_business",
        "date",
        "date_end",
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
        "template",
        "template_file",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "template", "template_file", "active"]
    list_filter = [
        ("active", BooleanFieldDefaultTrueListFilter),
    ]
    search_fields = [
        "name",
        "description",
        "template__name",
        "template__description",
        "template_file",
    ]
    autocomplete_fields = ["template"]


@admin.register(Document)
class DocumentAdmin(GenoBaseAdmin):
    model = Document
    fields = [
        "name",
        "doctype",
        "data",
        "content_type",
        "comment",
        "ts_created",
        "ts_modified",
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
        "ts_created",
        "ts_modified",
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
        "ts_created",
        "ts_modified",
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
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "event", "alt_text", "max_places", "is_backup_for"]
    ordering = ("-name",)
    search_fields = ["alt_text", "event__name", "comment"]
    list_filter = ["event", "max_places"]
    autocomplete_fields = ["event", "is_backup_for"]


class RegistrationSlotInline(admin.TabularInline):
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
    fields = [
        "name",
        "description",
        "confirmation_mail_sender",
        "confirmation_mail_text",
        ("publication_type", "active"),
        ("publication_start", "publication_end"),
        "show_counter",
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
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "confirmation_mail_sender", "active", "ts_created"]
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
        ("rent_netto", "nk", "nk_flat", "nk_electricity", "rent_total"),
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
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks", "rent_total"]
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
    list_filter = ["rental_type", "rooms", "building__name", "floor", "status", ("active", BooleanFieldDefaultTrueListFilter)]
    autocomplete_fields = ["building"]

@admin.display(description='Als "unterzeichnet" markieren')
def contract_mark_signed(modeladmin, request, queryset):
    queryset.update(state="unterzeichnet")


@admin.display(description='Als "angeboten" markieren')
def contract_mark_offered(modeladmin, request, queryset):
    queryset.update(state="angeboten")


@admin.display(description=("Mietbeginn auf 1. des nächsten Monats setzten"))
def contract_set_startdate_nextmonth(modeladmin, request, queryset):
    new_date = (datetime.date.today().replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    queryset.update(date=new_date)


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


class VertragstypFilter(admin.SimpleListFilter):
    title = "Vertragstyp"
    parameter_name = "main_contract"

    def lookups(self, request, model_admin):
        # define the filter options
        return (
            ("hv", "Hauptvertrag"),
            ("zv", "Zusatzvertrag"),
        )

    def queryset(self, request, queryset):
        # apply the filter to the queryset
        if self.value() == "hv":
            return queryset.filter(main_contract=None)
        if self.value() == "zv":
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
        "children_old",
        "state",
        "date",
        "date_end",
        "rent_reduction",
        "share_reduction",
        "send_qrbill",
        "billing_contract",
        "bankaccount",
        "note",
        "comment",
        "ts_created",
        "ts_modified",
        "import_id",
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "object_actions", "links", "backlinks"]
    list_display = ["__str__", "state", "date", "date_end", "note", "comment"]
    search_fields = [
        "contractors__name",
        "contractors__first_name",
        "contractors__organization",
        "children__name__name",
        "children__name__first_name",
        "rental_units__name",
        "note",
        "comment",
    ]
    list_filter = [
        VertragstypFilter,
        "state",
        "rental_units__rental_type",
        "rental_units__floor",
        "rental_units__rooms",
        "date",
        "date_end",
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
        contract_set_startdate_nextmonth,
    ]
    filter_horizontal = ["contractors", "children", "rental_units"]
    actions_list = [
        "contract_report",
    ]
    actions_detail = [
        "add_subcontract",
    ]

    @action(
        description=_("Report Pflichtanteile/Belegung"),
        permissions=["geno.rental_contracts", "geno.canview_share"],
        icon="download",
        # variant=ActionVariant.PRIMARY,
    )
    def contract_report(self, request):
        return redirect(reverse("geno:contract-report"))

    @action(
        description=_("Untervertrag hinzufügen"),
        icon="splitscreen_add",
        url_path="add-subcontract",
        permissions=["geno.add_contract"],
        variant=ActionVariant.PRIMARY,
    )
    def add_subcontract(self, request, object_id):
        return HttpResponseRedirect(
            reverse("admin:geno_contract_add") + f"?main_contract={object_id}"
        )


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
        "income_account",
        "receivables_account",
        "note",
        "manual_allowed",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
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

    list_filter = [("active", BooleanFieldDefaultTrueListFilter), "manual_allowed", "linked_object_type"]
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
        ("gnc_transaction", "gnc_account", "gnc_account_receivables"),
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "consolidated",
        "transaction_id",
        "reference_nr",
        "additional_info",
        "gnc_transaction",
        "gnc_account",
        "gnc_account_receivables",
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
        description=_("Mietobjektespiegel"),
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
        "ts_created",
        "ts_modified",
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
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "value", "date", "content_type", "ts_created", "ts_modified"]
    search_fields = ["name", "comment", "value"]
    list_filter = ["name", "ts_created", "ts_modified", "content_type"]
