import datetime

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect

import geno.settings as geno_settings
from geno.exporter import ExportXlsMixin
from geno.models import (
    Address,
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
)


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


## Base admin class
class GenoBaseAdmin(admin.ModelAdmin, ExportXlsMixin):
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


def set_title_mr(modeladmin, request, queryset):
    queryset.update(title="Herr")


set_title_mr.short_description = "Anrede auf 'Herr' setzen"


def set_title_mrs(modeladmin, request, queryset):
    queryset.update(title="Frau")


set_title_mrs.short_description = "Anrede auf 'Frau' setzen"


class AddressAdmin(GenoBaseAdmin):
    model = Address
    fields = [
        "organization",
        ("name", "first_name"),
        ("title", "formal"),
        "extra",
        ("street_name", "house_number", "po_box", "po_box_number"),
        ("city_zipcode", "city_name", "country"),
        ("telephone", "mobile"),
        ("email", "email2"),
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
        ("gnucash_id", "emonitor_id", "random_id"),
        "user",
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = [
        "ts_created",
        "ts_modified",
        "emonitor_id",
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
        "active",
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
    my_search_fields = [
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
        "bankaccount",
        "comment",
    ]
    search_fields = my_search_fields
    actions = GenoBaseAdmin.actions + [set_title_mr, set_title_mrs]


admin.site.register(Address, AddressAdmin)


def mark_flag_01(modeladmin, request, queryset):
    queryset.update(flag_01=True)


mark_flag_01.short_description = "Als '%s' markieren" % geno_settings.MEMBER_FLAGS[1]


def unmark_flag_01(modeladmin, request, queryset):
    queryset.update(flag_01=False)


unmark_flag_01.short_description = "Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[1]


def mark_flag_02(modeladmin, request, queryset):
    queryset.update(flag_02=True)


mark_flag_02.short_description = "Als '%s' markieren" % geno_settings.MEMBER_FLAGS[2]


def unmark_flag_02(modeladmin, request, queryset):
    queryset.update(flag_02=False)


unmark_flag_02.short_description = "Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[2]


def mark_flag_03(modeladmin, request, queryset):
    queryset.update(flag_03=True)


mark_flag_03.short_description = "Als '%s' markieren" % geno_settings.MEMBER_FLAGS[3]


def unmark_flag_03(modeladmin, request, queryset):
    queryset.update(flag_03=False)


unmark_flag_03.short_description = "Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[3]


def mark_flag_04(modeladmin, request, queryset):
    queryset.update(flag_04=True)


mark_flag_04.short_description = "Als '%s' markieren" % geno_settings.MEMBER_FLAGS[4]


def unmark_flag_04(modeladmin, request, queryset):
    queryset.update(flag_04=False)


unmark_flag_04.short_description = "Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[4]


def mark_flag_05(modeladmin, request, queryset):
    queryset.update(flag_05=True)


mark_flag_05.short_description = "Als '%s' markieren" % geno_settings.MEMBER_FLAGS[5]


def unmark_flag_05(modeladmin, request, queryset):
    queryset.update(flag_05=False)


unmark_flag_05.short_description = "Markierung '%s' entfernen" % geno_settings.MEMBER_FLAGS[5]


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


member_send_membermail.short_description = "Email Versand an ausgewählte Mitglieder"


class MemberAdmin(GenoBaseAdmin):
    model = Member
    fields = [
        "name",
        "date_join",
        "date_leave",
        "flag_01",
        "flag_02",
        "flag_03",
        "flag_04",
        "flag_05",
        "notes",
        "ts_created",
        "ts_modified",
        "object_actions",
        "links",
        "backlinks",
    ]
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
    my_search_fields = ["name__organization", "name__name", "name__first_name", "notes"]
    search_fields = my_search_fields
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


admin.site.register(Member, MemberAdmin)


class ChildAdmin(GenoBaseAdmin):
    model = Child
    fields = [
        "name",
        ("presence", "age"),
        "parents",
        "notes",
        "emonitor_id",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["age", "emonitor_id", "ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "presence", "parents", "age"]
    list_filter = ["presence", "name__active"]
    my_search_fields = ["name__name", "name__first_name", "parents", "notes"]
    search_fields = my_search_fields


admin.site.register(Child, ChildAdmin)


class BuildingAdmin(GenoBaseAdmin):
    model = Building
    fields = [
        "name",
        "description",
        "team",
        "active",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "active"]
    list_filter = ["active"]
    my_search_fields = ["name", "description", "team"]
    search_fields = my_search_fields


admin.site.register(Building, BuildingAdmin)


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
    list_filter = ["building__name", "active"]
    my_search_fields = ["name__name", "name__first_name", "building__name", "key_number", "notes"]
    search_fields = my_search_fields


admin.site.register(Tenant, TenantAdmin)


class MemberAttributeTypeAdmin(GenoBaseAdmin):
    model = MemberAttributeType
    fields = ["name", "description"]
    list_display = ["name", "description"]
    my_search_fields = ["name", "description"]
    search_fields = my_search_fields


admin.site.register(MemberAttributeType, MemberAttributeTypeAdmin)


def mark_paid(modeladmin, request, queryset):
    queryset.update(value="Bezahlt", date=datetime.date.today())


mark_paid.short_description = 'Attribut-Wert auf "Bezahlt" setzen'


def mark_billed(modeladmin, request, queryset):
    queryset.update(value="Rechnung geschickt", date=datetime.date.today())


mark_billed.short_description = 'Attribut-Wert auf "Rechnung geschickt" setzen'


def mark_reminder(modeladmin, request, queryset):
    queryset.update(value="Mahnung geschickt", date=datetime.date.today())


mark_reminder.short_description = 'Attribut-Wert auf "Mahnung geschickt" setzen'


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


member_attribute_send_membermail.short_description = "Email Versand an ausgewählte Mitglieder"


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
    my_search_fields = [
        "member__name__organization",
        "member__name__name",
        "member__name__first_name",
        "attribute_type__name",
        "value",
        "comment",
    ]
    search_fields = my_search_fields
    actions = GenoBaseAdmin.actions + [
        mark_billed,
        mark_paid,
        mark_reminder,
        member_attribute_send_membermail,
    ]


admin.site.register(MemberAttribute, MemberAttributeAdmin)


class ShareTypeAdmin(GenoBaseAdmin):
    model = ShareType
    fields = ["name", "description", "standard_interest"]
    list_display = ["name", "description", "standard_interest"]
    list_filter = ["standard_interest"]
    my_search_fields = ["name", "description"]
    search_fields = my_search_fields


admin.site.register(ShareType, ShareTypeAdmin)


def share_mark_paid(modeladmin, request, queryset):
    queryset.update(state="bezahlt", date=datetime.date.today())


share_mark_paid.short_description = 'Als "bezahlt" markieren'


def share_mark_billed(modeladmin, request, queryset):
    queryset.update(state="gefordert", date=datetime.date.today())


share_mark_billed.short_description = 'Als "gefordert" markieren'


def share_delete_duration(modeladmin, request, queryset):
    queryset.update(duration=None)


share_delete_duration.short_description = "Laufzeit löschen"


def share_set_duration5(modeladmin, request, queryset):
    queryset.update(duration=5)


share_set_duration5.short_description = "Laufzeit auf 5 Jahre setzen"


def share_set_duration10(modeladmin, request, queryset):
    queryset.update(duration=10)


share_set_duration10.short_description = "Laufzeit auf 10 Jahre setzen"


def share_set_end_endofyear(modeladmin, request, queryset):
    queryset.update(date_end=datetime.date(datetime.datetime.now().year - 1, 12, 31))


share_set_end_endofyear.short_description = (
    "Datum Ende auf 31.12. des Vorjahres (=Jahresende) setzen"
)


def share_set_end_endofyear2(modeladmin, request, queryset):
    queryset.update(date_end=datetime.date(datetime.datetime.now().year - 2, 12, 31))


share_set_end_endofyear2.short_description = (
    "Datum Ende auf 31.12. vor ZWEI Jahren (=Jahresende) setzen"
)


def share_set_interest_mode_standard(modeladmin, request, queryset):
    queryset.update(interest_mode="Standard")


share_set_interest_mode_standard.short_description = "Zinsatz-Modus auf «Standard» setzen."


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


share_send_membermail.short_description = "Email Versand an ausgewählte Mitglieder"


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
    my_search_fields = [
        "name__organization",
        "name__name",
        "name__first_name",
        "share_type__name",
        "value",
        "comment",
        "note",
    ]
    search_fields = my_search_fields
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


admin.site.register(Share, ShareAdmin)


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
        "active",
    ]
    my_search_fields = [
        "name",
        "description",
        "template__name",
        "template__description",
        "template_file",
    ]
    search_fields = my_search_fields


admin.site.register(DocumentType, DocumentTypeAdmin)


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
    my_search_fields = ["name", "comment"]
    list_filter = ["doctype", "ts_created", "ts_modified", "content_type"]
    search_fields = my_search_fields


admin.site.register(Document, DocumentAdmin)


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
    my_search_fields = ["name", "first_name", "email", "slot__event__name"]
    list_filter = [
        "slot__event__active",
        "check1",
        "check2",
        "check3",
        "check4",
        "check5",
        "slot__event",
        "slot",
    ]
    search_fields = my_search_fields


admin.site.register(Registration, RegistrationAdmin)


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
    my_search_fields = ["alt_text", "event__name", "comment"]
    list_filter = ["event", "max_places"]
    search_fields = my_search_fields


admin.site.register(RegistrationSlot, RegistrationSlotAdmin)


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
    my_search_fields = ["name", "description", "confirmation_mail_sender", "comment"]
    list_filter = [
        "active",
        "confirmation_mail_sender",
        "publication_type",
        "publication_start",
        "publication_end",
        "ts_created",
    ]
    search_fields = my_search_fields
    inlines = [RegistrationSlotInline]

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)


admin.site.register(RegistrationEvent, RegistrationEventAdmin)


@admin.decorators.register(RentalUnit)
class RentalUnitAdmin(GenoBaseAdmin):
    fields = [
        "name",
        ("label", "label_short"),
        ("rental_type", "rooms", "min_occupancy"),
        ("building", "floor"),
        ("area", "area_balcony", "area_add"),
        ("height", "volume"),
        ("rent_netto", "nk", "nk_electricity", "rent_total"),
        ("share", "depot"),
        "note",
        "svg_polygon",
        "description",
        "status",
        "adit_serial",
        "active",
        "comment",
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
        "share",
        "status",
        "comment",
    ]
    my_search_fields = [
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
    list_filter = ["rental_type", "rooms", "building__name", "floor", "status", "active"]
    search_fields = my_search_fields


def contract_mark_signed(modeladmin, request, queryset):
    queryset.update(state="unterzeichnet")


contract_mark_signed.short_description = 'Als "unterzeichnet" markieren'


def contract_mark_offered(modeladmin, request, queryset):
    queryset.update(state="angeboten")


contract_mark_offered.short_description = 'Als "angeboten" markieren'


def contract_set_startdate_nextmonth(modeladmin, request, queryset):
    new_date = (datetime.date.today().replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    queryset.update(date=new_date)


contract_set_startdate_nextmonth.short_description = (
    "Mietbeginn auf 1. des nächsten Monats setzten"
)


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


class ContractAdmin(GenoBaseAdmin):
    form = ContractAdminModelForm
    fields = [
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
        "emonitor_id",
        "object_actions",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "object_actions", "links", "backlinks"]
    list_display = ["__str__", "state", "date", "date_end", "note", "comment"]
    my_search_fields = [
        "contractors__name",
        "contractors__first_name",
        "contractors__organization",
        "children__name__name",
        "children__name__first_name",
        "rental_units__name",
        "bankaccount",
        "note",
        "comment",
    ]
    list_filter = [
        "state",
        "rental_units__rental_type",
        "rental_units__floor",
        "rental_units__rooms",
        "date",
        "date_end",
        "send_qrbill",
    ]
    search_fields = my_search_fields
    actions = GenoBaseAdmin.actions + [
        contract_mark_signed,
        contract_mark_offered,
        contract_set_startdate_nextmonth,
    ]
    filter_horizontal = ["contractors", "children", "rental_units"]


admin.site.register(Contract, ContractAdmin)


def invoice_revert_consolidation(modeladmin, request, queryset):
    queryset.update(consolidated=False)


invoice_revert_consolidation.short_description = 'Als "NICHT konsolidiert" markieren'


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
    my_search_fields = [
        "name",
        "income_account",
        "receivables_account",
        "note",
        "reference_id",
        "comment",
    ]
    list_filter = ["active", "manual_allowed", "linked_object_type"]
    search_fields = my_search_fields


admin.site.register(InvoiceCategory, InvoiceCategoryAdmin)


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
    my_search_fields = [
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
    search_fields = my_search_fields
    actions = GenoBaseAdmin.actions + [invoice_revert_consolidation]

    def person_or_contract(self, obj):
        if obj.contract:
            return str(obj.contract)
        else:
            return str(obj.person)

    person_or_contract.short_description = "Person/Vertrag"


admin.site.register(Invoice, InvoiceAdmin)


class LookupTableAdmin(GenoBaseAdmin):
    model = LookupTable
    fields = ["name", "lookup_type", "value", "ts_created", "ts_modified", "links", "backlinks"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "lookup_type", "value", "ts_modified"]
    my_search_fields = ["name", "value"]
    list_filter = ["lookup_type"]
    search_fields = my_search_fields


admin.site.register(LookupTable, LookupTableAdmin)


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
    my_search_fields = ["name", "text"]
    list_filter = [
        "active",
        "template_type",
        "manual_creation_allowed",
        "template_context",
        "ts_created",
        "ts_modified",
    ]
    search_fields = my_search_fields
    filter_horizontal = ["template_context"]

    class Media:
        js = ("geno/js/content_template_admin.js",)


admin.site.register(ContentTemplate, ContentTemplateAdmin)


class ContentTemplateOptionAdmin(GenoBaseAdmin):
    model = ContentTemplateOption
    fields = ["name", "value", "comment", "ts_created", "ts_modified"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "value", "comment", "ts_created", "ts_modified"]
    my_search_fields = ["name", "value", "comment"]
    list_filter = ["name", "ts_created", "ts_modified"]
    search_fields = my_search_fields


admin.site.register(ContentTemplateOption, ContentTemplateOptionAdmin)


class ContentTemplateOptionTypeAdmin(GenoBaseAdmin):
    model = ContentTemplateOption
    fields = ["name", "description", "comment", "ts_created", "ts_modified"]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "description", "comment", "ts_created", "ts_modified"]
    my_search_fields = ["name", "description", "comment"]
    list_filter = ["ts_created", "ts_modified"]
    search_fields = my_search_fields


admin.site.register(ContentTemplateOptionType, ContentTemplateOptionTypeAdmin)


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
    my_search_fields = ["name", "comment", "value"]
    list_filter = ["name", "ts_created", "ts_modified", "content_type"]
    search_fields = my_search_fields


admin.site.register(GenericAttribute, GenericAttributeAdmin)
