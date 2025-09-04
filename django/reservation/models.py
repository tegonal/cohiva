import logging
from datetime import timedelta
from decimal import Decimal

import select2.fields
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from cohiva.utils.settings import get_default_app_sender
from geno.models import Address, ContentTemplate, GenoBase, RentalUnit

logger = logging.getLogger("reservation")


RESERVATION_STATE_CHOICES = (
    ("new", "Neu"),
    ("approved", "Bestätigt"),
    ("cancelled", "Gecancelt"),
    ("deleted", "Gelöscht"),
)

RESERVATIONTYPE_ROLE_CHOICES = (
    ("user", "Alle aktiven Benutzer:innen"),
    ("member", "Alle Mitglieder"),
    ("renter", "Alle Mieter:innen"),
    ("community", "Alle in der Siedlung"),
    ## TODO?: Add tenants per building dynamically...
    ## and/or allow more dynamic group configuration: Add lists of groups here.
    ## And make groups either manually or automatically (renters, tenants...)
)


class ReservationType(GenoBase):
    name = models.CharField("Reservationstyp", max_length=50, unique=True)
    fixed_time = models.BooleanField("Fixe Uhrzeiten", default=False)
    default_time_start = models.TimeField("Standardzeit Beginn", default="10:00")
    default_time_end = models.TimeField("Standardzeit Ende", default="12:00")
    summary_required = models.BooleanField(
        "Text mit Anlass/Grund der Reservation benötigt?", default=False
    )
    required_role = models.CharField(
        "Verfügbar für", default="renter", choices=RESERVATIONTYPE_ROLE_CHOICES, max_length=30
    )
    confirmation_email_template = select2.fields.ForeignKey(
        ContentTemplate,
        verbose_name="Vorlage Bestätigungs-Email",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Leer lassen falls keine Bestätigung gesendet werden soll.",
    )
    confirmation_email_sender = models.CharField(
        "Absender Bestätigungs-Email",
        max_length=100,
        default=get_default_app_sender,
        help_text="Format: '\"Vorname Name\" &lt;email@example.com&gt;'",
    )
    color = models.CharField(
        "Kalender-Farbe", max_length=7, default="#7d7d78", help_text='Format: "#rrggbb"'
    )
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Reservationstyp"
        verbose_name_plural = "Reservationstypen"


class ReservationUsageType(GenoBase):
    name = models.CharField("Name", max_length=50, unique=True)
    label = models.CharField("Bezeichnung", max_length=50)

    class Meta:
        verbose_name = "Nutzungsart"
        verbose_name_plural = "Nutzungsarten"


RESERVATION_TIME_UNIT_CHOICES = (
    ("hours", "Stunden"),
    ("days", "Tage"),
)
RESERVATION_COST_TYPE_CHOICES = (
    ("fixed", "Fixpreis"),
    ("per_time_unit", "pro Zeiteinheit"),
)


class ReservationPrice(GenoBase):
    name = models.CharField("Bezeichnung", max_length=50)
    usage_type = select2.fields.ForeignKey(
        ReservationUsageType, verbose_name="Reservations Nutzungsart", on_delete=models.CASCADE
    )
    priority = models.IntegerField(
        "Priorität",
        default=1,
        help_text="Es wird der erste Preis angewendet, auf welchen die Dauer der Reservation zutrifft (in aufteigender Prioritäts-Reihenfolge)",
    )
    time_unit = models.CharField(
        "Zeit-Einheit", max_length=20, choices=RESERVATION_TIME_UNIT_CHOICES, default="hours"
    )
    duration_min = models.FloatField(
        "Min. Dauer",
        help_text="Trifft auf Reservationen zu, deren Dauer mindestens diesem Wert entspricht.",
        default=0,
        null=False,
    )
    duration_max = models.FloatField(
        "Max. Dauer",
        help_text="Trifft auf Reservationen zu, deren Dauer maximal diesem Wert entspricht.",
        default=9999,
        null=False,
    )
    cost = models.DecimalField("Preis", max_digits=7, decimal_places=2, default=Decimal(0))
    cost_type = models.CharField(
        "Preis-Modus",
        max_length=20,
        choices=RESERVATION_COST_TYPE_CHOICES,
        default="per_time_unit",
    )

    class Meta:
        unique_together = ["usage_type", "priority"]
        verbose_name = "Reservationstarif"
        verbose_name_plural = "Reservationstarife"


class ReservationObject(GenoBase):
    name = models.CharField("Name", max_length=80)
    reservation_type = select2.fields.ForeignKey(
        ReservationType, verbose_name="Reservationstyp", on_delete=models.CASCADE
    )
    short_description = models.CharField(
        "Kurzbeschreibung", max_length=300, default="", blank=True
    )
    description = models.TextField("Beschreibung", default="", blank=True)
    image = models.ImageField("Bild", blank=True, default="", upload_to="reservation/images/")
    ## cost is deprecated: Use ReservationUsageType with ReservationPrice now!
    cost = models.DecimalField(
        "Preis (ALT)",
        max_digits=7,
        decimal_places=2,
        default=Decimal(0),
        help_text="Sollte nicht mehr verwendet werden. Neu wird der Preis über Reservationstarife via Nutzungsarten festgelegt.",
    )
    usage_types = models.ManyToManyField(
        ReservationUsageType,
        verbose_name="Nutzungsarten",
        related_name="reservationusagetype_reservationobjects",
        blank=True,
    )

    def get_blocking_reservations(self, date_start, date_end=None):
        if not date_end:
            date_end = date_start + timedelta(minutes=5)
        # print("get_blocking_reservation() query: %s - %s" % (date_start,date_end))
        blocking = (
            Reservation.objects.filter(name=self)
            .filter(Q(state="new") | Q(state="approved"))
            .exclude(date_start__gte=date_end)
            .exclude(date_end__lte=date_start)
            .order_by("date_start")
        )
        # for r in blocking:
        #    print("Blocking res: %s %s  [%s - %s]" % (r,r.id,r.date_start,r.date_end))
        return blocking

    def update_reservation_blockers(self, rule_change=False):
        now = timezone.localtime(timezone.now())
        past_cutoff_date = now - timedelta(days=30)
        future_cutoff_date = now + timedelta(days=3 * 365)
        ## 1) If rules have changed: Delete all blockers, else delete all blockers older than 1 month
        if rule_change:
            (del_count, del_dict) = (
                Reservation.objects.filter(name=self).filter(is_auto_blocker=True).delete()
            )
        else:
            (del_count, del_list) = (
                Reservation.objects.filter(name=self)
                .filter(is_auto_blocker=True)
                .filter(date_end__lt=past_cutoff_date)
                .delete()
            )
        if del_count:
            # print("Deleted %s reservation blockers for reservation object %s (id %s)" % (del_count, self.name, self.id))
            logger.info(
                "Deleted %s reservation blockers for reservation object %s (id %s)"
                % (del_count, self.name, self.id)
            )

        ## 2) Create new blockers up to 3 years in the future that don't exist yet.
        ## TODO: Move rule config to individual ReservationObject instead of hard-coded.
        ## TODO: Add more rule types (daily, bi-weekly, monthly, first/last weekday of month, yearly, ...?)
        blocker_rules = []
        for ruleconf in settings.RESERVATION_BLOCKER_RULES:
            if ruleconf["object"] == self.name:
                adr = Address.objects.get(**ruleconf["contact"])
                rule = ruleconf["rule"].copy()
                rule["contact"] = adr
                blocker_rules.append(rule)
        if not blocker_rules:
            return
        try:
            last_blocker = (
                Reservation.objects.filter(name=self)
                .filter(is_auto_blocker=True)
                .latest("date_start")
            )
            cur = timezone.localtime(last_blocker.date_start) + timedelta(days=1)
            # print("Start adding blockers from last blocker at %s" % last_blocker.date_start)
        except Reservation.DoesNotExist:
            cur = past_cutoff_date
            # print("No existing blockers -> start adding blockers from NOW")
        while cur < future_cutoff_date:
            self.apply_reservation_blocker_rules(cur, blocker_rules)
            cur += timedelta(days=1)

    def apply_reservation_blocker_rules(self, date, rules):
        for rule in rules:
            if rule["type"] == "weekly" and date.weekday() in rule["weekdays"]:
                start_time = rule["time_start"].split(":")
                end_time = rule["time_end"].split(":")
                start = date.replace(
                    hour=int(start_time[0]), minute=int(start_time[1]), second=0, microsecond=0
                )
                end = date.replace(
                    hour=int(end_time[0]), minute=int(end_time[1]), second=0, microsecond=0
                )
                ## TODO: Check and warn if an overlapping reservation exists already.
                res = Reservation(
                    name=self,
                    date_start=start,
                    date_end=end,
                    is_auto_blocker=True,
                    contact=rule["contact"],
                    summary=rule["summary"],
                )
                res.save()
                # print("Added reservation blocker for %s: %s - %s (id %s)" % (self.name, res.date_start.strftime("%d.%m.%Y %H:%M"), res.date_end.strftime("%d.%m.%Y %H:%M"), res.id))
                logger.info(
                    "Added reservation blocker for %s: %s - %s (id %s)"
                    % (
                        self.name,
                        res.date_start.strftime("%d.%m.%Y %H:%M"),
                        res.date_end.strftime("%d.%m.%Y %H:%M"),
                        res.id,
                    )
                )

    def save_as_copy(self):
        old_usage_types = self.usage_types.all()
        super().save_as_copy()
        self.usage_types.set(old_usage_types)

    class Meta:
        unique_together = ["name", "reservation_type"]
        verbose_name = "Reservationsobjekt"
        verbose_name_plural = "Reservationsobjekte"


class Reservation(GenoBase):
    name = select2.fields.ForeignKey(
        ReservationObject, verbose_name="Objekt", on_delete=models.CASCADE
    )
    contact = select2.fields.ForeignKey(
        Address, verbose_name="Kontaktperson", on_delete=models.CASCADE
    )
    contact_text = models.CharField(
        "Kontaktperson (alternativer Text)", max_length=200, blank=True
    )
    flink_user_id = models.IntegerField(
        "Flink UserID", null=True
    )  ## Warning: Does not need to match contact!
    date_start = models.DateTimeField("Beginn Reservation")
    date_end = models.DateTimeField("Ende Reservation")
    summary = models.CharField(
        "Beschreibung",
        default="",
        blank=True,
        max_length=120,
        help_text="Kurze Beschreibung des Anlasses/Grund der Reservation",
    )
    usage_type = select2.fields.ForeignKey(
        ReservationUsageType,
        verbose_name="Nutzungsart",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    state = models.CharField(
        "Status", default="new", choices=RESERVATION_STATE_CHOICES, max_length=30, db_index=True
    )
    key_number = models.CharField(
        "Schlüsselnr.",
        default="",
        blank=True,
        max_length=10,
        help_text="Nummer des ausgegebenen Schlüssels.",
    )
    key_back = models.BooleanField(
        "Zurück?", default=False, help_text="Ankreuzen wenn der Schlüssel zurückgegeben wurde."
    )
    billed = models.BooleanField(
        "Verrechnet?",
        default=False,
        help_text="Ankreuzen wenn für die Reservation eine Rechnung gestellt wurde.",
    )
    remark = models.TextField("Bemerkungen", default="", blank=True)
    additional_information = models.TextField("Zusatzinfos", default="", blank=True)
    is_auto_blocker = models.BooleanField(
        "Automatisch eingefügter Reservations-Blocker", default=False
    )

    flink_id = models.CharField(
        "Flink reservation ID",
        max_length=20,
        unique=True,
        null=True,
        default=None,
        blank=True,
        db_index=True,
    )

    def can_edit(self):
        return self.date_start > timezone.now()

    def clean(self, *args, **kwargs):
        if (
            self.state in ("new", "approved")
            and hasattr(self, "name")
            and self.date_start
            and self.date_end
        ):
            ## Check if dates are not overlapping with another reservation
            for r in self.name.get_blocking_reservations(self.date_start, self.date_end):
                if r != self:
                    raise ValidationError(
                        "Es gibt bereits eine Reservation in diesem Zeitfenster: %s, %s - %s (id=%s)"
                        % (
                            r.contact,
                            timezone.localtime(r.date_start).strftime("%d.%m.%Y %H:%M"),
                            timezone.localtime(r.date_end).strftime("%d.%m.%Y %H:%M"),
                            r.id,
                        )
                    )
        super().clean(*args, **kwargs)

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservationen"
        ordering = ["-date_start"]


class ReportType(GenoBase):
    name = models.CharField("Meldungstyp", max_length=50, unique=True)

    class Meta:
        verbose_name = "Meldungstyp"
        verbose_name_plural = "Meldungstypen"


class ReportCategory(GenoBase):
    name = models.CharField("Kategorie", max_length=50)
    report_type = select2.fields.ForeignKey(
        ReportType, verbose_name="Meldungstyp", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ["name", "report_type"]
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"


REPORT_STATE_CHOICES = (
    ("new", "Neu"),
    ("open", "Offen"),
    ("closed", "Erledigt"),
    ("invalid", "Ungültig"),
    ("deleted", "Gelöscht"),
)


class Report(GenoBase):
    name = models.CharField("Betreff", max_length=100)
    report_type = select2.fields.ForeignKey(
        ReportType, verbose_name="Meldungstyp", on_delete=models.CASCADE
    )
    category = select2.fields.ForeignKey(
        ReportCategory, verbose_name="Kategorie", on_delete=models.CASCADE
    )
    rental_unit = select2.fields.ForeignKey(
        RentalUnit, verbose_name="Mietobjekt", on_delete=models.CASCADE, blank=True, null=True
    )
    contact = select2.fields.ForeignKey(
        Address, verbose_name="Kontaktperson", on_delete=models.CASCADE, blank=True, null=True
    )
    contact_text = models.CharField("Erreichbarkeit", max_length=300, blank=True)
    text = models.TextField("Beschreibung", default="")
    report_date = models.DateTimeField("Meldungsdatum")
    status_date = models.DateTimeField("Statusdatum")
    status = models.CharField(
        "Status", default="new", choices=REPORT_STATE_CHOICES, max_length=30, db_index=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_status = self.status

    def save(self, **kwargs):
        if self._old_status != self.status or not self.status_date:
            self.status_date = timezone.now()
            if (
                update_fields := kwargs.get("update_fields")
            ) is not None and "status" in update_fields:
                kwargs["update_fields"] = {"status_date"}.union(update_fields)
        super().save(**kwargs)

    def __str__(self):
        if self.id:
            return "%s-%s" % (self.id, self.name)
        else:
            return self.name

    class Meta:
        verbose_name = "Meldung"
        verbose_name_plural = "Meldungen"


def report_picture_path(instance, filename):
    prefix = ""
    if settings.DEBUG:
        prefix = "TEST_"
    return "report/images/%s%s_%s" % (prefix, instance.name, filename)


class ReportPicture(GenoBase):
    name = models.CharField("Name", max_length=100)
    image = models.ImageField("Bild", upload_to=report_picture_path)
    report = select2.fields.ForeignKey(Report, verbose_name="Meldung", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["image", "report"]
        verbose_name = "Meldungsbild"
        verbose_name_plural = "Meldungsbilder"


class ReportLogEntry(GenoBase):
    name = select2.fields.ForeignKey(Report, verbose_name="Meldung", on_delete=models.CASCADE)
    text = models.TextField("Text")
    user = select2.fields.ForeignKey(
        User, verbose_name="Autor:in", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = "Logbucheintrag"
        verbose_name_plural = "Logbucheinträge"

    def __str__(self):
        if self.name:
            report_str = "Meldung %s" % self.name.id
        else:
            report_str = "Meldung"
        if self.ts_modified:
            return "%s - Log %s - %s" % (
                report_str,
                timezone.localtime(self.ts_modified).strftime("%d.%m.%Y %H:%M"),
                self.user,
            )
        else:
            return "%s - Log - %s" % (report_str, self.user)
