from geno.models import ContentTemplate
from reservation.models import (
    ReservationObject,
    ReservationPrice,
    ReservationType,
    ReservationUsageType,
)


def create_reservationtypes(cls):
    cls.reservationtypes = {}

    confirmation_template = ContentTemplate.objects.create(
        name="Confirmation-Email-Text",
        template_type="Email",
        text="{{anrede}}\n\nReservations-Bestätigung:\n\nBezeichnung: {{reservation_object}}\nVon: {{reservation_from}}\nBis: {{reservation_to}}\nReservationsnummer: {{reservation_id}}",
    )

    rt = ReservationType.objects.create(
        name="Gästezimmer",
        fixed_time=True,
        default_time_start="12:00",
        default_time_end="14:00",
        required_role="renter",
        confirmation_email_template=confirmation_template,
    )
    cls.reservationtypes["Gästezimmer"] = rt

    rt = ReservationType.objects.create(name="Werkstatt", required_role="community")
    cls.reservationtypes["Werkstatt"] = rt

    rt = ReservationType.objects.create(
        name="Dachküche", required_role="member", summary_required=True
    )
    cls.reservationtypes["Dachküche"] = rt

    rt = ReservationType.objects.create(
        name="Sitzungszimmer", required_role="user", summary_required=True
    )
    cls.reservationtypes["Sitzungszimmer"] = rt


def create_usagetypes(cls):
    cls.usagetypes = {}

    cls.usagetypes["Gästezimmer Standard"] = ReservationUsageType.objects.create(
        name="Gästezimmer Standard", label="Standardtarif"
    )
    ReservationPrice.objects.create(
        name="Erste drei Tage gratis",
        usage_type=cls.usagetypes["Gästezimmer Standard"],
        priority=1,
        time_unit="days",
        duration_min=0.0,
        duration_max=3.0,
        cost=0.00,
        cost_type="per_time_unit",
    )
    ReservationPrice.objects.create(
        name="Ab 4. Tag",
        usage_type=cls.usagetypes["Gästezimmer Standard"],
        priority=2,
        time_unit="days",
        duration_min=3.0,
        duration_max=9999.0,
        cost=17.00,
        cost_type="per_time_unit",
    )

    cls.usagetypes["Sitzungszimmer kostenlos"] = ReservationUsageType.objects.create(
        name="Sitzungszimmer kostenlos", label="Eigene Nutzung"
    )
    ReservationPrice.objects.create(
        name="Kostenlos",
        usage_type=cls.usagetypes["Sitzungszimmer kostenlos"],
        priority=1,
        time_unit="hours",
        duration_min=0.0,
        duration_max=9999.0,
        cost=0.00,
        cost_type="fixed",
    )

    cls.usagetypes["Sitzungszimmer intern"] = ReservationUsageType.objects.create(
        name="Sitzungszimmer intern", label="Interne Nutzung"
    )
    ReservationPrice.objects.create(
        name="Halbtag",
        usage_type=cls.usagetypes["Sitzungszimmer intern"],
        priority=1,
        time_unit="hours",
        duration_min=0.0,
        duration_max=5.0,
        cost=15.00,
        cost_type="fixed",
    )
    ReservationPrice.objects.create(
        name="Zwei Halbtage",
        usage_type=cls.usagetypes["Sitzungszimmer intern"],
        priority=2,
        time_unit="hours",
        duration_min=5.0,
        duration_max=10.0,
        cost=30.00,
        cost_type="fixed",
    )
    ReservationPrice.objects.create(
        name="Ganzer Tag inkl. Abend",
        usage_type=cls.usagetypes["Sitzungszimmer intern"],
        priority=3,
        time_unit="hours",
        duration_min=10.0,
        duration_max=24.0,
        cost=40.00,
        cost_type="fixed",
    )

    cls.usagetypes["Sitzungszimmer extern"] = ReservationUsageType.objects.create(
        name="Sitzungszimmer extern", label="Externe Nutzung"
    )
    ReservationPrice.objects.create(
        name="Halbtag",
        usage_type=cls.usagetypes["Sitzungszimmer extern"],
        priority=1,
        time_unit="hours",
        duration_min=0.0,
        duration_max=5.0,
        cost=50.00,
        cost_type="fixed",
    )
    ReservationPrice.objects.create(
        name="Zwei Halbtage",
        usage_type=cls.usagetypes["Sitzungszimmer extern"],
        priority=2,
        time_unit="hours",
        duration_min=5.0,
        duration_max=10.0,
        cost=100.00,
        cost_type="fixed",
    )
    ReservationPrice.objects.create(
        name="Ganzer Tag inkl. Abend",
        usage_type=cls.usagetypes["Sitzungszimmer extern"],
        priority=3,
        time_unit="hours",
        duration_min=10.0,
        duration_max=24.0,
        cost=140.00,
        cost_type="fixed",
    )


def create_reservationobjects(cls):
    create_reservationtypes(cls)
    create_usagetypes(cls)

    cls.reservationobjects = {}

    ro = ReservationObject.objects.create(
        name="Gästezimmer A", reservation_type=cls.reservationtypes["Gästezimmer"]
    )
    ro.usage_types.set(
        [
            cls.usagetypes["Gästezimmer Standard"],
        ]
    )
    cls.reservationobjects["Gästezimmer A"] = ro

    ro = ReservationObject.objects.create(
        name="Arbeitsplatz 1", reservation_type=cls.reservationtypes["Werkstatt"]
    )
    cls.reservationobjects["Arbeitsplatz 1"] = ro

    ro = ReservationObject.objects.create(
        name="Dachküche", reservation_type=cls.reservationtypes["Dachküche"]
    )
    cls.reservationobjects["Dachküche"] = ro

    ro = ReservationObject.objects.create(
        name="Sitzungszimmer gross", reservation_type=cls.reservationtypes["Sitzungszimmer"]
    )
    ro.usage_types.set(
        [
            cls.usagetypes["Sitzungszimmer kostenlos"],
            cls.usagetypes["Sitzungszimmer intern"],
            cls.usagetypes["Sitzungszimmer extern"],
        ]
    )
    cls.reservationobjects["Sitzungszimmer gross"] = ro
