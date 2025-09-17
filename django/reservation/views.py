import datetime
import logging
import zoneinfo

import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

## For ical import
from icalendar import Calendar  # , vDatetime, Event

from geno.models import Address

from .models import Reservation, ReservationObject, ReservationType

logger = logging.getLogger("reservation")


def sync_ical_reservations(request):
    data_url = (
        "https://export.kalender.digital/ics/0/<ID>/<NAME>.ics?past_months=1&future_months=36"
    )
    # data_url="https://export.kalender.digital/ics/0/<ID>/<NAME>.ics?past_months=1&future_months=36"
    # data_url="https://export.kalender.digital/ics/0/<ID>/<NAME>.ics?past_months=0&future_months=1"
    local_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)

    ret = []

    ret.append({"info": "Getting data from %s." % (data_url)})
    try:
        response = requests.get(data_url)
        response.raise_for_status()
    except Exception as e:
        ret.append({"info": "ERROR: Could not fetch reservations data: %s" % (e)})
        return render(
            request, "geno/messages.html", {"response": ret, "title": "Sync reservations iCal"}
        )

    try:
        cal = Calendar.from_ical(response.text)
    except Exception as e:
        ret.append({"info": "ERROR: Could not parse calendar data: %s - %s" % (e, response.text)})
        return render(
            request, "geno/messages.html", {"response": ret, "title": "Sync reservations iCal"}
        )

    skip_list = [
        "Dachküche für Alle - keine Reservation möglich",
        "Dachküche: offen für alle - keine Reservation möglich",
        "Dachküche offen für alle, keine Reservationen möglich",
        "Gründonnerstag",
        "Augsburger Friedensfest",
    ]

    ignore_fields = ["contact"]
    default_adr = Address.objects.get(organization=settings.GENO_NAME, name="")

    skipped = []
    imported = []
    not_imported = []
    counts = {"total": 0, "skip": 0, "add": 0, "update": 0, "unchanged": 0}

    # print("=== cal object ===")
    # print(str(cal.to_ical()).replace('\\r\\n', '\n').strip())
    event_ids_found = []
    first_event_date = None
    for e in cal.walk("vevent"):  # cal.subcomponents:
        cal_event = {}
        cal_event["start"] = e.get("dtstart").dt
        cal_event["end"] = e.get("dtend").dt
        cal_event["uid"] = e.get("uid")
        cal_event["categories"] = e.get("categories")
        cal_event["summary"] = e.get("summary")
        cal_event["attendee"] = e.get("attendee")
        cal_event["description"] = e.get("description")
        # ret.append({'info': "Cal event: %s" % cal_event})
        if cal_event["summary"][-4:] == " (§)" or cal_event["summary"] in skip_list:
            skipped.append(
                "%s / %s" % (cal_event["summary"], cal_event["start"].strftime("%d.%m.%Y %H:%M"))
            )
            continue
        counts["total"] += 1
        text = cal_event["summary"]
        event_id = "icdk-%s" % cal_event["uid"]
        if cal_event["attendee"]:
            text = "%s (%s)" % (text, cal_event["attendee"])
        if cal_event["description"]:
            text = "%s: %s" % (text, cal_event["description"])
        info = "%s - %s: %s [%s, %s]" % (
            cal_event["start"].strftime("%d.%m.%Y %H:%M%z"),
            cal_event["end"].strftime("%d.%m.%Y %H:%M%z"),
            text,
            event_id,
            cal_event["categories"],
        )

        if not isinstance(cal_event["start"], datetime.datetime):
            ## Whole day reservation: convert date to datetime
            cal_event["start"] = datetime.datetime.combine(
                cal_event["start"], datetime.datetime.min.time()
            ).replace(tzinfo=local_tz)
            cal_event["end"] = datetime.datetime.combine(
                cal_event["end"], datetime.datetime.min.time()
            ).replace(tzinfo=local_tz)
            # print("Converted whole day reservation: %s ==> %s - %s" % (info, cal_event['start'], cal_event['end']))

        ## Create or update reservation
        try:
            reservation_model_object = ReservationObject.objects.get(name="Dachküche")
        except ReservationObject.DoesNotExist:
            logger.warning(
                "Ignoring reservation with unknown reservation object: %s." % (event_id)
            )
            counts["skip"] += 1
            continue

        reservation_data = {
            #'name': reservation_object['name'],
            #'reservation_type': reservation_object['type'],
            "name": reservation_model_object,
            "contact": default_adr,
            "date_start": cal_event["start"],
            "date_end": cal_event["end"],
            "summary": text[:120],
            "additional_information": cal_event["categories"],
        }

        try:
            reservation = Reservation.objects.get(flink_id=event_id)
            changes = False
            logger.debug("Reservation %s exists already. Checking for changes." % event_id)
            for key in reservation_data:
                old = getattr(reservation, key)
                new = reservation_data[key]
                if old != new:
                    if key in ignore_fields:
                        logger.debug("Ignoring changes for %s: %s -> %s" % (key, old, new))
                        continue
                    if not changes:
                        changes = True
                        logger.info(
                            "+- Updating reservation %s (%s):" % (event_id, cal_event["start"])
                        )
                    logger.info("   - %s: %s -> %s" % (key, old, new))
                    setattr(reservation, key, new)
            if changes:
                reservation.save()
                counts["update"] += 1
                imported.append(info)
            else:
                counts["unchanged"] += 1
                not_imported.append(info)
        except Reservation.DoesNotExist:
            logger.info("++ New reservation %s (%s)." % (event_id, cal_event["start"]))
            reservation = Reservation(flink_id=event_id)
            for key in reservation_data:
                setattr(reservation, key, reservation_data[key])
            reservation.save()
            counts["add"] += 1
            imported.append(info)

        if not first_event_date:
            first_event_date = reservation.date_start
        event_ids_found.append(event_id)

    ## Check for deleted event_ids
    cancel_count = 0
    for res in (
        Reservation.objects.filter(Q(state="new") | Q(state="approved"))
        .filter(flink_id__startswith="icdk-")
        .filter(date_start__gt=first_event_date)
    ):
        if res.flink_id not in event_ids_found:
            cancel_count += 1
            logger.info(
                "-- Cancelling reservation %s (%s/%s/%s) id=%s."
                % (res.flink_id, res.date_start, res.contact, res.summary, res.id)
            )
            res.state = "cancelled"
            res.save()

    ret.append({"info": "Imported %s events" % len(imported), "objects": imported})
    # ret.append({'info': "Skipped %s events (already imported)" % len(not_imported), 'objects': not_imported})
    # ret.append({'info': "Skipped %s events (in skip list)" % len(skipped), 'objects': skipped})
    ret.append(
        {
            "info": "DONE",
            "objects": [
                "Total: %s" % counts["total"],
                "Skipped: %s" % counts["skip"],
                "Added: %s" % counts["add"],
                "Updated: %s" % counts["update"],
                "Unchanged: %s" % counts["unchanged"],
                "Cancelled: %s" % cancel_count,
            ],
        }
    )

    return render(
        request, "geno/messages.html", {"response": ret, "title": "Sync reservations iCal"}
    )


def send_report_emails(request):
    ## Send ALL report emails
    ret = []
    # for r in Report.objects.all():
    #    ret.append({'info': "Sending report email for %s" % r})
    #    send_report_email(r)
    #    break
    ret.append({"info": "Sending report emails is disabled."})

    return render(
        request, "geno/messages.html", {"response": ret, "title": "Send ALL Report Emails"}
    )


def cron_maintenance(request):
    ## Add/delete reservation blockers
    info = []
    for ro in ReservationObject.objects.filter(reservation_type__active=True):
        info.append("Updating reservation blockers for %s. (debug=%s)" % (ro, settings.DEBUG))
        ro.update_reservation_blockers()
    return JsonResponse({"status": "OK", "info": info})


def calendar_feed(request, calendar_id):
    ## Example request: "GET /calendar/feed/?start=2017-10-30&end=2017-12-11&_=1511889435427 HTTP/1.1"
    ## Example response:
    # events = [{
    #   title: 'Meeting',
    #   start: '2017-11-12T10:30:00',
    #   end: '2017-11-12T12:30:00',
    #   description 'Meeting description',
    #   url: 'Link'
    # }]

    if request.GET.get("start") and request.GET.get("end"):
        start_iso = request.GET.get("start")
        end_iso = request.GET.get("end")
        start = datetime.datetime.strptime(
            start_iso[: len(start_iso) - 3] + start_iso[len(start_iso) - 2 :],
            "%Y-%m-%dT%H:%M:%S%z",
        )
        end = datetime.datetime.strptime(
            end_iso[: len(end_iso) - 3] + end_iso[len(end_iso) - 2 :], "%Y-%m-%dT%H:%M:%S%z"
        )
    else:
        return JsonResponse([], safe=False)

    events = []
    if calendar_id[0:5] == "_res-":
        reservation_type = ReservationType.objects.filter(id=calendar_id[5:]).first()
        if reservation_type:
            events = reservation_type.get_calendar_events(start, end)
    elif "website" in settings.COHIVA_FEATURES:
        from website.views import get_calendar_events

        events = get_calendar_events(calendar_id, start, end)

    return JsonResponse(events, safe=False)
