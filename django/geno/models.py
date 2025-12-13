import datetime
import logging
import math
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.template import Template
from django.utils import timezone
from django.utils.html import format_html, format_html_join, mark_safe
from filer.fields.file import FilerFileField

import geno.settings as geno_settings
from cohiva.utils.settings import (
    get_default_email,
    get_default_formal_choice,
    get_default_mail_footer,
)
from geno.model_fields import LowercaseEmailField
from geno.utils import (
    is_member,
    is_renting,
    nformat,
    sanitize_filename,
)  # , send_info_mail, send_error_mail

logger = logging.getLogger("access_portal")


## Abstract base class
class GenoBase(models.Model):
    comment = models.CharField("Kommentar", max_length=500, blank=True)
    ts_created = models.DateTimeField("Erstellt", auto_now_add=True)
    ts_modified = models.DateTimeField("Geändert", auto_now=True)

    ## List objects linked to by this instance.
    @admin.display(description="Links")
    def links(self):
        foreign_key_fields = []
        for field in self._meta.get_fields():
            if field.is_relation and field.concrete and not field.auto_created:
                if field.name == "content_type" and field.related_model == ContentType:
                    ## Standard generic relation -> assume standard field name 'object_id' for ID.
                    content_type = getattr(self, field.name)
                    objs = content_type.model_class().objects.get(pk=self.object_id)
                    field_verbose_name = content_type.model_class()._meta.verbose_name
                else:
                    if self.pk:
                        ## Object is saved
                        objs = getattr(self, field.name, None)
                    else:
                        objs = None
                    field_verbose_name = field.related_model._meta.verbose_name
                obj_data = []
                if field.many_to_many:
                    for obj in objs.all().order_by("-ts_modified")[
                        : geno_settings.MAX_LINKS_DISPLAY
                    ]:
                        obj_data.append((obj._meta.app_label, obj._meta.model_name, obj.pk, obj))
                elif objs:
                    obj_data.append((objs._meta.app_label, objs._meta.model_name, objs.pk, objs))
                if obj_data:
                    links = format_html_join(", ", '<a href="/admin/{}/{}/{}">{}</a>', obj_data)
                    foreign_key_fields.append((field_verbose_name, links))
        return format_html(
            "<ul>{}</ul>", format_html_join("\n", "<li>{}: {}</li>", foreign_key_fields)
        )

    ## List objects that link to this instance.
    @admin.display(description="Backlinks")
    def backlinks(self):
        if self.id is None:
            return ""
        items = []
        models_done = []
        for rfield in self._meta.get_fields():
            if (
                not rfield.concrete
                and rfield.related_model
                and rfield.related_model not in models_done
            ):
                foreign_key_fields = []
                ## ForeignKey links
                for field in rfield.related_model._meta.get_fields():
                    if field.is_relation and field.concrete:
                        inst_filter = {}
                        if isinstance(self, field.related_model):
                            ## Get instances that link to this object
                            inst_filter["%s__pk" % field.name] = self.id
                        elif field.related_model == ContentType and field.name == "content_type":
                            ## Standard generic relation
                            ## => assume standard field name 'object_id' for ID.
                            inst_filter["object_id"] = self.id
                            inst_filter["content_type"] = ContentType.objects.get(
                                app_label=self._meta.app_label, model=self._meta.model_name
                            )
                        if inst_filter:
                            for instance in rfield.related_model.objects.filter(
                                **inst_filter
                            ).order_by("-ts_modified")[: geno_settings.MAX_LINKS_DISPLAY]:
                                foreign_key_fields.append(
                                    (
                                        instance._meta.app_label,
                                        instance._meta.model_name,
                                        instance.id,
                                        instance,
                                    )
                                )
                if foreign_key_fields:
                    items.append(
                        (
                            rfield.related_model._meta.verbose_name,
                            format_html(
                                "<ul>{}</ul>",
                                format_html_join(
                                    "",
                                    '<li><a href="/admin/{}/{}/{}">{}</a></li>',
                                    foreign_key_fields,
                                ),
                            ),
                        )
                    )
                models_done.append(rfield.related_model)
        return format_html("<ul>{}</ul>", format_html_join("\n", "<li>{}: {}</li>", items))

    def get_object_actions(self):
        return []

    @admin.display(description="Aktionen")
    def object_actions(self):
        actions = self.get_object_actions()
        if not actions:
            return None
        action_buttons = []
        for action in actions:
            if len(action) > 2:
                button_html = format_html(
                    '<a href="{}" title="{}">{}<span class="help help-tooltip help-icon">'
                    "</span></a>",
                    action[0],
                    action[2],
                    action[1],
                )
            else:
                button_html = format_html('<a href="{}">{}</a>', *action[0:2])
            action_buttons.append(f"<li>{button_html}</li>")
        action_list = "\n".join(action_buttons)
        return mark_safe(f'<ul class="cohiva_object-actions">{action_list}</ul>')

    def save_as_copy(self):
        if hasattr(self, "name") and isinstance(self.name, str):
            self.name = "%s [KOPIE]" % self.name
        self.pk = None
        self.id = None
        self._state.adding = True
        self.save()

    def __str__(self):
        if hasattr(self, "name") and self.name:
            return self.name
        return f"{type(self).__name__}-{self.pk}"

    class Meta:
        abstract = True


class BankAccount(GenoBase):
    iban = models.CharField("IBAN", max_length=34, blank=True)
    financial_institution = models.CharField("Finanzinstitut", max_length=100, blank=True)
    account_holders = models.CharField("Kontoinhaber", max_length=100, blank=True)

    def __str__(self):
        account_holders = self.account_holders.strip() if self.account_holders else ""
        iban = self.iban.strip() if self.iban else ""
        if account_holders and iban:
            return f"{account_holders} ({iban})"
        elif account_holders:
            return account_holders
        elif iban:
            return iban
        elif self.comment:
            return f"Ohne IBAN / {self.comment}"
        else:
            return "Kein Konto angegeben"

    class Meta:
        verbose_name = "Bankkonto"
        verbose_name_plural = "Bankkonten"


class Address(GenoBase):
    TITLE_CHOICES = (
        ("Herr", "Herr"),
        ("Frau", "Frau"),
        ("Divers", "Divers"),
        ("Paar", "Familie/Paar"),
        ("Org", "Organisation/Firma"),
    )
    FORMAL_CHOICES = (
        ("Du", "Du/Ihr"),
        ("Sie", "Sie"),
    )
    INTEREST_ACTION_CHOICES = (
        ("Bank", "Überweisung auf angegebenes Bankkonto"),
        ("Loan", "Dem Darlehen anrechnen"),
        ("Deposit", "Dem Depositenkassenkonto anrechnen"),
    )
    organization = models.CharField(
        "Organisation", max_length=150, blank=True, help_text="Bei Privatpersonen: leer lassen"
    )
    name = models.CharField(
        "Nachname", max_length=150, blank=True, help_text="Bei Organisationen: Kontaktperson"
    )  ## db_index=True ???
    first_name = models.CharField("Vorname", max_length=100, blank=True)  ## db_index=True ???
    title = models.CharField("Anrede", max_length=20, choices=TITLE_CHOICES, blank=True)
    formal = models.CharField(
        "Duzen", max_length=20, choices=FORMAL_CHOICES, default=get_default_formal_choice
    )
    extra = models.CharField(
        "Adresszusatz", max_length=100, blank=True, help_text="z.B. c/o (optional)"
    )
    street_name = models.CharField("Strasse", max_length=100, blank=True)
    house_number = models.CharField("Hausnummer", max_length=100, blank=True)
    po_box = models.BooleanField("Postfach", default=False)
    po_box_number = models.CharField("Postfach Nr.", max_length=100, blank=True)
    city_zipcode = models.CharField("PLZ", max_length=30, blank=True)
    city_name = models.CharField("Ort", max_length=100, blank=True)
    country = models.CharField("Land", max_length=100, blank=True, default="Schweiz")
    telephone = models.CharField("Telefon", max_length=30, blank=True)
    mobile = models.CharField("2. Telefon", max_length=30, blank=True)
    telephoneOffice = models.CharField("Telefon Geschäft", max_length=30, blank=True)
    telephoneOffice2 = models.CharField("2. Telefon Geschäft", max_length=30, blank=True)
    email = LowercaseEmailField("Email", blank=True)
    email2 = LowercaseEmailField("2. Email", blank=True)
    website = models.CharField("Webseite", max_length=300, blank=True)
    date_birth = models.DateField("Geburtsdatum", null=True, blank=True)
    hometown = models.CharField("Heimatort", max_length=50, blank=True)
    occupation = models.CharField("Beruf/Ausbildung", max_length=150, blank=True)
    bankaccount = models.ForeignKey(
        BankAccount,
        verbose_name="Kontoverbindung",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Z.B. für Auszahlung Zinsen",
    )
    interest_action = models.CharField(
        "Standard-Zinsvergütung",
        max_length=100,
        choices=INTEREST_ACTION_CHOICES,
        blank=True,
        help_text="Für Darlehen. Leer = Nachfragen",
    )
    paymentslip = models.BooleanField(
        "Kein automatischer Versand",
        default=False,
        help_text=(
            "Auswählen für Spezialfälle, welche manuell verarbeitet werden, "
            "z.B. Versand per Post statt E-Mail."
        ),
    )
    ignore_in_lists = models.BooleanField(
        "Für Listen ignorieren",
        default=False,
        help_text=(
            "Auswählen für Personen, die nicht auf Listen wie Bewohnendenspiegel "
            "oder Sonnerie/Briefkasten etc. erscheinen sollen."
        ),
    )
    active = models.BooleanField("Aktiv", db_index=True, default=True)
    import_id = models.CharField(
        "Import-ID", max_length=255, unique=True, null=True, default=None, blank=True
    )
    random_id = models.UUIDField("Zufalls-ID", unique=True, default=uuid.uuid4, editable=False)

    ## Reverse relation to Documents/Attributes
    documents = GenericRelation("Document", related_query_name="addresses")
    attributes = GenericRelation("GenericAttribute", related_query_name="addresses")

    ## Link to Django User (optional)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    login_permission = models.BooleanField(
        "Login auch ohne Mitgliedschaft/Mietvertrag erlauben", default=False
    )

    ## CardDAV sync data
    carddav_href = models.CharField("carddav_href", max_length=255, blank=True)
    carddav_etag = models.CharField("carddav_etag", max_length=255, blank=True)
    carddav_syncts = models.DateTimeField("carddav_syncts", null=True, blank=True)

    def __str__(self):
        if self.organization:
            return "%s, %s %s" % (self.organization, self.first_name, self.name)
        else:
            return "%s, %s" % (self.name, self.first_name)

    @property
    @admin.display(description="Strasse/Nr.")
    def street(self):
        ret = ""
        if self.street_name:
            ret = self.street_name
            if self.house_number:
                ret += f" {self.house_number}"
            if self.po_box:
                ret += ", Postfach"
                if self.po_box_number:
                    ret += f" {self.po_box_number}"
        elif self.po_box:
            ret = "Postfach"
            if self.po_box_number:
                ret += f" {self.po_box_number}"
        return ret

    @property
    @admin.display(description="PLZ/Ort")
    def city(self):
        if self.city_zipcode and self.city_name:
            return f"{self.city_zipcode} {self.city_name}"
        else:
            return self.city_name

    @admin.display(description="Person/Organisation")
    def list_name(self):
        return self.__str__()

    def get_filename_str(self):
        if self.organization:
            filename = "%s_%s%s" % (self.organization, self.name, self.first_name)
        else:
            filename = "%s_%s" % (self.name, self.first_name)
        return sanitize_filename(filename)

    def get_absolute_url(self):
        return "/admin/geno/address/%i/" % self.id

    def list_rental_units(self, short=True, exclude_minor=True, as_list=False):
        units = []
        for c in self.get_contracts():
            units.extend(
                c.list_rental_units(short=short, exclude_minor=exclude_minor, as_list=True)
            )
        if as_list:
            return units
        else:
            return "/".join(units)

    def get_rental_units(self):
        units = []
        for c in self.get_contracts():
            units.extend(c.rental_units.all())
        return units

    def get_contracts(self):
        if self.address_contracts.exists():
            return get_active_contracts(pre_select=self.address_contracts.all())
        elif hasattr(self, "address_child"):
            if self.address_child.child_contracts.exists():
                return get_active_contracts(pre_select=self.address_child.child_contracts.all())
        return []

    def is_tenant(self):
        return bool(Tenant.objects.filter(name=self).filter(active=True).first())

    def get_roles(self):
        roles = []
        if self.active:
            roles.append("user")
            if is_member(self):
                roles.append("member")
            if is_renting(self):
                roles.append("renter")
                roles.append("community")
            elif self.is_tenant():
                roles.append("community")
        return roles

    def get_full_name(self):
        if self.first_name and self.name:
            name_person = f"{self.first_name} {self.name}"
        else:
            name_person = self.name
        if self.organization and name_person:
            return f"{self.organization}, {name_person}"
        return self.organization or name_person or "[Ohne Name]"

    def get_mail_recipient(self):
        if settings.DEBUG or settings.DEMO or self.email.split("@")[-1] == "example.com":
            email_address = settings.TEST_MAIL_RECIPIENT
        else:
            email_address = self.email
        mail_recipient = f'"{self.get_full_name()}" <{email_address}>'
        return mail_recipient

    def get_context(self):
        words = {
            "dir": ["Ihnen", "euch"],
            "dein": ["Ihr", "euer"],
            "Dein": ["Ihr", "Euer"],
            "deine": ["Ihre", "eure"],
            "Deine": ["Ihre", "Eure"],
            "deiner": ["Ihrer", "eurer"],
            "deinen": ["Ihren", "euren"],
            "deinem": ["Ihrem", "eurem"],
            "Deinem": ["Ihrem", "Eurem"],
            "deines": ["Ihres", "eures"],
            "dich": ["Sie", "euch"],
            "du": ["Sie", "ihr"],
            "Du": ["Sie", "Ihr"],
            "du_dich": ["Sie sich", "ihr euch"],
            "eurem": ["Ihrem", "eurem"],
            "euch": ["Sie", "euch"],
            "hast": ["haben", "habt"],
            "kannst": ["können", "könnt"],
            "leistest": ["leisten", "leistet"],
            "wünschst": ["wünschen", "wünscht"],
            "findest": ["finden", "findet"],
            "erhältst": ["erhalten", "erhält"],
            "sende": ["senden Sie", "sendet"],
            "verwende": ["verwenden Sie", "verwendet"],
            "beachte": ["beachten Sie", "beachtet"],
            "gewährst": ["gewähren", "gewährt"],
            "planst": ["planen", "plant"],
            "wirst": ["werden", "werdet"],
            "möchtest": ["möchten", "möchtet"],
            "fülle": ["füllen Sie", "füllt"],
            "bekommst": ["bekommen", "bekommt"],
            "wurdest": ["wurden", "wurdet"],
            "richte": ["richten Sie", "richtet"],
            "richtet": ["richten Sie", "richtet"],
            "Kontaktiere": ["Kontaktieren Sie", "Kontaktiert"],
            "kontaktiere": ["kontaktieren Sie", "kontaktiert"],
            "Retourniere": ["Retournieren Sie", "Retourniert"],
            "retourniere": ["retournieren Sie", "retourniert"],
            "brauchst": ["brauchen", "braucht"],
            "bist": ["sind", "seid"],
            "leite": ["leiten Sie", "leitet"],
            "weisst": ["wissen", "wisst"],
            "einbezahlst": ["einbezahlen", "einbezahlt"],
            "einzahlst": ["einzahlen", "einzahlt"],
            "zahle": ["zahlen Sie", "zahlt"],
            "Zahle": ["Zahlen Sie", "Zahlt"],
            "anmeldest": ["anmelden", "anmeldet"],
        }
        words_select = 0

        c = {}
        c["organisation"] = self.organization
        c["vorname"] = self.first_name
        c["name"] = self.name
        if self.extra:
            c["strasse"] = "%s\n%s" % (self.extra, self.street)
        else:
            c["strasse"] = self.street

        ## Add room number if in building
        c["roomnr"] = ""
        if self.street in settings.GENO_ADDRESSES_WITH_APARTMENT_NUMBER:
            ## Add first apartment/room number
            ru = self.list_rental_units(as_list=True)
            # ru.sort()
            # ru.sort(key = int)
            for r in ru:
                if not r.startswith("PP") and not r.startswith("9"):
                    c["roomnr"] = r
                    c["strasse"] = "%s / %s" % (c["strasse"], c["roomnr"])

        c["wohnort"] = self.city
        c["telefon"] = "Keine Angabe"
        c["email"] = "Keine Angabe"
        c["geburtsdatum"] = "Keine Angabe"
        c["uuid"] = str(self.random_id)
        if self.telephone and self.mobile:
            c["telefon"] = "%s (Mobil: %s)" % (self.telephone, self.mobile)
        elif self.telephone:
            c["telefon"] = self.telephone
        elif self.mobile:
            c["telefon"] = self.mobile
        if self.email:
            c["email"] = self.email
        if self.date_birth:
            c["geburtsdatum"] = self.date_birth.strftime("%d.%m.%Y")
        anrede_person = "Guten Tag"
        if self.formal == "Du":
            if self.title == "Herr" and len(self.first_name):
                anrede_person = "Lieber %s" % self.first_name
                words_select = 0
            elif self.title == "Divers" and len(self.first_name):
                anrede_person = "Liebe*r %s" % self.first_name
                words_select = 0
            elif self.title == "Frau" and len(self.first_name):
                anrede_person = "Liebe %s" % self.first_name
                words_select = 0
            elif self.title == "" and len(self.first_name):
                anrede_person = "Hallo %s" % self.first_name
                words_select = 0
            else:
                ## Paar or Org.
                words_select = 2
        else:
            if self.title == "Herr" and len(self.name):
                if settings.GENO_FORMAL:
                    anrede_person = "Sehr geehrter Herr %s" % self.name
                else:
                    anrede_person = "Lieber Herr %s" % self.name
                words_select = 1
            elif self.title == "Divers" and len(self.name):
                if settings.GENO_FORMAL:
                    anrede_person = "Sehr geehrte*r %s" % self.name
                else:
                    anrede_person = "Guten Tag  %s" % self.name
                words_select = 1
            elif self.title == "Frau" and len(self.name):
                if settings.GENO_FORMAL:
                    anrede_person = "Sehr geehrte Frau %s" % self.name
                else:
                    anrede_person = "Liebe Frau %s" % self.name
                words_select = 1
            elif self.title == "":
                if len(self.first_name) and len(self.name):
                    anrede_person = "Guten Tag %s %s" % (self.first_name, self.name)
                words_select = 1
            else:
                ## Paar or Org.
                if settings.GENO_FORMAL:
                    anrede_person = "Sehr geehrte Damen und Herren"
                words_select = 1
        if len(self.organization):
            if (
                self.organization.startswith("Verein ")
                or self.organization.endswith("verein")
                or self.organization.startswith("Hausverein")
                or self.organization.startswith("Verband ")
                or self.organization.endswith("verband")
                or self.organization.startswith("Regionalverband")
                or self.organization.endswith("regionalverband")
                or self.organization.endswith("Gewerkschaftsbund")
                or self.organization.endswith("Asylsozialdienst")
                or self.organization.startswith("sgf Bern")
            ):
                c["anrede"] = "Lieber %s" % self.organization
            elif self.organization.startswith("Kollektiv ") or self.organization.endswith(
                "kollektiv"
            ):
                c["anrede"] = "Liebes %s" % self.organization
            else:
                c["anrede"] = "Liebe %s" % self.organization
            if anrede_person != "Guten Tag":
                c["anrede"] = "%s, %s" % (c["anrede"], anrede_person)
        else:
            c["anrede"] = anrede_person

        for word in list(words.keys()):
            if words_select == 0:
                c[word] = word.replace("_", " ")
            else:
                c[word] = words[word][words_select - 1]

        today = datetime.date.today()
        c["datum"] = today.strftime("%d.%m.%Y")
        c["monat"] = today.strftime("%B")
        c["jahr"] = today.year
        today_plus30 = today + datetime.timedelta(days=30)
        c["datum_plus30"] = today_plus30.strftime("%d.%m.%Y")
        c["monat_plus30"] = today_plus30.strftime("%B")
        c["jahr_plus30"] = today_plus30.year

        c["org_info"] = settings.GENO_ORG_INFO

        return c

    def get_object_actions(self):
        return [
            (
                "/geno/share/statement/current_year/%s/" % self.pk,
                "Kontoauszug erzeugen (aktuelles Jahr)",
            ),
            (
                "/geno/share/statement/previous_year/%s/" % self.pk,
                "Kontoauszug erzeugen (Vorjahr)",
            ),
        ]

    def save_as_copy(self):
        self.user = None
        self.import_id = None
        self.random_id = uuid.uuid4()
        super().save_as_copy()

    class Meta:
        unique_together = ["organization", "name", "first_name", "email"]
        ordering = ["organization", "name", "first_name"]
        verbose_name = "Adresse"
        verbose_name_plural = "Adressen"


@receiver(post_save, sender=User)
@receiver(post_save, sender=Address)
def sync_user(sender, instance, created, **kwargs):
    from geno.utils import send_info_mail

    if sender.__name__ == "User":
        user = instance
    else:
        user = instance.user
    if hasattr(user, "address"):
        ## Sync email/name/vorname but make sure user email is unique!!
        info = []
        updated = False
        if user.address.first_name and user.first_name != user.address.first_name:
            info.append(
                "Updating first_name for user %s from address: %s -> %s"
                % (user.username, user.first_name, user.address.first_name)
            )
            user.first_name = user.address.first_name
            updated = True
        if user.address.name and user.last_name != user.address.name:
            info.append(
                "Updating last_name for user %s from address: %s -> %s"
                % (user.username, user.last_name, user.address.name)
            )
            user.last_name = user.address.name
            updated = True
        if user.address.email and user.email != user.address.email:
            try:
                existing_user = User.objects.get(email=user.address.email)
                info.append(
                    "WARNING: User with same email exists already: %s. "
                    "CAN'T update email for %s from Address (%s -> %s)"
                    % (existing_user.username, user.username, user.email, user.address.email)
                )
            except User.DoesNotExist:
                info.append(
                    "Updating email for user %s from address: %s -> %s"
                    % (user.username, user.email, user.address.email)
                )
                user.email = user.address.email
                updated = True
        if info:
            for i in info:
                logger.warning(i)
            send_info_mail("Updated user from address: %s" % (user.username), "\n".join(info))
        if updated:
            user.save()


class Child(GenoBase):
    name = models.OneToOneField(
        Address, verbose_name="Person", on_delete=models.CASCADE, related_name="address_child"
    )
    presence = models.DecimalField("Anwesenheit (Tage/Woche)", max_digits=2, decimal_places=1)
    parents = models.CharField("Eltern(teil)", max_length=200, blank=True)
    notes = models.TextField("Bemerkungen", blank=True)
    import_id = models.CharField(
        "Import-ID", max_length=255, unique=True, null=True, default=None, blank=True
    )

    @admin.display(description="Alter", ordering="name__date_birth")
    def age(self, precision=1):
        if self.name.date_birth:
            age_years = (datetime.date.today() - self.name.date_birth) / datetime.timedelta(
                days=365.2425
            )
            if precision == 0:
                ## Ganzzahliges Alter: abrunden
                return "%d" % math.floor(age_years)
            return nformat(age_years, precision)
        else:
            return "-"

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    class Meta:
        ordering = ["name"]
        verbose_name = "Kind"
        verbose_name_plural = "Kinder"


class Building(GenoBase):
    name = models.CharField("Liegenschaft", max_length=100, unique=True)
    description = models.CharField("Beschreibung", max_length=200, blank=True)
    street_name = models.CharField("Strasse", max_length=100, blank=True)
    house_number = models.CharField("Hausnummer", max_length=100, blank=True)
    city_zipcode = models.CharField("PLZ", max_length=30, blank=True)
    city_name = models.CharField("Ort", max_length=100, blank=True)
    country = models.CharField("Land", max_length=100, blank=True, default="Schweiz")
    value_insurance = models.DecimalField(
        "Gebäudeversicherungswert (Fr.)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    value_build = models.DecimalField(
        "Anlagekosten (Fr.)", max_digits=12, decimal_places=2, null=True, blank=True
    )
    team = models.CharField(
        "Rocket.Chat Team",
        max_length=100,
        blank=True,
        help_text=(
            "Name des Rocket.Chat Teams für diese Liegenschaft "
            "(für automatische Zuordnung von Nutzer:innen)."
        ),
    )
    accounting_postfix = models.PositiveIntegerField("Buchhaltungs-Postfix", null=True, blank=True)
    egid = models.PositiveIntegerField("EGID", null=True, blank=True)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Liegenschaft"
        verbose_name_plural = "Liegenschaften"


class Tenant(GenoBase):
    name = models.OneToOneField(
        Address, verbose_name="Person", on_delete=models.CASCADE, related_name="address_tenant"
    )
    building = models.ForeignKey(Building, verbose_name="Gebäude", on_delete=models.CASCADE)
    key_number = models.CharField(
        "Schlüsselnr.",
        default="",
        blank=True,
        max_length=30,
        help_text="Nummer des ausgegebenen Schlüssels.",
    )
    notes = models.TextField("Bemerkungen", blank=True)
    invitation_date = models.DateTimeField("Einladung geschickt am", null=True, blank=True)
    active = models.BooleanField("Aktiv", default=True)

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    class Meta:
        ordering = ["name"]
        verbose_name = "Externe Nutzer:in"
        verbose_name_plural = "Externe Nutzer:innen"


class Member(GenoBase):
    name = models.OneToOneField(
        Address, verbose_name="Person/Organisation", on_delete=models.CASCADE
    )
    date_join = models.DateField("Eintritt")
    date_leave = models.DateField("Austritt", null=True, blank=True)
    ## verbose_names of flags are set below!
    flag_01 = models.BooleanField(default=False)
    flag_02 = models.BooleanField(default=False)
    flag_03 = models.BooleanField(default=False)
    flag_04 = models.BooleanField(default=False)
    flag_05 = models.BooleanField(default=False)
    notes = models.TextField("Bemerkungen", blank=True)

    ## Reverse relation to Documents
    documents = GenericRelation("Document", related_query_name="members")

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    def get_absolute_url(self):
        return "/admin/geno/member/%i/" % self.id

    def get_object_actions(self):
        actions = []
        for dt in DocumentType.objects.filter(active=True).filter(name__startswith="member"):
            actions.append(
                (
                    "/geno/documents/%s/%s/create/" % (dt.name, self.pk),
                    "%s erzeugen" % (dt.description),
                )
            )
        return actions

    class Meta:
        ordering = ["name"]
        verbose_name = "Mitglied"
        verbose_name_plural = "Mitglieder"
        permissions = (
            ("canview_member", "Can see members"),
            ("canview_member_overview", "Can see member overview"),
            ("canview_member_mailinglists", "Can see member mailinglist information"),
            ("canview_billing", "Can see billing/payment information"),
            ("check_payments", "Kann Zahlungen überprüfen"),
            ("transaction", "Kann Zahlungen erfassen"),
            ("transaction_invoice", "Kann Rechnungen erstellen und bezahlte erfassen"),
            ("admin_import", "Can import data"),
            ("admin_maintenance", "Can run admin maintenance tasks"),
            ("send_mail", "Can send emails to members/users"),
            ("send_newmembers", "Kann neue Beitritte bestätigen"),
            ("adit", "Kann Gegensprechanlage (ADIT) Daten sehen/bearbeiten"),
        )


## Set customized verbose_names here to prevent them from entering migrations.
Member._meta.get_field("flag_01").verbose_name = geno_settings.MEMBER_FLAGS[1]
Member._meta.get_field("flag_02").verbose_name = geno_settings.MEMBER_FLAGS[2]
Member._meta.get_field("flag_03").verbose_name = geno_settings.MEMBER_FLAGS[3]
Member._meta.get_field("flag_04").verbose_name = geno_settings.MEMBER_FLAGS[4]
Member._meta.get_field("flag_05").verbose_name = geno_settings.MEMBER_FLAGS[5]


class MemberAttributeType(GenoBase):
    name = models.CharField("Name", max_length=50, unique=True)
    description = models.CharField("Beschreibung", max_length=200)

    class Meta:
        verbose_name = "Mitglieder Attribut Typ"
        verbose_name_plural = "Mitglieder Attribut Typen"


class MemberAttribute(GenoBase):
    member = models.ForeignKey(Member, verbose_name="Mitglied", on_delete=models.CASCADE)
    attribute_type = models.ForeignKey(
        MemberAttributeType, verbose_name="Attributtyp", on_delete=models.CASCADE
    )
    date = models.DateField("Datum", null=True, blank=True)
    value = models.CharField("Wert", max_length=100)

    def __str__(self):
        date_str = ""
        if self.date:
            date_str = " (%s)" % self.date.strftime("%d.%m.%Y")
        return "%s [%s - %s]%s" % (self.member, self.attribute_type, self.value, date_str)

    class Meta:
        verbose_name = "Mitglieder Attribut"
        verbose_name_plural = "Mitglieder Attribute"


class ShareType(GenoBase):
    name = models.CharField("Name", max_length=50, unique=True)
    description = models.CharField("Beschreibung", max_length=200)
    standard_interest = models.DecimalField(
        "Standard-Zinssatz",
        max_digits=4,
        decimal_places=2,
        default=0.00,
        help_text="Zinssatz gilt für alle Beteiligungen mit Zinssatz-Modus «Standard».",
    )

    class Meta:
        verbose_name = "Beteiligungstyp"
        verbose_name_plural = "Beteiligungstypen"


class Share(GenoBase):
    name = models.ForeignKey(Address, verbose_name="Person/Organisation", on_delete=models.CASCADE)
    share_type = models.ForeignKey(
        ShareType, verbose_name="Beteiligungstyp", on_delete=models.CASCADE
    )
    STATE_CHOICES = (
        ("gefordert", "gefordert"),
        ("bezahlt", "bezahlt"),
    )
    state = models.CharField("Status", max_length=50, choices=STATE_CHOICES, blank=True)
    date = models.DateField("Datum Beginn")
    date_end = models.DateField("Datum Ende", null=True, blank=True, default=None)
    duration = models.PositiveIntegerField(
        "Laufzeit", null=True, blank=True, help_text="Jahre (bei Darlehen)"
    )
    date_due = models.DateField(
        "Fälligkeit",
        null=True,
        blank=True,
        help_text="Explizites Fälligkeitsdatum; leer=autom. mit Laufzeit berechnet",
    )
    quantity = models.PositiveIntegerField("Anzahl", default=1)
    value = models.DecimalField("Betrag pro Stück", max_digits=10, decimal_places=2)
    INTEREST_MODE_CHOICES = (
        ("Standard", "Standard"),
        ("Manual", "Manuell"),
    )
    interest_mode = models.CharField(
        "Zinsatz-Modus",
        max_length=50,
        default="Standard",
        choices=INTEREST_MODE_CHOICES,
        help_text="Standard = Zinssatz von Beteiligungstyp übernehmen",
    )
    # interest = models.DecimalField('Zinssatz', max_digits=4, decimal_places=2, default=0.00)
    manual_interest = models.DecimalField(
        "Zinssatz (manuell)",
        max_digits=4,
        decimal_places=2,
        default=0.00,
        help_text="Gilt, falls Zinssatz-Modus auf «Manuell» eingestellt ist.",
    )
    is_interest_credit = models.BooleanField("Zinsgutschrift", default=False)
    is_pension_fund = models.BooleanField("WEF-Guthaben (BVG/3.Säule)", default=False)
    is_business = models.BooleanField("Gewerbe", default=False)
    attached_to_contract = models.ForeignKey(
        "Contract",
        verbose_name="Fixe Zuteilung als Pflichtanteil für Vertrag",
        help_text=(
            "Falls leer werden Anteilscheine automatisch als Pflichtanteile zu "
            "Verträgen zugewiesen"
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contract_attached_shares",
    )
    attached_to_building = models.ForeignKey(
        "Building",
        verbose_name="Liegenschaft",
        help_text=("Nur ausfüllbar wenn kein Vertrag gewählt ist."),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="building_attached_shares",
    )
    note = models.CharField("Zusatzinfo", max_length=200, blank=True)

    ## Reverse relation to Documents
    documents = GenericRelation("Document", related_query_name="shares")

    @admin.display(description="Zinssatz")
    def interest(self):
        if self.interest_mode == "Standard":
            return self.share_type.standard_interest
        else:
            return self.manual_interest

    def __str__(self):
        extra_info = self.share_type
        if self.state:
            extra_info = "%s, %s" % (extra_info, self.state)
        if self.is_pension_fund:
            extra_info = "%s, BVG-GUTHABEN!!" % (extra_info)
        return "%s [%s]" % (self.name, extra_info)

    def get_object_actions(self):
        actions = []
        for dt in DocumentType.objects.filter(active=True).filter(name__startswith="share"):
            actions.append(
                (
                    "/geno/documents/%s/%s/create/" % (dt.name, self.pk),
                    "%s erzeugen" % (dt.description),
                )
            )
        return actions

    @admin.display(description="Total")
    def value_total(self):
        if self.quantity and self.value:
            return self.quantity * self.value
        else:
            return "-"

    def clean(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        # contract and building relations may not both be present
        if self.attached_to_building is not None and self.attached_to_contract is not None:
            raise ValidationError("Vertrag und Liegeneschaft dürfen nicht beide ausgewählt sein.")
        super().clean(*args, **kwargs)

    class Meta:
        verbose_name = "Beteiligung"
        verbose_name_plural = "Beteiligungen"
        constraints = [
            models.CheckConstraint(
                check=Q(attached_to_building=None) | Q(attached_to_contract=None),
                name="geno_share_attached_to_building_or_contract",
            )
        ]
        permissions = (
            ("canview_share", "Can view shares"),
            ("canview_share_overview", "Can see share overview"),
            ("confirm_share", "Kann Betiligungen bestätigen"),
            ("share_interest_statements", "Kann Zins-/Kontoauszüge erstellen und Zinsen anpassen"),
            ("share_mailing", "Kann Mailing zu Beteiligungen erstellen"),
        )


def get_active_shares(interest=True, date=None):
    if date is None:
        date = datetime.datetime.today()
    select = Share.objects.filter(Q(date_end=None) | Q(date_end__gt=date)).filter(date__lte=date)
    if not interest:
        return select.filter(is_interest_credit=False).filter(state="bezahlt")
    else:
        return select.filter(state="bezahlt")


DOCUMENTTYPE_NAME_CHOICES = (
    ("invoice", "invoice"),
    ("contract_check", "contract_check"),
    ("loanreminder", "loanreminder"),
    ("contract_letter", "contract_letter"),
    ("contract", "contract"),
    ("statement", "statement"),
    ("memberfee", "memberfee"),
    ("shareconfirm", "shareconfirm"),
    ("shareconfirm_req", "shareconfirm_req"),
    ("memberfinanz", "memberfinanz"),
    ("memberletter", "memberletter"),
)


class DocumentType(GenoBase):
    name = models.CharField("Name", max_length=50, unique=True, choices=DOCUMENTTYPE_NAME_CHOICES)
    description = models.CharField("Beschreibung", max_length=200)
    template = models.ForeignKey(
        "ContentTemplate",
        verbose_name="Vorlage",
        on_delete=models.CASCADE,
        help_text="OpenDocument Dokumentvorlage",
        blank=True,
        null=True,
    )
    template_file = models.CharField(
        "Dateiname Vorlage (alte Methode)", max_length=200, blank=True
    )
    active = models.BooleanField("Aktiv", default=True)

    def clean(self, *args, **kwargs):
        if not self.template_file and not self.template:
            raise ValidationError(
                "Es muss entweder eine Vorlage ausgewählt (neue Methode) "
                "oder ein Dateiname angegeben weden (alte Methode)."
            )
        if self.template and self.template.template_type != "OpenDocument":
            raise ValidationError("Es muss eine OpenDocument Dokument-Vorlage ausgewählt werden.")
        super().clean(*args, **kwargs)

    class Meta:
        verbose_name = "Dokumenttyp"
        verbose_name_plural = "Dokumenttypen"


class Document(GenoBase):
    name = models.CharField("Name", max_length=250)
    doctype = models.ForeignKey(DocumentType, verbose_name="Dokumenttyp", on_delete=models.CASCADE)
    data = models.TextField("Data")

    ## Generic relation to object
    content_type = models.ForeignKey(
        ContentType, verbose_name="Verknüpft mit", on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        date = timezone.localtime(self.ts_created).strftime("%d.%m.%Y %H:%M")
        if self.ts_created != self.ts_modified:
            date += ", geändert %s" % timezone.localtime(self.ts_modified).strftime(
                "%d.%m.%Y %H:%M"
            )
        return "%s (%s)" % (self.name, date)

    def get_object_actions(self):
        return [
            (f"/geno/documents/{self.doctype.name}/{self.pk}/download/", "Dokument neu erzeugen")
        ]

    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"
        permissions = (
            ("regenerate_document", "Can regenerate documents"),
            ("tools_odt2pdf", "Kann ODT in PDFs umwandeln"),
            ("tools_webstamp", "Kann PDFs frankieren"),
        )


PUBLICATION_TYPE_CHOICES = (
    ("internal", "Im Intranet"),
    ("public", "Öffentlich mit Link"),
)


class RegistrationEvent(GenoBase):
    name = models.CharField("Titel", max_length=255)
    description = models.TextField("Beschreibung", default="", blank=True)
    confirmation_mail_sender = models.CharField(
        "Absender Bestätigungs-Mail",
        default=get_default_email,
        max_length=50,
        blank=True,
        help_text=(
            "Leer lassen, falls kein Bestätigungsmail an die Anmeldenden gesendet werden soll."
        ),
    )
    confirmation_mail_text = models.TextField(
        "Zusatztext Bestätigungs-Mail",
        default=get_default_mail_footer,
        help_text=(
            "Dieser Text wird an den Standard-Mailtext «Hallo [name] / "
            "Du hast dich für den Anlass [titel] vom [datum] angemeldet.» angehängt"
        ),
    )
    publication_type = models.CharField(
        "Anzeigemodus", default="internal", choices=PUBLICATION_TYPE_CHOICES, max_length=30
    )
    publication_start = models.DateTimeField("Beginn Anmeldefrist", blank=True, null=True)
    publication_end = models.DateTimeField("Ende Anmeldefrist", blank=True, null=True)
    active = models.BooleanField("Aktiv", db_index=True, default=True)
    enable_notes = models.BooleanField("Kommentarfeld anzeigen?", default=False)
    enable_telephone = models.BooleanField(
        "Telefonnummer abfragen (zwingend wegen Covid-19)?", default=False
    )
    show_counter = models.BooleanField("Anzahl bisherige Anmeldungen anzeigen?", default=True)
    check1_label = models.CharField(
        "Checkbox-Frage 1",
        max_length=100,
        blank=True,
        help_text="Optionale Zusatzfragen zum ankreuzen",
    )
    check2_label = models.CharField("Checkbox-Frage 2", max_length=100, blank=True)
    check3_label = models.CharField("Checkbox-Frage 3", max_length=100, blank=True)
    check4_label = models.CharField("Checkbox-Frage 4", max_length=100, blank=True)
    check5_label = models.CharField("Checkbox-Frage 5", max_length=100, blank=True)
    text1_label = models.CharField(
        "Textfeld-Frage 1",
        max_length=100,
        blank=True,
        help_text=(
            "Optionale Textfelder, zusätzlich zu den Standardfeldern "
            "Name, Vorname, Email, Telefon, Kommentar"
        ),
    )
    text2_label = models.CharField("Textfeld-Frage 2", max_length=100, blank=True)
    text3_label = models.CharField("Textfeld-Frage 3", max_length=100, blank=True)
    text4_label = models.CharField("Textfeld-Frage 4", max_length=100, blank=True)
    text5_label = models.CharField("Textfeld-Frage 5", max_length=100, blank=True)

    class Meta:
        verbose_name = "Anmeldung-Anlass"
        verbose_name_plural = "Anmeldung-Anlässe"


class RegistrationSlot(GenoBase):
    name = models.DateTimeField(
        "Anlass/Termin", help_text="Falls keine spezifische Uhrzeit, 00:00 angeben"
    )
    alt_text = models.CharField(
        "Alternativer Text",
        max_length=100,
        blank=True,
        help_text="Falls ausgefüllt, wird anstelle des Datums dieser Text im Formular angezeigt.",
    )
    max_places = models.IntegerField(
        "Max. Anzahl Plätze",
        default=-1,
        help_text="Für unbeschränkte Anzahl -1 (minus 1) eingeben.",
    )
    event = models.ForeignKey(RegistrationEvent, verbose_name="Anlass", on_delete=models.CASCADE)
    is_backup_for = models.OneToOneField(
        "self",
        verbose_name="Ist Backup für Termin",
        help_text=(
            "Falls gesetzt, wird dieser Termin erst angeboten, wenn der hier angegebene "
            "Termin keine freien Plätze mehr hat."
        ),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="backup_slot",
    )

    def get_slot_text(self):
        if self.alt_text:
            return self.alt_text
        elif timezone.localtime(self.name).strftime("%H:%M") == "00:00":
            return timezone.localtime(self.name).strftime("%A, %d.%m.%Y")
        else:
            return timezone.localtime(self.name).strftime("%A, %d.%m.%Y %H:%M")

    def __str__(self):
        return "%s/%s" % (self.event, timezone.localtime(self.name).strftime("%d.%m.%Y %H:%M"))

    class Meta:
        verbose_name = "Anmeldung-Termin"
        verbose_name_plural = "Anmeldung-Termine"


class Registration(GenoBase):
    name = models.CharField("Nachname", max_length=30)
    first_name = models.CharField("Vorname", max_length=30)
    email = models.EmailField("Email")
    telephone = models.CharField(
        "Telefon", max_length=30, blank=True, help_text="Angabe zwingend wegen COVID-19 Massnahmen"
    )
    slot = models.ForeignKey(
        RegistrationSlot, verbose_name="Datum/Zeit Beginn", on_delete=models.CASCADE
    )
    notes = models.TextField("Kommentar", blank=True)
    check1 = models.BooleanField("Checkbox 1", default=False)
    check2 = models.BooleanField("Checkbox 2", default=False)
    check3 = models.BooleanField("Checkbox 3", default=False)
    check4 = models.BooleanField("Checkbox 4", default=False)
    check5 = models.BooleanField("Checkbox 5", default=False)
    text1 = models.CharField("Textfeld 1", max_length=100, blank=True)
    text2 = models.CharField("Textfeld 2", max_length=100, blank=True)
    text3 = models.CharField("Textfeld 3", max_length=100, blank=True)
    text4 = models.CharField("Textfeld 4", max_length=100, blank=True)
    text5 = models.CharField("Textfeld 5", max_length=100, blank=True)

    def __str__(self):
        return "%s, %s [%s]" % (self.name, self.first_name, self.slot)

    class Meta:
        verbose_name = "Anmeldung"
        verbose_name_plural = "Anmeldungen"


RENTAL_UNIT_TYPES = (
    ("Wohnung", "Wohnung"),
    ("Grosswohnung", "Grosswohnung"),
    ("Jokerzimmer", "Jokerzimmer"),
    ("Selbstausbau", "Selbstausbau"),
    ("Kellerabteil", "Kellerabteil"),
    ("Gewerbe", "Gewerbefläche"),
    ("Lager", "Lagerraum"),
    ("Hobby", "Hobbyraum"),
    ("Gemeinschaft", "Gemeinschaftsräume/Diverses"),
    ("Parkplatz", "Parkplatz"),
)


class RentalUnit(GenoBase):
    name = models.CharField("Nr.", max_length=255)
    label = models.CharField("Bezeichnung", max_length=50, blank=True)
    label_short = models.CharField("Kurzbezeichnung", blank=True, max_length=50)
    rental_type = models.CharField("Typ", max_length=50, choices=RENTAL_UNIT_TYPES)
    # building = models.CharField('Gebäude(teil)', max_length=100, blank=True)
    building = models.ForeignKey("Building", verbose_name="Liegenschaft", on_delete=models.CASCADE)
    floor = models.CharField("Stockwerk", max_length=50, blank=True)
    area = models.DecimalField(
        "Fläche (m2)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    area_balcony = models.DecimalField(
        "Balkonfläche (m2)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    area_add = models.DecimalField(
        "Zusatzfläche (m2)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    height = models.CharField("Raumhöhe (m)", max_length=10, null=True, blank=True)
    volume = models.DecimalField(
        "Volumen (m3)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    rooms = models.DecimalField(
        "Anzahl Zimmer", max_digits=5, decimal_places=1, null=True, blank=True
    )
    min_occupancy = models.DecimalField(
        "Mindestbelegung", max_digits=5, decimal_places=1, null=True, blank=True
    )
    nk = models.DecimalField(
        "Nebenkosten Akonto (Fr.)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wird bei unvermieteten Gewerberäumen auch auf der Website angezeigt.",
    )
    nk_flat = models.DecimalField(
        "Nebenkosten Pauschal (Fr.)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    nk_electricity = models.DecimalField(
        "Strompauschale (Fr.)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    rent_netto = models.DecimalField(
        "Netto-Miete (Fr.)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="exkl. NK+Strom",
    )
    rent_year = models.DecimalField(
        "Nettomiete publiziert (Fr./Jahr)",
        max_digits=11,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Diese Miete wird für Gewerberäume auf der Website angezeigt.",
    )
    depot = models.DecimalField(
        "Depot (Fr.)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    share = models.DecimalField(
        "Anteilskapital (Fr.)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    note = models.CharField("Zusatzinfo", max_length=200, blank=True)
    active = models.BooleanField("Aktiv", default=True)
    status = models.CharField("Status", default="Verfügbar", max_length=100)
    ewid = models.PositiveIntegerField("EWID", null=True, blank=True)
    internal_nr = models.PositiveIntegerField("Interne-Nummer", null=True, blank=True)
    svg_polygon = models.TextField("SVG Polygon", default="", blank=True)
    description = models.TextField("Beschreibung", default="", blank=True)
    adit_serial = models.TextField(
        "ADIT-Seriennr.",
        default="",
        blank=True,
        max_length=50,
        help_text="Mehrere Seriennr. durch Komma trennen.",
    )
    import_id = models.CharField(
        "Import-ID", max_length=255, unique=True, null=True, default=None, blank=True
    )

    @property
    @admin.display(description="Bruttomiete (Fr.)")
    def rent_total(self):
        """
        Bruttomiete inkl. NK und Strom
        """
        return (
            (self.rent_netto if self.rent_netto else Decimal(0.0))
            + (self.nk if self.nk else Decimal(0.0))
            + (self.nk_flat if self.nk_flat else Decimal(0.0))
            + (self.nk_electricity if self.nk_electricity else Decimal(0.0))
        )

    def str_short(self):
        if self.label:
            return "%s %s" % (self.name, self.label)
        else:
            return "%s %s" % (self.name, self.rental_type)

    def __str__(self):
        return "%s (%s)" % (self.str_short(), self.building)

    def get_absolute_url(self):
        return "/admin/geno/rental_unit/%i/" % self.id

    class Meta:
        unique_together = ["name", "building"]
        verbose_name = "Mietobjekt"
        verbose_name_plural = "Mietobjekte"
        ordering = ["building__name", "name"]


class Contract(GenoBase):
    main_contract = models.ForeignKey(
        "self",
        verbose_name="Hauptvertrag",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sub_contract",
    )
    contractors = models.ManyToManyField(
        Address, verbose_name="Vertragspartner", related_name="address_contracts"
    )
    main_contact = models.ForeignKey(
        Address,
        verbose_name="Kontaktperson/Hauptmieter*in",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="address_main_contracts",
    )
    children = models.ManyToManyField(
        Child, verbose_name="Kinder", blank=True, related_name="child_contracts"
    )
    rental_units = models.ManyToManyField(
        RentalUnit, verbose_name="Mietobjekt(e)", related_name="rentalunit_contracts"
    )
    CONTRACT_STATE_CHOICES = (
        ("angeboten", "angeboten"),
        ("unterzeichnet", "unterzeichnet"),
        ("gekuendigt", "gekündigt"),
        ("ungueltig", "ungültig"),
    )
    state = models.CharField("Status", max_length=50, choices=CONTRACT_STATE_CHOICES, blank=True)
    date_since = models.DateField(
        "Verhältnis seit",
        null=True,
        blank=True,
        default=None,
        help_text="Start des Mietverhältnisses (ggf. abweichend vom Vertragsbeginn). Wird in keiner Berechnung verwendet.",
    )
    date = models.DateField("Vertragsbeginn")
    date_end = models.DateField("Vertragsende", null=True, blank=True, default=None)
    billing_date_start = models.DateField(
        "Sollstellung ab",
        null=True,
        blank=True,
        default=None,
        help_text="Leer lassen, falls ab Vertragsbeginn.",
    )
    billing_date_end = models.DateField(
        "Sollstellung bis",
        null=True,
        blank=True,
        default=None,
        help_text="Leer lassen, falls bis Vertragsende.",
    )
    note = models.CharField("Zusatzinfo", max_length=200, blank=True)
    import_id = models.CharField(
        "Import-ID", max_length=255, unique=True, null=True, default=None, blank=True
    )
    rent_reduction = models.DecimalField(
        "Mietzinsreduktion Nettomiete (Fr./Monat)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    rent_reservation = models.DecimalField(
        "Mietzinsvorbehalt Nettomiete (Fr./Monat)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    share_reduction = models.DecimalField(
        "Reduktion Pflichtanteilkapital (Fr.)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    CONTRACT_QRBILL_CHOICES = (
        ("none", "Keine Rechnung per Mail verschicken"),
        ("only_next", "Nur nächste Rechnung per Mail verschicken"),
        ("always", "Rechung immer per Mail verschicken"),
    )
    send_qrbill = models.CharField(
        "QR-Rechnung", max_length=50, choices=CONTRACT_QRBILL_CHOICES, default="only_next"
    )
    ## TODO: Billing and Debitoren for linked contracts.
    billing_contract = models.ForeignKey(
        "Contract",
        verbose_name="In Inkasso von diesem Vertrag integrieren",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contract_billing_contracts",
    )
    bankaccount = models.ForeignKey(
        BankAccount,
        verbose_name="Kontoverbindung",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Z.B. für Rückzahlung Nebenkosten",
    )

    ## Reverse relation to Documents
    documents = GenericRelation("Document", related_query_name="contracts")

    def __str__(self):
        contractors = []
        for c in self.contractors.all():
            if c.organization:
                name_str = "%s, %s %s" % (c.organization, c.first_name, c.name)
            else:
                name_str = "%s %s" % (c.first_name, c.name)
            if c == self.main_contact:
                contractors.insert(0, name_str)
            else:
                contractors.append(name_str)

        contractors_str = "/".join(contractors)
        if len(contractors_str) > 80:
            contractors_str = contractors_str[0:80] + "..."

        return "%s [%s]" % (self.list_rental_units(), contractors_str)

    def get_contact_address(self):
        if self.main_contact:
            return self.main_contact
        else:
            return self.contractors.first()

    def get_contract_label(self):
        if self.main_contact:
            address = self.main_contact
            if address.organization:
                return "%05d, %s" % (self.id, address.organization)
            else:
                return "%05d, %s %s" % (self.id, address.first_name, address.name)
        else:
            names = []
            for a in self.contractors.all():
                if a.organization:
                    names.append(a.organization)
                else:
                    names.append("%s %s" % (a.first_name, a.name))
            return "%05d, %s" % (self.id, "/".join(names))

    def get_building_label(self):
        ru = self.rental_units.first()
        return ru.building.name if ru else None

    def list_rental_units(self, short=False, exclude_minor=False, as_list=False):
        units = []
        if exclude_minor:
            rus = self.rental_units.exclude(rental_type="Kellerabteil")
        else:
            rus = self.rental_units.all()
        for u in rus.order_by("name"):
            if short:
                units.append("%s" % u.name)
            else:
                units.append("%s" % u)
        if as_list:
            return units
        else:
            return "/".join(units)

    def get_object_actions(self):
        actions = []
        if not self.main_contract:
            # No invoices for sub-contracts
            actions.append(
                (
                    "/geno/invoice/download/contract/%s/" % (self.pk),
                    "Mietzinsrechnung herunterladen, aktueller Monat",
                    "Es wird nur das PDF erzeugt, nicht gebucht!",
                )
            )
            actions.append(
                (
                    "/geno/invoice/download/contract/%s/?date=last_month" % (self.pk),
                    "Mietzinsrechnung herunterladen, letzter Monat",
                    "Es wird nur das PDF erzeugt, nicht gebucht!",
                )
            )
            actions.append(
                (
                    "/geno/invoice/download/contract/%s/?date=next_month" % (self.pk),
                    "Mietzinsrechnung herunterladen, nächster Monat",
                    "Es wird nur das PDF erzeugt, nicht gebucht!",
                )
            )
        for dt in DocumentType.objects.filter(active=True).filter(name__startswith="contract"):
            actions.append(
                (
                    "/geno/documents/%s/%s/create/" % (dt.name, self.pk),
                    "%s erzeugen" % (dt.description),
                )
            )
        return actions

    def save_as_copy(self):
        old_contractors = self.contractors.all()
        old_children = self.children.all()
        old_rental_units = self.rental_units.all()
        self.import_id = None
        super().save_as_copy()
        self.contractors.set(old_contractors)
        self.children.set(old_children)
        self.rental_units.set(old_rental_units)

    class Meta:
        verbose_name = "Vertrag"
        verbose_name_plural = "Verträge"
        ordering = ("date_end", "-date")
        permissions = (
            (
                "rental_contracts",
                "Kann Mietverträge erstellen, NK-Abrechung, Pflichtanteile überprüfen",
            ),
            (
                "rental_objects",
                "Kann Mieter-/Objektespiegel erstellen und Mietobjekt-Dokumente erstellen",
            ),
        )


def get_active_contracts(date=None, pre_select=None, include_subcontracts=False):
    if date is None:
        date = datetime.date.today()
        if date < datetime.date(2021, 12, 1):
            date = datetime.date(2021, 12, 1)
    if not pre_select:
        pre_select = Contract.objects.all()
    select = pre_select.filter(Q(date_end=None) | Q(date_end__gt=date)).filter(date__lte=date)
    if include_subcontracts:
        return select
    else:
        return select.filter(main_contract__isnull=True)


INVOICE_OBJECT_TYPE_CHOICES = (
    ("Address", "Adresse"),
    ("Contract", "Vertrag"),
)


class InvoiceCategory(GenoBase):
    name = models.CharField("Name", max_length=50)
    reference_id = models.SmallIntegerField(
        "Kategorie-Code für Referenznummer",
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(89)],
    )
    note = models.CharField("Bemerkung", max_length=255, blank=True)
    linked_object_type = models.CharField(
        "Rechnung verknüpft mit",
        max_length=50,
        choices=INVOICE_OBJECT_TYPE_CHOICES,
        default="Address",
    )
    income_account = models.CharField("Kontonummer Ertrag", max_length=50, default="3000")
    income_account_building_based = models.BooleanField(
        "Ertragskonto liegenschaftsabhängig",
        default=False,
        help_text="Liegenschafts-Postfix (bspw. 81) wird genutzt um Kontonummer zu bilden. Es resultiert bspw. 300081",
    )
    receivables_account = models.CharField(
        "Kontonummer Forderungen", max_length=50, default="1102"
    )
    receivables_account_building_based = models.BooleanField(
        "Forderungskonto liegenschaftsabhängig",
        default=False,
        help_text="Liegenschafts-Postfix (bspw. 81) wird genutzt um Kontonummer zu bilden. Es resultiert bspw. 110281",
    )
    manual_allowed = models.BooleanField("Manuelle Rechnungsstellung erlaubt", default=False)
    email_template = models.ForeignKey(
        "ContentTemplate",
        verbose_name="Email-Vorlage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    active = models.BooleanField("Aktiv", default=True)

    def clean(self, *args, **kwargs):
        if self.email_template and self.email_template.template_type != "Email":
            raise ValidationError("Die ausgewählte Vorlage ist keine Email-Vorlage.")
        super().clean(*args, **kwargs)

    class Meta:
        verbose_name = "Rechnungstyp"
        verbose_name_plural = "Rechnungstypen"
        constraints = [
            models.CheckConstraint(
                name="geno_invoicecategory_reference_id_range",
                check=Q(reference_id__gt=0) & Q(reference_id__lt=90),
            )
        ]


INVOICE_TYPE_CHOICES = (
    ("Invoice", "Rechnung"),
    ("Payment", "Einzahlung"),
)


class Invoice(GenoBase):
    name = models.CharField("Beschreibung", max_length=1000)
    person = models.ForeignKey(
        Address,
        verbose_name="Person/Organisation",
        on_delete=models.CASCADE,
        db_index=True,
        null=True,
        blank=True,
    )
    invoice_type = models.CharField(
        "Typ", max_length=50, choices=INVOICE_TYPE_CHOICES, default="Invoice", db_index=True
    )
    invoice_category = models.ForeignKey(
        InvoiceCategory, verbose_name="Kategorie", on_delete=models.CASCADE, db_index=True
    )
    date = models.DateField("Datum")
    amount = models.DecimalField("Betrag (Fr.)", max_digits=10, decimal_places=2)
    consolidated = models.BooleanField("Konsolidiert", default=False, db_index=True)

    ## Sepa
    transaction_id = models.CharField("Transaktions-ID", max_length=150, db_index=True, blank=True)
    reference_nr = models.CharField("Referenz-Nr.", max_length=50, db_index=True, blank=True)
    additional_info = models.CharField("Zusatzinfos", max_length=255, blank=True)

    ## Invoice specific fields
    year = models.IntegerField("Rechnung für Jahr", null=True, blank=True, db_index=True)
    month = models.IntegerField("Rechnung für Monat", null=True, blank=True, db_index=True)
    is_additional_invoice = models.BooleanField(
        "Zusatzrechnung zu einer Hauptrechnung?", default=False, db_index=True
    )
    contract = models.ForeignKey(
        Contract,
        verbose_name="Vertrag",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_index=True,
    )
    active = models.BooleanField("Aktiv", default=True, db_index=True)

    ## Financial accounting references
    fin_transaction_ref = models.CharField(
        "Transaktions-Referenz Buchhaltung", max_length=1024, blank=True
    )
    fin_account = models.CharField("Konto Buchhaltung", max_length=50, blank=True)
    fin_account_receivables = models.CharField(
        "Konto Forderungen Buchhaltung", max_length=50, blank=True
    )

    def __str__(self):
        if self.person:
            namestr = "%s" % self.person
        else:
            namestr = "%s" % self.contract
        return "%s/%s %s CHF %.2f" % (namestr, self.name, self.invoice_type, self.amount)

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"
        constraints = [
            models.CheckConstraint(
                check=(Q(person__isnull=True) & Q(contract__isnull=False))
                | (Q(person__isnull=False) & Q(contract__isnull=True)),
                name="either_person_or_contract",
            ),
        ]


@receiver(pre_delete, sender=Invoice)
def _delete_invoice_pre(sender, instance, *args, **kwargs):
    from .billing import delete_invoice_transaction

    ret = delete_invoice_transaction(instance)
    if ret:
        raise Exception(ret)


class LookupTable(GenoBase):
    name = models.CharField("Key", max_length=255)
    lookup_type = models.CharField("Lookup type", max_length=20)
    value = models.CharField("Value", max_length=1000)


class GenericAttribute(GenoBase):
    name = models.CharField("Name", max_length=250, db_index=True)
    date = models.DateField("Datum", null=True, blank=True)
    value = models.CharField("Wert", max_length=100)

    ## Generic relation to object
    content_type = models.ForeignKey(
        ContentType, verbose_name="Verknüpft mit", on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        date_str = ""
        if self.date:
            date_str = " (%s)" % self.date.strftime("%d.%m.%Y")
        return "%s [%s - %s]%s" % (self.content_object, self.name, self.value, date_str)

    class Meta:
        verbose_name = "Attribut"
        verbose_name_plural = "Attribute"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "content_type", "object_id"],
                name="unique_content_object_attribute_name",
            ),
        ]


#        permissions = (
#            ("regenerate_document", "Can regenerate documents"),
#        )


class ContentTemplateOptionType(GenoBase):
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.CharField("Bezeichung", max_length=200)

    class Meta:
        verbose_name = "Vorlagenoptionentyp"
        verbose_name_plural = "Vorlagenoptionentypen"

    def __str__(self):
        return self.description


class ContentTemplateOption(GenoBase):
    name = models.ForeignKey(
        ContentTemplateOptionType, verbose_name="Variable", on_delete=models.CASCADE
    )
    value = models.CharField("Wert", max_length=100, blank=True)

    class Meta:
        verbose_name = "Vorlagenoption"
        verbose_name_plural = "Vorlagenoptionen"

    def __str__(self):
        desc = f"{self.name.description}"
        if self.value:
            desc = f"{desc}: {self.value}"
        if self.comment:
            desc = f"{desc} ({self.comment})"
        return desc


CONTENTTEMPLATE_TYPE_CHOICES = (
    ("Email", "Email-Vorlage"),
    ("Email-Subject", "Email-Betreff"),
    ("Email-Sender", "Email-Absender"),
    ("OpenDocument", "Dokument-Vorlage (OpenDocument-Datei mit Variablen)"),
    ("File", "Datei"),
)


class ContentTemplate(GenoBase):
    name = models.CharField("Bezeichnung", max_length=255)
    template_type = models.CharField(
        "Typ", max_length=50, choices=CONTENTTEMPLATE_TYPE_CHOICES, default="Email"
    )
    text = models.TextField(
        "Text", default="", blank=True, help_text="Für Dokument-Vorlagen leer lassen."
    )
    file = FilerFileField(
        verbose_name="Datei",
        null=True,
        blank=True,
        help_text="Für Text-Vorlagen leer lassen.",
        related_name="file_contenttemplate",
        on_delete=models.CASCADE,
    )
    manual_creation_allowed = models.BooleanField(
        "Manuelle Dokumenterstellung erlaubt?", default=True
    )
    template_context = models.ManyToManyField(
        ContentTemplateOption,
        verbose_name="Kontext-Optionen",
        related_name="contenttemplates",
        blank=True,
    )
    active = models.BooleanField("Aktiv", db_index=True, default=True)

    def clean(self, *args, **kwargs):
        if self.template_type in ("OpenDocument", "File"):
            if self.text or not self.file:
                raise ValidationError(
                    "Für Dokument-Vorlagen muss eine Datei ausgewählt werden "
                    "und das Text-Feld muss leer bleiben."
                )
        else:
            if not self.text or self.file:
                raise ValidationError(
                    "Für Text-Vorlagen muss ein Text eingegeben werden "
                    "und das Datei-Feld muss leer bleiben."
                )
        super().clean(*args, **kwargs)

    def get_template(self):
        if self.template_type == "Email":
            return Template("%s%s%s" % ("{% autoescape off %}", self.text, "{% endautoescape %}"))
        elif self.template_type in ("Email-Subject", "Email-Sender"):
            return Template(self.text)
        else:
            return None

    def save_as_copy(self):
        old_template_context = self.template_context.all()
        super().save_as_copy()
        self.template_context.set(old_template_context)

    class Meta:
        verbose_name = "Vorlage"
        verbose_name_plural = "Vorlagen"

    def __str__(self):
        return f"{self.template_type}: {self.name}"


class TenantsView(GenoBase):
    bu_name = models.CharField("Liegenschaft", max_length=100, unique=True)
    ru_name = models.CharField("Mietobjekt Nr.", max_length=255)
    ru_label = models.CharField("Mietobjekt Bezeichnung", max_length=50, blank=True)
    ru_type = models.CharField("Mietobjekt Typ", max_length=50, choices=RENTAL_UNIT_TYPES)
    ru_floor = models.CharField("Mietobjekt Stockwerk", max_length=50, blank=True)
    ru_rooms = models.DecimalField(
        "Mietobjekt Anzahl Zimmer", max_digits=5, decimal_places=1, null=True, blank=True
    )
    ru_area = models.DecimalField(
        "Mietobjekt Fläche (m2)", max_digits=10, decimal_places=2, null=True, blank=True
    )

    organization = models.CharField("Mieter*in Organisation", max_length=100, blank=True)
    ad_name = models.CharField("Mieter*in Nachname", max_length=30)
    ad_first_name = models.CharField("Mieter*in Vorname", max_length=30)
    ad_title = models.CharField("Mieter*in Titel", max_length=50, blank=True)
    ad_email = models.CharField("Mieter*in Email", max_length=100, blank=True)
    c_ischild = models.BooleanField("Ist Kind", default=False)
    c_age = models.IntegerField("Alter Kind", null=True, blank=True)
    presence = models.CharField("Anwesenheit Kind", max_length=50, blank=True)
    ad_date_birth = models.DateField("Mieter*in Geburtsdatum", null=True, blank=True)
    ad_city = models.CharField("Mieter*in Ort", max_length=100, blank=True)
    ad_street = models.CharField("Mieter*in Strasse", max_length=100, blank=True)
    ad_tel1 = models.CharField("Mieter*in Telefon 1", max_length=30, blank=True)
    ad_tel2 = models.CharField("Mieter*in Telefon 2", max_length=30, blank=True)
    p_hometown = models.CharField("Mieter*in Heimatort", max_length=100, blank=True)
    p_occupation = models.CharField("Mieter*in Beruf", max_length=100, blank=True)
    p_membership_date = models.DateField("Mieter*in Mitglied seit", null=True, blank=True)
    c_issubcontract = models.BooleanField("Ist Untervertrag", default=False)

    building = models.ForeignKey(
        "Building", verbose_name="Liegenschaft", on_delete=models.DO_NOTHING
    )
    rental_unit = models.ForeignKey(
        "RentalUnit", verbose_name="Mietobjekt", on_delete=models.DO_NOTHING
    )
    contract = models.ForeignKey(Contract, verbose_name="Vertrag", on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "geno_TenantsView"
        managed = False
        verbose_name = "Mieter:innenspiegel"
        verbose_name_plural = "Mieter:innenspiegel"
        ordering = ["bu_name", "ru_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["building", "rental_unit", "contract"],
                name="unique_tenantsview_entry",
            ),
        ]
