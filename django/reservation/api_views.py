import datetime
import logging
import os
import re
import zoneinfo

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.db.models import Q
from django.template import Context, Template
from django.utils import timezone
from html2text import html2text
from rest_framework import permissions, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from geno.models import Address, RentalUnit

from .models import (
    Report,
    ReportCategory,
    ReportPicture,
    ReportType,
    Reservation,
    ReservationObject,
    ReservationType,
)
from .serializers import ReservationSerializer, ReservationTypeSerializer

logger = logging.getLogger("reservation")


class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows reservations to be viewed
    """

    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get_queryset(self):
        """
        Returns new/approved reservations owned by user for active reservation types.
        """
        # print(self.request.user)
        adr = get_address(self.request.user)
        queryset = (
            Reservation.objects.filter(contact=adr)
            .filter(Q(state="new") | Q(state="approved"))
            .filter(name__reservation_type__active=True)
            .order_by("-date_start")
        )  # filter(active=True)
        # queryset = Reservation.objects.filter(contact=adr).filter(Q(state='new')|Q(state='approved')).order_by('-date_start') #filter(active=True)
        return queryset


class ReservationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for reservation types.
    """

    serializer_class = ReservationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get_queryset(self):
        adr = get_address(self.request.user)
        roles = adr.get_roles()
        queryset = (
            ReservationType.objects.filter(active=True)
            .filter(required_role__in=roles)
            .order_by("id")
        )
        return queryset


class ReservationSearch(APIView):
    """
    View to search for reservable object based on type and date range.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get(self, request, format=None):
        """
        Return a list of reservable objects.
        """
        res = check_reservation_request(request, request.query_params)

        return Response(res["robjects_available"] + res["robjects_unavailable"])


class ReservationEdit(APIView):
    """
    View to add/edit reservation.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def post(self, request, format=None):
        # print(request.data)
        try:
            address = get_address(request.user)
        except Exception:
            logger.info("validation error: address for user %s not found." % request.user)
            raise ValidationError("Not allowed")

        if "action" not in request.data:
            logger.info("validation error: missing action.")
            raise ValidationError("Missing action.")
        if request.data["action"] == "add":
            return self.add_reservation(request, address)
        if request.data["action"] == "cancel":
            return self.cancel_reservation(request, address)
        else:
            logger.info("validation error: invalid action: %s." % request.data["action"])
            raise ValidationError("Invalid action.")

    def cancel_reservation(self, request, address):
        try:
            res = Reservation.objects.get(id=request.data["reservationId"])
        except Reservation.DoesNotExist:
            logger.error("Can't cancel. Reservation does not exist: %s." % request.data)
            raise ValidationError("Reservation not found.")
        except Exception as e:
            logger.error("Can't cancel. Reservation not found: %s / %s." % (str(e), request.data))
            raise ValidationError("Could not find reservation.")

        if res.contact != address:
            logger.error(
                "Can't cancel. Reservation %s is not assigned to user-address %s."
                % (res.id, address)
            )
            raise ValidationError("Reservation not assigned to user.")

        if res.state == "cancelled":
            ## Is already cancelled
            logger.info("Reservation %s is already cancelled. No action required." % res.id)
            return Response({"status": "OK"})
        elif res.state not in ("new", "approved"):
            logger.error("Can't cancel reservation %s with state %s." % (res.id, res.state))
            raise ValidationError("Can't cancel %s reservations." % res.state)

        try:
            res.state = "cancelled"
            res.save()
        except Exception as e:
            logger.error("Saving cancelled reservation %s failed: %s" % (res.id, str(e)))
            raise ValidationError("Could not save reservation")

        logger.info("Cancelled reservation %s (id=%s)" % (res, res.id))
        return Response({"status": "OK"})

    def add_reservation(self, request, address):
        res = check_reservation_request(request, request.data, get_blocking_res=True)
        if not res["type"]:
            logger.info(
                "validation error: reservationType %s not found." % request.data["reservationType"]
            )
            raise ValidationError(
                "reservationType %s not found." % request.data["reservationType"]
            )
        if "action" not in request.data:
            logger.info("validation error: Parameter action is required.")
            raise ValidationError("Parameter action is required.")
        if "selectedRoom" not in request.data:
            logger.info("validation error: Parameter selectedRoom is required.")
            raise ValidationError("Parameter selectedRoom is required.")
        if request.data["action"] not in ("add",):
            logger.info(
                "validation error: Invalid value for parameter action: %s."
                % request.data["action"]
            )
            raise ValidationError(
                "Invalid value for parameter action: %s." % request.data["action"]
            )
        if request.data["action"] == "add":
            if res["date_start"] < timezone.now():
                logger.warning(
                    "Tried to add reservation in the past: selectedRoom=%s date=%s-%s"
                    % (request.data["selectedRoom"], res["date_start"], res["date_end"])
                )
                return Response({"status": "ERROR", "msg": "Datum liegt in der Vergangenheit."})
            if res["blocking_res"]:
                logger.warning(
                    "Tried to add reservation for object that is not available anymore: selectedRoom=%s date=%s-%s"
                    % (request.data["selectedRoom"], res["date_start"], res["date_end"])
                )
                return Response({"status": "ERROR", "msg": "Nicht mehr verfügbar."})

            ## Add reservation
            try:
                ro = ReservationObject.objects.get(id=request.data["selectedRoom"])
            except ReservationObject.DoesNotExist:
                logger.info(
                    "validation error: Invalid reservation object id: %s"
                    % request.data["selectedRoom"]
                )
                raise ValidationError(
                    "Invalid reservation object id: %s" % request.data["selectedRoom"]
                )

            if "summary" in request.data and request.data["summary"]:
                reservation_summary = request.data["summary"]
            else:
                reservation_summary = ""
            if ro.reservation_type.summary_required and not reservation_summary:
                logger.info(
                    "validation error: Summary required for reservation object id: %s, summary: %s"
                    % (request.data["selectedRoom"], request.data["summary"])
                )
                raise ValidationError("Missing summary")

            new_res = Reservation(
                name=ro,
                contact=address,
                date_start=res["date_start"],
                date_end=res["date_end"],
                summary=reservation_summary,
                # state=,
            )
            new_res.save()
            logger.info(
                "Added new reservation: %s, id=%s, user=%s, date=%s - %s"
                % (new_res, new_res.id, request.user, new_res.date_start, new_res.date_end)
            )

            ## Double check for concurrent update
            res = check_reservation_request(request, request.data, get_blocking_res=True)
            if len(res["blocking_res"]) > 1 or res["blocking_res"][0] != new_res:
                ## Conflicting reservations -> roll back
                logger.error(
                    "ROLLBACK of added reservation for object that is not available anymore! selectedRoom=%s date=%s-%s"
                    % (request.data["selectedRoom"], res["date_start"], res["date_end"])
                )
                new_res.delete()
                return Response({"status": "ERROR", "msg": "Nicht mehr verfügbar."})

            ## Send confirmation email
            if (
                ro.reservation_type.confirmation_email_template
                and ro.reservation_type.confirmation_email_template.active
            ):
                try:
                    ctx = {
                        "template": ro.reservation_type.confirmation_email_template.text,
                        "sender": ro.reservation_type.confirmation_email_sender,
                        "subject": "Bestätigung Reservation %s" % ro,
                        "reservation_object": str(ro),
                        "reservation_from": new_res.date_start.strftime("%d.%m.%Y %H:%M"),
                        "reservation_to": new_res.date_end.strftime("%d.%m.%Y %H:%M"),
                        "reservation_id": new_res.id,
                    }
                    send_reservation_confirmation(address, ctx)
                except Exception as e:
                    mail_admins(
                        "Reservation confirmation ERROR",
                        "Could not send reservation confirmation. See logs.",
                    )
                    logger.error(
                        "Could not send reservation confirmation for reservation id %s: %s"
                        % (new_res.id, e)
                    )
                else:
                    new_res.state = "approved"
                    new_res.save()

        return Response({"status": "OK"})


def check_reservation_request(request, request_data, get_blocking_res=False):
    ret = {
        "type": None,
        "pay_days": 0,
        "robjects_available": [],
        "robjects_unavailable": [],
        "blocking_res": [],
        "date_start": None,
        "date_end": None,
    }
    if "reservationType" not in request_data:
        raise ValidationError("Parameter reservationType is required.")
    try:
        ret["type"] = ReservationType.objects.get(name=request_data["reservationType"])
        ## TODO: Set fixed time!
    except ReservationType.DoesNotExist:
        return ret

    if not user_has_permission_to_reserve(request.user, ret["type"]):
        return ret

    if "dateFrom" not in request_data:
        raise ValidationError("Parameter dateFrom is required.")
    if "dateTo" not in request_data:
        raise ValidationError("Parameter dateTo is required.")
    if "timeFrom" not in request_data:
        raise ValidationError("Parameter timeFrom is required.")
    if "timeTo" not in request_data:
        raise ValidationError("Parameter timeTo is required.")
    try:
        local_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        search_date_start = datetime.datetime.strptime(
            request_data["dateFrom"] + " " + request_data["timeFrom"], "%d.%m.%Y %H:%M"
        ).replace(tzinfo=local_tz)
        search_date_end = datetime.datetime.strptime(
            request_data["dateTo"] + " " + request_data["timeTo"], "%d.%m.%Y %H:%M"
        ).replace(tzinfo=local_tz)
    except ValueError as e:
        logger.error(
            "Got wrong date/time input for reservation: %s %s - %s %s: %s"
            % (
                request_data["dateFrom"],
                request_data["timeFrom"],
                request_data["dateTo"],
                request_data["timeTo"],
                e,
            )
        )
        raise ValidationError("Invalid date/time parameters")
    ret["date_start"] = search_date_start
    ret["date_end"] = search_date_end

    date_diff = search_date_end.date() - search_date_start.date()
    # print('Date diff: %s days' % date_diff.days)
    if date_diff.days > 3:
        ret["pay_days"] = date_diff.days - 3

    ro_query = ReservationObject.objects.filter(reservation_type=ret["type"])
    if "selectedRoom" in request_data:
        ro_query = ro_query.filter(id=request_data["selectedRoom"])
    for ro in ro_query.order_by("name"):
        # print(ro.name)
        ## Check availability - find start and end of unavailable block
        blocking_res = ro.get_blocking_reservations(search_date_start, search_date_end)
        if get_blocking_res:
            ## Just get blocking reservations
            for res in blocking_res:
                ret["blocking_res"].append(res)
            continue

        cur_res = blocking_res.first()
        ret["blocking_res"].append(cur_res)
        unavailable_date_start = None
        unavailable_date_end = None
        while cur_res:
            # print("- Unavailable block START date: %s - %s" % (cur_res.date_start,cur_res.date_end))
            unavailable_date_start = cur_res.date_start
            if ro.reservation_type.fixed_time:
                ## Check if there is a reservation on the previous day.
                cur_date = unavailable_date_start - datetime.timedelta(days=1)
            else:
                ## Check if there is a reservation just before the current one.
                cur_date = unavailable_date_start - datetime.timedelta(minutes=5)
            cur_res = ro.get_blocking_reservations(cur_date).first()
        cur_res = blocking_res.first()
        while cur_res:
            # print("- Unavailable block END date: %s - %s" % (cur_res.date_start,cur_res.date_end))
            unavailable_date_end = cur_res.date_end
            if ro.reservation_type.fixed_time:
                ## Check if there is a reservation on the next day.
                cur_date = unavailable_date_end + datetime.timedelta(days=1)
            else:
                ## Check if there is a reservation just after the current one.
                cur_date = unavailable_date_end + datetime.timedelta(minutes=5)
            cur_res = ro.get_blocking_reservations(cur_date).first()

        robject = {
            "id": ro.id,
            "title": ro.name,
            "subtitle": ro.short_description,
            "costs": "Fr. %s" % (ret["pay_days"] * ro.cost),
            "text": ro.description,
            "isAvailable": True,
            "unavailableDate": None,
        }
        if ro.image:
            robject["imageUrl"] = settings.BASE_URL + ro.image.url

        if unavailable_date_start:
            robject["isAvailable"] = False
            robject["unavailableDate"] = "%s bis %s" % (
                timezone.localtime(unavailable_date_start).strftime("%d.%m.%Y %H:%M"),
                timezone.localtime(unavailable_date_end).strftime("%d.%m.%Y %H:%M"),
            )
            ret["robjects_unavailable"].append(robject)
        else:
            ret["robjects_available"].append(robject)
    return ret


def user_has_permission_to_reserve(user, reservation_type):
    adr = get_address(user)
    roles = adr.get_roles()
    return reservation_type.required_role in roles


def get_address(user):
    try:
        adr = Address.objects.get(user=user)
    except Address.MultipleObjectsReturned:
        logger.error("User -> Address not unique: %s" % user)
        raise NotFound(detail="Benutzername %s nicht eindeutig." % user)
    except Address.DoesNotExist:
        logger.error("User -> Address not found: %s" % user)
        raise NotFound(detail="Benutzer*in %s nicht gefunden." % user)
    return adr


def send_reservation_confirmation(address, ctx):
    mail_template = Template(
        "%s%s%s" % ("{% autoescape off %}", ctx["template"], "{% endautoescape %}")
    )
    mail_template_ishtml = re.search("<html", ctx["template"], re.IGNORECASE)

    mail_recipient = address.get_mail_recipient()

    context = ctx
    context.update(address.get_context())

    mail_text_html = mail_template.render(Context(context))
    if mail_template_ishtml:
        mail_text = html2text(mail_text_html)
    else:
        mail_text = mail_text_html
    bcc = None
    # bcc = [settings.TEST_MAIL_RECIPIENT,]

    mail = EmailMultiAlternatives(
        context["subject"], mail_text, context["sender"], [mail_recipient], bcc
    )
    # for att in m['files']:
    #    attfile = open(att['file'], "rb")
    #    mail.attach(att['filename'], attfile.read()) #, 'application/pdf')
    #    attfile.close()
    if mail_template_ishtml:
        mail.attach_alternative(mail_text_html, "text/html")
        # mail.content_subtype = "html"  # Main content is now text/html
    mails_sent = mail.send()
    if mails_sent == 1:
        logger.info("Email '%s' an %s geschickt." % (context["subject"], mail_recipient))
    else:
        logger.error(
            "KEIN Email '%s' an %s geschickt (mails_sent=%s)."
            % (context["subject"], mail_recipient, mails_sent)
        )


def send_report_email(report):
    t = """{% autoescape off %}<html><body><p>Guten Tag</p>

<p>Es wurde folgende Meldung im System registriert:

<ul>
<li>Meldungstyp: {{report.report_type}}</li>
<li>Kategorie: {{report.category}}</li>
{% if report.rental_unit %}
<li>Mietobjekt: <a href="{{base_url}}/admin/geno/rentalunit/{{report.rental_unit.id}}/change/">{{report.rental_unit}}</a>, {{report.rental_unit.floor}}, {{report.rental_unit.building}}</li>
{% endif %}
<li>Kontakt: <a href="{{base_url}}/admin/geno/address/{{report.contact.id}}/change/">{{report.contact}}</a>, <a href="mailto:{{report.contact.email}}?subject={{subject|escape}}">{{report.contact.email}}</a>, {{report.contact.telephone}}</li>
<li>Erreichbarkeit: {{report.contact_text}}</li>
<li>Status: {{report.get_status_display}} / {{report.status_date|date:"d.m.Y H:i"}}</li>
<li><a href="{{base_url}}/admin/reservation/report/{{report.id}}/change/">Meldung im Admin-Tool bearbeiten</a></li>
</ul>
</p>

<p>
Betreff: {{report.name}}<br>
<hr>
{{report.text|linebreaks}}
<hr>
</p>

{% if images %}
<p>
Bilder im Anhang:
<ul>
{{images}}
</ul>
</p>
{% endif %}
</body></html>

{% endautoescape %}"""
    mail_template = Template(t)
    mail_template_ishtml = re.search("<html", t, re.IGNORECASE)

    sender = f'"Cohiva {settings.COHIVA_SITE_NICKNAME}" <{settings.GENO_DEFAULT_EMAIL}>'
    if settings.DEBUG:
        mail_recipient = settings.TEST_MAIL_RECIPIENT
        bcc = None
        recipient_cc = None
    else:
        mail_recipient = settings.COHIVA_REPORT_EMAIL
        bcc = None
        recipient_cc = None

    images = []
    images_text = ""
    for pic in ReportPicture.objects.filter(report=report):
        pic_filename = os.path.basename(pic.image.name)
        images.append({"file": pic.image.path, "filename": pic_filename})
        images_text += "<li>%s</li>\n" % pic_filename

    if report.rental_unit:
        ru_str = report.rental_unit.name
    else:
        ru_str = "000"

    context = {
        "subject": "%s: %s/%s - %s" % (report.report_type, ru_str, report.contact, report.name),
        "report": report,
        "images": images_text,
    }

    mail_text_html = mail_template.render(Context(context))
    if mail_template_ishtml:
        mail_text = html2text(mail_text_html)
    else:
        mail_text = mail_text_html

    mail = EmailMultiAlternatives(
        context["subject"], mail_text, sender, [mail_recipient], bcc, cc=recipient_cc
    )
    for img in images:
        # print("Adding image: %s" % (img['file']))
        attfile = open(img["file"], "rb")
        mail.attach(img["filename"], attfile.read())  # , 'application/pdf')
        attfile.close()
    if mail_template_ishtml:
        mail.attach_alternative(mail_text_html, "text/html")
        # mail.content_subtype = "html"  # Main content is now text/html
    mails_sent = mail.send()
    if mails_sent == 1:
        logger.info("Email '%s' an %s geschickt." % (context["subject"], mail_recipient))
    else:
        logger.error(
            "KEIN Email '%s' an %s geschickt (mails_sent=%s)."
            % (context["subject"], mail_recipient, mails_sent)
        )


class ReportSubmission(APIView):
    """
    Submit reports.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get(self, request, format=None):
        """
        Return data for report submission form.
        """

        default_report_type_id = 1
        try:
            report_type = ReportType.objects.get(id=default_report_type_id)
        except ReportType.DoesNotExist:
            raise NotFound(detail=f"Report type for id {default_report_type_id} not found.")

        categories = []
        for rc in ReportCategory.objects.filter(report_type=report_type).order_by("name"):
            categories.append({"value": rc.id, "label": rc.name})

        address = get_address(self.request.user)
        contact = "%s %s" % (address.first_name, address.name)
        if address.email:
            contact = "%s, %s" % (contact, address.email)
        if address.telephone:
            contact = "%s, %s" % (contact, address.telephone)

        rental_units = []
        for ru in address.get_rental_units():
            rental_units.append({"value": ru.id, "label": str(ru)})

        return Response(
            {
                "report_type": report_type.id,
                "categories": categories,
                "contact": contact,
                "rental_units": rental_units,
            }
        )

    def post(self, request, format=None):
        # print(request.data)
        # print(request.data['category'])

        default_report_type_id = 1
        try:
            if request.data["unit"] == "__OTHER__":
                rental_unit = None
            else:
                rental_unit = RentalUnit.objects.get(id=request.data["unit"])
            report = Report(
                name=request.data["subject"],
                report_type=ReportType.objects.get(id=default_report_type_id),
                category=ReportCategory.objects.get(id=request.data["category"]),
                rental_unit=rental_unit,
                contact=get_address(self.request.user),
                contact_text=request.data["contact_text"],
                text=request.data["text"],
                report_date=timezone.now(),
                status_date=timezone.now(),
            )
            report.save()
        except Exception as e:
            logger.error("Could not save report: %s / %s" % (str(e), request.data))
            return Response({"status": "ERROR", "msg": "Konnte Meldung nicht speichern"})

        pic_count = 1
        for pic in request.data.getlist("pictures"):
            # print(pic)
            try:
                if report.rental_unit:
                    ru_name = report.rental_unit.name
                else:
                    ru_name = "000"
                pic_name = "%s_Meldung-%s_Bild-%s" % (ru_name, report.id, pic_count)
                report_pic = ReportPicture(name=pic_name, image=pic, report=report)
                report_pic.save()
            except Exception as e:
                logger.error(
                    "Could not save picture for report %s (id=%s): %s / %s"
                    % (report.name, report.id, str(e), pic)
                )
                return Response(
                    {
                        "status": "ERROR",
                        "msg": "Meldung übermittelt, aber konnte Bild(er) nicht speichern.",
                    }
                )
            pic_count += 1

        logger.info("Saved report '%s' with %d images." % (report, (pic_count - 1)))
        try:
            send_report_email(report)
        except Exception as e:
            mail_admins("Report email ERROR", "Could not send report email. See logs.")
            logger.error("Could not send report email for report id %s: %s" % (report.id, e))

        return Response({"status": "OK"})


class CalendarFeeds(APIView):
    """
    Calendar feeds API.
    """

    permission_classes = [permissions.IsAuthenticated]  ## Allow all authenticated users

    def get(self, request, format=None):
        """
        Return a list of available calendar feeds (event sources).
        """
        calendars = [
            {
                "id": "plena",
                "cat": "Genossenschaft",
                "name": "Plena, GV, Hausversammlung etc.",
                "url": settings.BASE_URL + "/calendar/feed/plena",
                "color": "#4680CD",
                "textColor": "black",
            },
        ]
        for rtype in ReservationType.objects.all():
            if rtype.active:
                calendars.append(
                    {
                        "id": "_res-%d" % rtype.id,
                        "cat": "Reservation",
                        "name": rtype.name,
                        "url": settings.BASE_URL + "/calendar/feed/_res-%d" % rtype.id,
                        "color": rtype.color,
                        "textColor": "black",
                    }
                )
        return Response({"status": "OK", "calendars": calendars})


def get_capabilities(request, capabilities):
    return


## Model viewset
# class ModelViewSet(mixins.CreateModelMixin,
#                   mixins.RetrieveModelMixin,
#                   mixins.UpdateModelMixin,
#                   mixins.DestroyModelMixin,
#                   mixins.ListModelMixin,
#                   GenericViewSet)
#
# So rather than extending ModelViewSet, why not just use whatever you need? So for example:
#
# from rest_framework import viewsets, mixins
#
# class SampleViewSet(mixins.RetrieveModelMixin,
#                    mixins.UpdateModelMixin,
#                    mixins.DestroyModelMixin,
#                    viewsets.GenericViewSet):
