import datetime
import io
import json
import os
import re
import subprocess
import tempfile
import zipfile
from collections import OrderedDict
from smtplib import SMTPException

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.forms import formset_factory
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect

# from django.urls import reverse
from django.shortcuts import redirect, render
from django.template import Context, loader
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.html import escape
from django_tables2 import RequestConfig
from oauthlib.oauth2 import TokenExpiredError

## For OAuth client
from requests_oauthlib import OAuth2Session
from stdnum.ch import esr

if hasattr(settings, "SHARE_PLOT") and settings.SHARE_PLOT:
    ## For Plotting
    # from matplotlib import pyplot as plt
    import io

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

## For GnuCash and interest calc.
from decimal import Decimal

from piecash import Split, Transaction, open_book

if hasattr(settings, "CREATESEND_API_KEY") and settings.CREATESEND_API_KEY:
    import createsend

if hasattr(settings, "MAILMAN_API") and settings.MAILMAN_API["password"]:
    import mailmanclient

import geno.settings as geno_settings

from .documents import send_member_mail_process
from .exporter import (
    export_addresses_carddav,
    export_adit_file,
    export_data_to_xls,
    generate_demo_camt053_file,
)
from .forms import (
    InvoiceFilterForm,
    ManualInvoiceForm,
    ManualInvoiceLineForm,
    MemberMailActionForm,
    MemberMailForm,
    MemberMailSelectForm,
    TransactionForm,
    TransactionFormInvoice,
    TransactionUploadFileForm,
    TransactionUploadProcessForm,
    WebstampForm,
    process_registration_forms,
)
from .gnucash import (
    add_invoice,
    consolidate_invoices,
    create_invoices,
    create_qrbill,
    get_book,
    get_duplicate_invoices,
    get_reference_nr,
    guess_transaction,
    invoice_detail,
    invoice_overview,
    pay_invoice,
    process_sepa_transactions,
    process_transaction,
)
from .importer import (
    import_adit_serial,
    import_codes_from_file,
    import_contracts_from_file,
    import_emonitor_addresses_from_file,
    import_emonitor_children_from_file,
    import_emonitor_contracts_from_file,
    import_keller_from_file,
    import_members_from_file,
    import_rentalunits_from_file,
    process_eigenmittel,
    process_transaction_file,
    update_address_from_file,
)
from .models import (
    Address,
    Contract,
    Document,
    DocumentType,
    GenericAttribute,
    Invoice,
    InvoiceCategory,
    Member,
    MemberAttribute,
    MemberAttributeType,
    RentalUnit,
    Share,
    ShareType,
    get_active_contracts,
    get_active_shares,
)
from .shares import check_rental_shares_report, get_share_statement_data, share_interest_calc
from .tables import (
    InvoiceDetailTable,
    InvoiceOverviewTable,
    MemberTable,
    MemberTableAdmin,
)
from .utils import fill_template_pod, is_member, nformat, odt2pdf

# from .decorators import login_required

if "portal" in settings.INSTALLED_APPS:
    import portal.auth as portal_auth

import builtins
import contextlib
import logging

logger = logging.getLogger("geno")


def unauthorized(request):
    c = {
        "response": [{"info": "Sie haben keine Berechtigung für diese Aktion."}],
        "title": "Keine Berechtigung",
    }
    return render(request, "geno/messages.html", c)


@login_required
def import_generic(request, what):
    if not request.user.has_perm("geno.admin_import"):
        return unauthorized(request)
    if not settings.ALLOW_IMPORT:
        title = "Error"
        ret = [
            {"info": "Import is disabled in settings."},
        ]
    else:
        if what == "members":
            title = "Mitgliederliste importieren"
            ret = import_members_from_file(empty_tables_first=False)
        elif what == "address":
            title = "Adressen aktualisieren"
            ret = update_address_from_file()
        elif what == "contracts":
            title = "Verträge importieren"
            ret = import_contracts_from_file(empty_tables_first=True)
        elif what == "rentalunits":
            title = "Mietobjekte aus eMonitor importieren"
            ret = import_rentalunits_from_file(empty_tables_first=True)
        elif what == "emonitorcontracts":
            title = "Zuweisungen aus eMonitor importieren"
            ret = import_emonitor_contracts_from_file(empty_tables_first=True)
        elif what == "emonitoraddresses":
            title = "Adressen/Vertragsparteien aus eMonitor importieren"
            ret = import_emonitor_addresses_from_file(empty_tables_first=True)
        elif what == "emonitorchildren":
            title = "Kinder aus eMonitor importieren"
            ret = import_emonitor_children_from_file()
        elif what == "keller":
            title = "Mieterkeller importieren"
            ret = import_keller_from_file(empty_tables_first=True)
        elif what == "eigenmittel":
            title = "Eigenmittelliste abgleichen"
            # ret = process_eigenmittel()
            return process_eigenmittel()
        elif what == "codes":
            title = "Codes importieren"
            ret = import_codes_from_file(empty_tables_first=False)
        elif what == "adit_serial":
            title = "ADIT Seriennummern importieren"
            ret = import_adit_serial()
        else:
            raise Http404("Ungültige Adresse")
    c = {"response": ret, "title": title}
    return render(request, "geno/messages.html", c)


def export_generic(request, what):
    if what == "addresses_carddav":
        title = "Adressen nach CardDAV exportieren"
        ret = export_addresses_carddav(request.GET.get("delete", "") == "yes")
    elif what == "adit":
        title = "ADIT Gegensprechanlage exportieren"
        return export_adit_file()
    c = {"response": ret, "title": title}
    return render(request, "geno/messages.html", c)


def get_context_data(doctype, obj_id, extra_context):
    c = extra_context
    filename_prefix = {
        "memberletter": "Brief_Bestätigung_Mitgliedschaft",
        "memberfinanz": "Brief_Finanzielle_Unterstützung",
        "memberfee": "Brief_Einforderung_Mitgliederbeitrag",
        "memberfeereminder": "Brief_Einforderung_Mitgliederbeitrag_Reminder",
        "shareconfirm": "Brief_Bestätigung_Anteilscheine",
        "shareconfirm_req": "Brief_Bestätigung_Einforderung",
        #'shareconfirm_reqpart': "Brief_Bestätigung_Einforderung_Rate",
        "loanreminder": "Brief_Erinnerung_Darlehen",
        "statement": "Kontoauszug",
        "mailing": "Brief_Mitglieder",
        "contract": "Vertrag",
        "contract_letter": "Vertrag_Begleitbrief",
        "contract_check": "Formular_Überprüfung_Belegung_Fahrzeuge",
    }

    filename_ext = ".odt"
    if doctype[0:6] == "member":
        obj = Member.objects.get(pk=obj_id)
        adr = obj.name
        c["datum_eintritt"] = obj.date_join.strftime("%d.%m.%Y")
    elif doctype[0:5] == "share":
        obj = Share.objects.get(pk=obj_id)
        adr = obj.name

        if Share.objects.filter(name=adr).filter(share_type=obj.share_type).count() == 1:
            c["is_first_share"] = True
        else:
            c["is_first_share"] = False

        try:
            stype_share = ShareType.objects.get(name="Anteilschein")
        except ShareType.DoesNotExist:
            stype_share = "Nonexistent"
        try:
            stype_loan_noint = ShareType.objects.get(name="Darlehen zinslos")
        except ShareType.DoesNotExist:
            stype_loan_noint = "Nonexistent"
        try:
            stype_loan_int = ShareType.objects.get(name="Darlehen verzinst")
        except ShareType.DoesNotExist:
            stype_loan_int = "Nonexistent"
        try:
            stype_loan_special = ShareType.objects.get(name="Darlehen spezial")
        except ShareType.DoesNotExist:
            stype_loan_special = "Nonexistent"
        try:
            stype_deposit = ShareType.objects.get(name="Depositenkasse")
        except ShareType.DoesNotExist:
            stype_deposit = "Nonexistent"

        if obj.date_due:
            duedate = obj.date_due
        elif obj.duration:
            duedate = obj.date + relativedelta(years=obj.duration)
        else:
            duedate = None
        if duedate:
            duedate_text = " (Fälligkeit: %s)" % duedate.strftime("%d.%m.%Y")
        else:
            duedate_text = ""

        c["betrag_text_zusatz"] = None
        if obj.share_type == stype_share:
            if hasattr(adr, "member"):
                c["datum_eintritt"] = adr.member.date_join.strftime("%d.%m.%Y")
            else:
                c["datum_eintritt"] = None
            if c["datum_eintritt"] and c["is_first_share"]:
                c["betreff"] = "Bestätigung Anteilscheine/Mitgliedschaft"
            else:
                c["betreff"] = "Bestätigung Anteilscheine"
            if obj.quantity == 1:
                c["betrag_text"] = "1 Anteilschein zu CHF %s" % (nformat(obj.value))
            else:
                c["betrag_text"] = "%s Anteilscheine zu CHF %s in Summe CHF %s" % (
                    nformat(obj.quantity, 0),
                    nformat(obj.value),
                    nformat(obj.quantity * obj.value),
                )
            if obj.is_pension_fund:
                c["betrag_text"] = "%s (aus Mitteln der beruflichen Vorsorge)" % (c["betrag_text"])
                c["bvg"] = True
            else:
                c["bvg"] = False
            count = 0
            amount = 0
            for s in get_active_shares().filter(name=obj.name).filter(share_type=stype_share):
                count += s.quantity
                amount += s.quantity * s.value
            if count == 1:
                c["total_anzahl"] = "1 Anteilschein"
            else:
                c["total_anzahl"] = "%s Anteilscheine" % (nformat(count, 0))
            c["total_summe"] = "%s" % (nformat(amount))
        elif obj.share_type == stype_loan_noint:
            c["betrag_text"] = "Zinsloses Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
        elif obj.share_type == stype_loan_int:
            c["betrag_text"] = "Darlehen von CHF %s%s" % (nformat(obj.value, 2), duedate_text)
            c["betrag_text_zusatz"] = "Aktueller Zinssatz: %s%%" % (nformat(obj.interest(), 2))
        elif obj.share_type == stype_deposit:
            c["betrag_text"] = "Einlage in die Depositenkasse von CHF %s" % (nformat(obj.value, 2))
            c["betrag_text_zusatz"] = "Aktueller Zinssatz: %s%%" % (nformat(obj.interest(), 2))
        elif obj.share_type == stype_loan_special:
            c["betrag_text"] = "Darlehen von CHF %s%s" % (nformat(obj.value, 2), duedate_text)
            c["betrag_text_zusatz"] = "Zinssatz: %s%% (gemäss Darlehensvertrag)" % (
                nformat(obj.interest(), 2)
            )
        else:
            c["betrag_text"] = "%s von CHF %s" % (obj.share_type.name, nformat(obj.value, 2))

        c["datum_zahlung"] = obj.date.strftime("%d.%m.%Y")
    elif doctype == "statement" or doctype == "mailing" or doctype == "loanreminder":
        obj = Address.objects.get(pk=obj_id)
        adr = obj
    elif doctype[0:8] == "contract":
        obj = Contract.objects.get(pk=obj_id)
        adr = obj.get_contact_address()
        # adr = obj.person
        c["mietobjekt"] = ", ".join([str(ru) for ru in obj.rental_units.all()])
        c["mindestbelegung"] = " + ".join(
            [str(int(ru.min_occupancy)) for ru in obj.rental_units.filter(min_occupancy__gt=0)]
        )
        c["bewohnende"] = []
        duplicate_check = []
        for tenant in obj.contractors.exclude(ignore_in_lists=True):
            dup_id = f"{tenant.name}{tenant.first_name}"
            if dup_id not in duplicate_check:
                c["bewohnende"].append({"name": tenant.name, "vorname": tenant.first_name})
                duplicate_check.append(dup_id)
        for child in obj.children.exclude(name__ignore_in_lists=True):
            dup_id = f"{child.name.name}{child.name.first_name}"
            if dup_id not in duplicate_check:
                c["bewohnende"].append({"name": child.name.name, "vorname": child.name.first_name})
                duplicate_check.append(dup_id)
        # c['area'] = "%s" % (nformat(obj.area,0))
        # c['netto'] = "%s" % (nformat(obj.rent_total-obj.nk,2))
        # c['nk'] = "%s" % (nformat(obj.nk,2))
        # c['rent_total'] = "%s" % (nformat(obj.rent_total,2))
        # c['depot'] = "%s" % (nformat(obj.depot,2))
        # c['begin'] = obj.date.strftime("%d.%m.%Y")
    else:
        raise RuntimeError("Doctype not implemented.")

    adr_filename_str = ""
    if adr:
        c.update(adr.get_context())
        adr_filename_str = adr.get_filename_str()
    if "filename_tag" in c:
        filename_tag = "_%s" % c["filename_tag"]
    else:
        filename_tag = ""
    if c["roomnr"]:
        adr_filename_str = "%s_%s" % (c["roomnr"], adr_filename_str)
    filename = "%s_%s%s%s" % (
        filename_prefix[doctype],
        adr_filename_str,
        filename_tag,
        filename_ext,
    )

    return {
        "content_object": obj,
        "visible_filename": filename.replace(" ", "").replace("+", "-").replace("/", "-"),
        "context": c,
    }


def context_format(context, output_format="odt"):
    # for k,v in context.items():
    #    if output_format == 'odt':
    #        if isinstance(context[k], basestring):
    #            context[k] = mark_safe(v.replace('\n', '<text:line-break />'))
    return context


@login_required
def documents(request, doctype, obj_id, action):
    try:
        doctype_obj = DocumentType.objects.get(name=doctype)
        if action == "create":
            ## Create new document and attach to content_object
            if not request.user.has_perm("geno.add_document"):
                return unauthorized(request)
            data = get_context_data(doctype, obj_id, {})
        elif action == "download":
            ## Regenerate document
            if not request.user.has_perm("geno.regenerate_document"):
                return unauthorized(request)
            doc = Document.objects.get(pk=obj_id)
            data = {"visible_filename": doc.name, "context": json.loads(doc.data)}
        else:
            raise RuntimeError("Action '%s' is not implemented." % action)
        filename = fill_template_pod(
            doctype_obj.template.file.path, context_format(data["context"]), output_format="odt"
        )
        if not filename:
            raise RuntimeError("Could not fill template")
        if "content_object" in data:
            ## Attach document data to object
            d = Document(
                name=data["visible_filename"],
                doctype=doctype_obj,
                data=json.dumps(data["context"]),
                content_object=data["content_object"],
            )
            d.save()
        resp = FileResponse(
            open(filename, "rb"), as_attachment=True, filename=smart_str(data["visible_filename"])
        )  # content_type = "application/pdf")
        os.remove(filename)
        return resp
    except (RuntimeError, DocumentType.DoesNotExist) as e:
        error = "Fehler beim Erzeugen des Dokuments: %s" % e
    ret = [
        {"info": "ERROR: %s" % error},
    ]
    return render(request, "geno/messages.html", {"response": ret, "title": "Document error"})


@login_required
def share_overview(request):
    if not request.user.has_perm("geno.canview_share_overview"):
        return unauthorized(request)

    ret = []

    try:
        stype_AS = ShareType.objects.get(name="Anteilschein")
    except ShareType.DoesNotExist:
        stype_AS = None

    if len(request.GET.get("date", "")) == 10:
        reference_date = datetime.datetime.strptime(request.GET.get("date"), "%Y-%m-%d").date()
        ret.append({"info": "Übersicht per %s" % (reference_date.strftime("%Y-%m-%d"))})
    else:
        reference_date = None
        ret.append(
            {
                "info": (
                    "Übersicht per heute (datum kann mit ?date=YYYY-MM-DD in URL angegeben werden)"
                )
            }
        )

    total = {"value": 0}
    for share_type in ShareType.objects.all():
        stat = {"quantity": 0, "value": 0, "last_date": None}
        for s in get_active_shares(date=reference_date).filter(share_type=share_type):
            stat["quantity"] += s.quantity
            stat["value"] += s.quantity * s.value
            if stat["last_date"] is None or s.date > stat["last_date"]:
                stat["last_date"] = s.date
        obj = [
            "Anzahl: %s" % nformat(stat["quantity"], 0),
            "Summe CHF: %s" % nformat(stat["value"]),
            "Letzter Eingang: %s" % stat["last_date"],
        ]
        ret.append({"info": share_type, "objects": obj})
        total["value"] += stat["value"]
    ret.append({"info": "TOTAL", "objects": ["Summe CHF: %s" % nformat(total["value"])]})

    if not reference_date and request.user.has_perm("geno.canview_share") and stype_AS:
        non_members = []
        for s in get_active_shares(date=reference_date).filter(share_type=stype_AS):
            try:
                m = Member.objects.get(name=s.name)
                if m.date_leave:
                    non_members.append(
                        "%s (%d) [ausgetreten %s]"
                        % (s.name, s.quantity, m.date_leave.strftime("%d.%m.%Y"))
                    )
            except Member.DoesNotExist:
                non_members.append("%s (%d)" % (s.name, s.quantity))
        if non_members:
            ret.append(
                {"info": "WARNUNG: Nichtmitglieder mit Anteilsscheinen:", "objects": non_members}
            )

    if not reference_date and hasattr(settings, "SHARE_PLOT") and settings.SHARE_PLOT:
        ret.append({"info": '<img src="/geno/share/overview/plot/" alt="Statistik">'})

    return render(
        request, "geno/messages.html", {"response": ret, "title": "Übersicht Beteiligungen"}
    )


@login_required
def member_overview_plot(request):
    if not request.user.has_perm("geno.canview_member_overview"):
        return unauthorized(request)

    if not (hasattr(settings, "SHARE_PLOT") and settings.SHARE_PLOT):
        raise Http404("Plot not found")

    # age_limits = (20,30,40,50,60,70,80,1000)

    changes = []
    for m in Member.objects.all():
        ## Age stat
        # if m.name.date_birth:
        #    born = m.name.date_birth
        #    today = datetime.date.today()
        #    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        #    for i,limit in enumerate(age_limits):
        #        if age < limit:
        #            age_stat['u%d' % limit] += 1
        #            break
        # else:
        #    age_stat['Unbekannt'] += 1

        changes.append({"date": m.date_join, "value": 1})
        if m.date_leave:
            changes.append({"date": m.date_leave, "value": -1})

    changes_sorted = sorted(changes, key=lambda x: x["date"])
    x = []
    y = []
    agg = 0
    for data in changes_sorted:
        if data["date"] > datetime.date.today():
            break
        x.append(data["date"])
        agg += data["value"]
        y.append(agg)

    fig = Figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    ax.plot(x, y, "b-")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Anzahl Mitglieder")
    ax.grid(axis="x", linestyle=":")
    ax.grid(axis="y", linestyle=":")
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    response = HttpResponse(output.getvalue(), content_type="image/png")
    output.close()
    return response


@login_required
def share_overview_boxplot(request):
    if not request.user.has_perm("geno.canview_share_overview"):
        return unauthorized(request)

    if not (hasattr(settings, "SHARE_PLOT") and settings.SHARE_PLOT):
        raise Http404("Plot not found")

    today = datetime.datetime.today()
    try:
        stype_DarlehenSpezial = ShareType.objects.get(name="Darlehen spezial")
    except ShareType.DoesNotExist:
        stype_DarlehenSpezial = None
    try:
        stype_Hypothek = ShareType.objects.get(name="Hypothek")
    except ShareType.DoesNotExist:
        stype_Hypothek = None

    ## Statisik: Beteiligung pro Typ und Mitglieder
    stat = []
    labels = []
    for share_type in ShareType.objects.exclude(name="Darlehen spezial").exclude(name="Hypothek"):
        stat_share = []
        for m in Member.objects.filter(Q(date_leave=None) | Q(date_leave__gt=today)):
            total = 0
            for s in get_active_shares().filter(name=m.name).filter(share_type=share_type):
                total += s.quantity * float(s.value)
            if total >= 1000:
                stat_share.append(total / 1000.0)
        labels.append("%s\nn=%d" % (share_type.name, len(stat_share)))
        stat.append(stat_share)

    ## Statistik: Beteiligung Total pro Mitglied
    count_below_threshold = 0
    stat_share = []
    for m in Member.objects.filter(Q(date_leave=None) | Q(date_leave__gt=today)):
        total = 0
        for s in (
            get_active_shares()
            .filter(name=m.name)
            .exclude(share_type=stype_DarlehenSpezial)
            .exclude(share_type=stype_Hypothek)
        ):
            total += s.quantity * float(s.value)
        if total >= 1000:
            stat_share.append(total / 1000.0)
        else:
            count_below_threshold += 1
    stat.append(stat_share)
    labels.append("%s\nn=%d" % ("Gesamt", len(stat_share)))

    ## Statistik: Beteiligung Nichtmitglieder
    stat_share = []
    for a in Address.objects.filter(active=True):
        try:
            m = Member.objects.get(name=a.id)
        except Member.DoesNotExist:
            total = 0
            for s in (
                get_active_shares()
                .filter(name=a.id)
                .exclude(share_type=stype_DarlehenSpezial)
                .exclude(share_type=stype_Hypothek)
            ):
                total += s.quantity * float(s.value)
            if total >= 1000:
                stat_share.append(total / 1000.0)
    stat.append(stat_share)
    labels.append("%s\nn=%d" % ("Nichtmitglieder", len(stat_share)))

    fig = Figure(figsize=(10, 7))
    ax = fig.add_subplot(111)
    ax.boxplot(stat, tick_labels=labels)
    ax.set_ylabel("Betrag (kFr.)")
    ax.axvline(5.5)
    ax.set_title(
        "Beteiligungen ab Fr. 1000.- von Mitgliedern und Nichtmitglieden "
        "(ohne Darlehen spez./Hypothek)\n"
        "(%d Mitglieder sind mit weniger als Fr. 1000.- beteiligt)\n"
        "Rot = Median, Box = Quartile (50%% der Daten), Linien = Min-Max ohne Ausreisser (1.5-IQR)"
        % count_below_threshold
    )
    ax.grid(axis="y", linestyle=":")
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    response = HttpResponse(output.getvalue(), content_type="image/png")
    output.close()
    return response


@login_required
def member_overview(request):
    if not request.user.has_perm("geno.canview_member_overview"):
        return unauthorized(request)

    ret = []
    stat = OrderedDict(
        [
            ("Total", 0),
            ("Frauen", 0),
            ("Männer", 0),
            ("Organisationen", 0),
            ("Andere/Unbekannt", 0),
        ]
    )

    # age_limits = (20,30,40,50,60,70,80,1000)
    age_limits = (30, 45, 60, 1000)
    age_stat = {}
    for limit in age_limits:
        age_stat["u%d" % limit] = 0
    age_stat["Unbekannt"] = 0

    date_mode = "strict"
    today = datetime.date.today()
    reference_date = today
    if request.GET.get("date", "") == "last_year":
        date_mode = "last_year"
        reference_date = datetime.date(today.year - 1, 12, 31)

    # for m in Member.objects.exclude(date_leave__isnull=False):
    for m in Member.objects.all():
        if is_member(m.name, date_mode=date_mode):
            stat["Total"] += 1

            ## Gender stat
            if m.name.title == "Org" or m.name.organization:
                stat["Organisationen"] += 1
            elif m.name.title == "Herr":
                stat["Männer"] += 1
            elif m.name.title == "Frau":
                stat["Frauen"] += 1
            else:
                stat["Andere/Unbekannt"] += 1

            ## Age stat
            if m.name.date_birth:
                born = m.name.date_birth
                age = (
                    reference_date.year
                    - born.year
                    - ((reference_date.month, reference_date.day) < (born.month, born.day))
                )
                for limit in age_limits:
                    if age < limit:
                        age_stat["u%d" % limit] += 1
                        break
            else:
                age_stat["Unbekannt"] += 1

    tot = stat["Total"]
    if tot > 0:
        obj = []
        for k, v in stat.items():
            obj.append("%s: %d (%d%%)" % (k, v, round(float(v) / float(tot) * 100.0)))
    else:
        obj = ["Keine Mitglieder gefunden"]

    ret.append({"info": "Mitgliederspiegel", "objects": obj})

    if tot > 0:
        obj = []
        last = 0
        for limit in age_limits:
            v = age_stat["u%d" % limit]
            if limit == 1000:
                obj.append("Über %d: %d (%d%%)" % (last, v, round(float(v) / float(tot) * 100.0)))
            else:
                obj.append(
                    "%d - %d: %d (%d%%)" % (last, limit, v, round(float(v) / float(tot) * 100.0))
                )
            last = limit
        if age_stat["Unbekannt"]:
            v = age_stat["Unbekannt"]
            obj.append("Unbekannt: %d (%d%%)" % (v, round(float(v) / float(tot) * 100.0)))

    ret.append({"info": "Altersverteilung", "objects": obj})

    if hasattr(settings, "SHARE_PLOT") and settings.SHARE_PLOT:
        ret.append({"info": '<img src="/geno/member/overview/plot/" alt="Statistik">'})

    return render(
        request, "geno/messages.html", {"response": ret, "title": "Übersicht Mitglieder"}
    )


@login_required
def member_list(request):
    if not request.user.has_perm("geno.canview_member"):
        return unauthorized(request)
    if "q" in request.GET:
        members = Member.objects.exclude(date_leave__isnull=False).filter(
            Q(name__organization__icontains=request.GET.get("q"))
            | Q(name__name__icontains=request.GET.get("q"))
            | Q(name__first_name__icontains=request.GET.get("q"))
            | Q(name__street_name__icontains=request.GET.get("q"))
            | Q(name__city_name__icontains=request.GET.get("q"))
            | Q(name__email__icontains=request.GET.get("q"))
            | Q(name__telephone__icontains=request.GET.get("q"))
            | Q(name__mobile__icontains=request.GET.get("q"))
            | Q(name__occupation__icontains=request.GET.get("q"))
        )
    else:
        members = Member.objects.exclude(date_leave__isnull=False)
    table = MemberTable(members)
    RequestConfig(request, paginate={"per_page": 50}).configure(table)
    return render(request, "geno/table.html", {"table": table})


@login_required
def member_list_admin(request):
    if not request.user.has_perm("geno.canview_billing"):
        return unauthorized(request)
    if "q" in request.GET:
        members = Member.objects.exclude(date_leave__isnull=False).filter(
            Q(name__organization__icontains=request.GET.get("q"))
            | Q(name__name__icontains=request.GET.get("q"))
            | Q(name__first_name__icontains=request.GET.get("q"))
            | Q(name__street_name__icontains=request.GET.get("q"))
            | Q(name__city_name__icontains=request.GET.get("q"))
            | Q(name__email__icontains=request.GET.get("q"))
            | Q(name__telephone__icontains=request.GET.get("q"))
            | Q(name__mobile__icontains=request.GET.get("q"))
            | Q(name__occupation__icontains=request.GET.get("q"))
            | Q(name__bankaccount__icontains=request.GET.get("q"))
        )
    else:
        members = Member.objects.exclude(date_leave__isnull=False)
    table = MemberTableAdmin(members)
    RequestConfig(request, paginate={"per_page": 50}).configure(table)
    return render(request, "geno/table.html", {"table": table})


@login_required
def address_export(request, show_wohnung=True):
    import openpyxl
    from openpyxl.styles import Font

    if not request.user.has_perm("geno.canview_member"):
        return unauthorized(request)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        "attachment; filename=%s_Adressen.xlsx" % settings.GENO_FILENAME_STR
    )
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Adressliste %s" % settings.GENO_FILENAME_STR

    row_num = 0

    ## Header
    columns = [
        ("A", "ID", 7),
        ("B", "Organisation", 18),
        ("C", "Name", 18),
        ("D", "Vorname", 15),
        ("E", "Anrede", 8),
        ("F", "Du/Sie", 7),
        ("G", "Adresszusatz", 22),
        ("H", "Adresse", 22),
        ("I", "PLZ Ort", 22),
        ("J", "Telefon", 15),
        ("K", "Mobile", 15),
        ("L", "Email", 25),
        ("M", "Geb.dat.", 15),
        ("N", "Heimatort", 20),
        ("O", "Beruf/Ausbildung", 40),
        ("P", "Mitglied seit", 15),
        ("Q", "Austritt", 15),
        ("R", geno_settings.MEMBER_FLAGS[1], 10),
        ("S", geno_settings.MEMBER_FLAGS[2], 10),
        ("T", geno_settings.MEMBER_FLAGS[3], 10),
        ("U", geno_settings.MEMBER_FLAGS[4], 10),
        ("V", geno_settings.MEMBER_FLAGS[5], 10),
        ("W", "Status Mitgliedschaft", 22),
        ("X", "Anteilschein bezahlt", 15),
    ]
    if show_wohnung:
        columns.append(("Y", "Wohnung", 15))
        columns.append(("Z", "Kinder", 25))
    for col_num in range(len(columns)):
        c = ws.cell(row=row_num + 1, column=col_num + 1)
        c.value = columns[col_num][1]
        c.font = Font(bold=True)
        # set column width
        ws.column_dimensions[columns[col_num][0]].width = columns[col_num][2]

    ## Data
    try:
        matt_type = MemberAttributeType.objects.get(name="Status Mitgliedschaft")
    except:
        matt_type = None
    try:
        stype01 = ShareType.objects.get(name="Anteilschein Einzelmitglied")
    except:
        stype01 = None
    for a in Address.objects.filter(active=True):
        row = []
        row.append(a.pk)
        row.append(a.organization)
        row.append(a.name)
        row.append(a.first_name)
        row.append(a.title)
        row.append(a.formal)
        row.append(a.extra)
        row.append(a.street)
        row.append(a.city)
        row.append(a.telephone)
        row.append(a.mobile)
        row.append(a.email)
        row.append(a.date_birth)
        row.append(a.hometown)
        row.append(a.occupation)
        date_join = ""
        date_leave = ""
        flag_01 = ""
        flag_02 = ""
        flag_03 = ""
        flag_04 = ""
        flag_05 = ""
        status = ""
        share01_paid = ""
        wohnung = ""
        kinder = ""
        try:
            m = Member.objects.get(name=a)
            if m.date_leave:
                date_leave = m.date_leave
                # date_join = m.date_join
            else:
                date_join = m.date_join
            if m.flag_01:
                flag_01 = "X"
            else:
                flag_01 = "--"
            if m.flag_02:
                flag_02 = "X"
            else:
                flag_02 = "--"
            if m.flag_03:
                flag_03 = "X"
            else:
                flag_03 = "--"
            if m.flag_04:
                flag_04 = "X"
            else:
                flag_04 = "--"
            if m.flag_05:
                flag_05 = "X"
            else:
                flag_05 = "--"
            if matt_type:
                matt = MemberAttribute.objects.filter(member=m, attribute_type=matt_type).first()
                if matt:
                    status = matt.value
        except Member.DoesNotExist:
            pass

        if stype01:
            share = get_active_shares().filter(share_type=stype01).filter(name=a).first()
            if share:
                share01_paid = share.date.strftime("%d.%m.%Y")

        if show_wohnung:
            for c in get_active_contracts().filter(contractors__pk=a.pk):
                for child in c.children.all():
                    if kinder == "":
                        kinder = "%s %s (%s)" % (
                            child.name.first_name,
                            child.name.name,
                            child.age(precision=0),
                        )
                    else:
                        kinder = "%s, %s %s (%s)" % (
                            kinder,
                            child.name.first_name,
                            child.name.name,
                            child.age(precision=0),
                        )
                for w in c.rental_units.exclude(rental_type="Kellerabteil"):
                    if wohnung == "":
                        wohnung = w.name
                    else:
                        wohnung = "%s/%s" % (wohnung, w.name)
        row.append(date_join)
        row.append(date_leave)
        row.append(flag_01)
        row.append(flag_02)
        row.append(flag_03)
        row.append(flag_04)
        row.append(flag_05)
        row.append(status)
        row.append(share01_paid)
        if show_wohnung:
            row.append(wohnung)
            row.append(kinder)

        row_num += 1
        for col_num in range(len(row)):
            c = ws.cell(row=row_num + 1, column=col_num + 1)
            c.value = row[col_num]

    wb.save(response)
    return response


@login_required
def share_export(request):
    import openpyxl
    from openpyxl.styles import Font

    if not request.user.has_perm("geno.canview_share"):
        return unauthorized(request)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        "attachment; filename=%s_Beteiligungen.xlsx" % settings.GENO_FILENAME_STR
    )
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Beteiligungen %s" % settings.GENO_FILENAME_STR

    row_num = 0

    ## Header
    if request.GET.get("aggregate", "") == "yes":
        columns = [
            ("A", "Name", 30),
            ("B", "Typ", 20),
            ("C", "Anzahl", 8),
            ("D", "Summe CHF", 12),
            ("E", "Fälligkeit", 10),
            ("F", "Laufzeit", 8),
            ("G", "Mitgliedschaft", 30),
        ]
    else:
        columns = [
            ("A", "ID", 7),
            ("B", "Name", 30),
            ("C", "Adress-ID", 10),
            ("D", "Typ", 20),
            ("E", "Datum", 12),
            ("F", "Anzahl", 8),
            ("G", "Betrag CHF", 12),
            ("H", "Summe CHF", 12),
            ("I", "Zinssatz-Modus", 10),
            ("J", "Zinssatz", 10),
            ("K", "Zins?", 8),
            ("L", "Zusatzinfo", 30),
            ("M", "Erstellt", 22),
            ("N", "Geändert", 22),
        ]
    for col_num in range(len(columns)):
        c = ws.cell(row=row_num + 1, column=col_num + 1)
        c.value = columns[col_num][1]
        c.font = Font(bold=True)
        # set column width
        ws.column_dimensions[columns[col_num][0]].width = columns[col_num][2]

    ## Data
    today = datetime.datetime.today()
    if request.GET.get("jahresende", "") == "yes":
        valuta_date = datetime.date(today.year - 1, 12, 31)
    else:
        valuta_date = today
    if request.GET.get("anonymous", "") == "yes":
        anonymous = True
    else:
        anonymous = False
    person_count = 0
    person_nr = {}
    if request.GET.get("aggregate", "") == "yes":
        last = None
        row = []
        for a in get_active_shares(date=valuta_date).order_by("share_type", "name", "date"):
            if a.date_due:
                duedate = a.date_due
            elif a.duration:
                duedate = a.date + relativedelta(years=a.duration)
            else:
                duedate = ""

            if last == str(a.name) + str(a.share_type) + str(duedate):
                ## Update row
                row[2] += a.quantity
                row[3] += a.quantity * a.value
            else:
                ## Insert row
                if last is not None:
                    row_num += 1
                    for col_num in range(len(row)):
                        c = ws.cell(row=row_num + 1, column=col_num + 1)
                        c.value = row[col_num]
                row = []
                # row.append(a.pk)
                if anonymous:
                    if a.name.pk not in person_nr:
                        person_count += 1
                        person_nr[a.name.pk] = "Person %s" % person_count
                    person_name = person_nr[a.name.pk]
                else:
                    person_name = str(a.name)
                row.append(person_name)
                row.append(str(a.share_type))
                row.append(a.quantity)
                row.append(a.quantity * a.value)
                row.append(duedate)
                row.append(a.duration)
                if is_member(a.name):
                    row.append("Ja")
                else:
                    row.append("Nein")
            last = str(a.name) + str(a.share_type) + str(duedate)
        if last is not None:
            row_num += 1
            for col_num in range(len(row)):
                c = ws.cell(row=row_num + 1, column=col_num + 1)
                c.value = row[col_num]
    else:
        for a in get_active_shares(date=valuta_date).order_by("-date"):
            row = []
            row.append(a.pk)
            row.append(str(a.name))
            row.append(a.name.pk)
            row.append(str(a.share_type))
            row.append(a.date)
            row.append(a.quantity)
            row.append(a.value)
            row.append(a.quantity * a.value)
            row.append(a.interest_mode)
            row.append(a.interest())
            if a.is_interest_credit:
                row.append(1)
            else:
                row.append(0)
            row.append(a.note)
            row.append(timezone.localtime(a.ts_created).strftime("%Y-%m-%d %H:%M"))
            row.append(timezone.localtime(a.ts_modified).strftime("%Y-%m-%d %H:%M"))
            row_num += 1
            for col_num in range(len(row)):
                c = ws.cell(row=row_num + 1, column=col_num + 1)
                c.value = row[col_num]

    wb.save(response)
    return response


@login_required
def transaction_invoice(request):
    if not request.user.has_perm("geno.transaction"):
        return unauthorized(request)

    if request.method == "POST":
        form = TransactionFormInvoice(request.POST)
        if form.is_valid():
            # Process transaction
            invoice = form.cleaned_data["invoice"]
            if form.cleaned_data["amount"]:
                amount = form.cleaned_data["amount"]
            else:
                amount = invoice.amount
            ret = pay_invoice(invoice, form.cleaned_data["date"], amount)
            if ret:
                messages.error(
                    request, "Zahlung von %s konnte nicht gebucht werden: %s" % (invoice, ret)
                )
            else:
                messages.success(request, "Zahlung gebucht: %s [%.2f]" % (invoice, amount))
                form = TransactionFormInvoice(initial={"date": form.cleaned_data["date"]})
    else:
        form = TransactionFormInvoice()  # initial={'transaction': default_transaction})
    return render(
        request,
        "geno/transaction.html",
        {"form": form, "form_action": "/geno/transaction_invoice/"},
    )


@login_required
def transaction(request):
    if not request.user.has_perm("geno.transaction"):
        return unauthorized(request)

    error = False
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            # Process transaction
            if form.cleaned_data["transaction"][0:3] == "fee":
                fee_year = form.cleaned_data["transaction"][3:]
                try:
                    att_type = MemberAttributeType.objects.get(
                        name="Mitgliederbeitrag %s" % fee_year
                    )
                except MemberAttributeType.DoesNotExist:
                    error = True
                    messages.error(
                        request,
                        "Mitglieder Attribut 'Mitgliederbeitrag %s' existiert nicht." % fee_year,
                    )
                if not error:
                    member = Member.objects.filter(name=form.cleaned_data["name"])
                    if len(member) != 1:
                        error = True
                        messages.error(
                            request,
                            "Member not found or not unique: %s" % form.cleaned_data["name"],
                        )
                    else:
                        att = MemberAttribute.objects.filter(
                            member=member[0], attribute_type=att_type
                        )
                        for a in att:
                            messages.info(
                                request,
                                "Mitglieder Attribut gefunden: %s - %s" % (a.date, a.value),
                            )
                        if len(att) == 0:
                            ## Create new attribute
                            att = MemberAttribute(member=member[0], attribute_type=att_type)
                        elif len(att) == 1:
                            att = att[0]
                            if att.value.startswith("Bezahlt"):
                                error = True
                                messages.error(request, "Schon als bezahlt markiert")
                            elif (
                                att.value != "Mail-Rechnung geschickt"
                                and att.value != "Mail-Reminder geschickt"
                                and att.value != "Rechnung geschickt"
                                and att.value != "Gefordert"
                                and att.value != "Brief-Rechnung geschickt"
                                and att.value != "Brief-Reminder geschickt"
                                and att.value != "Brief-Mahnung geschickt"
                                and att.value != "Brief-Mahnung2 geschickt"
                            ):
                                error = True
                                messages.error(request, "Unknown attribute value")
                        else:
                            error = True
                            messages.error(request, "More than one attribute found")
                if not error and settings.GNUCASH:
                    ## Add transaction to GnuCash
                    msg = "Undefined"
                    try:
                        book = open_book(
                            uri_conn=settings.GNUCASH_DB_SECRET,
                            readonly=settings.GNUCASH_READONLY,
                            do_backup=False,
                        )
                        to_account = book.accounts(
                            code=geno_settings.GNUCASH_ACC_POST
                        )  # Aktiven:Umlaufvermögen:Flüssige Mittel:Postkonto
                        from_account = book.accounts(
                            code=geno_settings.GNUCASH_ACC_MEMBER_FEE
                        )  # Ertrag aus Leistungen:Mitgliederbeiträge")
                        amount = Decimal("80.00")
                        t = Transaction(
                            post_date=form.cleaned_data["date"],
                            enter_date=datetime.datetime.now(),
                            currency=book.currencies(mnemonic="CHF"),
                            description="Mitgliederbeitrag %s %s" % (fee_year, member[0]),
                            splits=[
                                Split(account=to_account, value=amount, memo=""),
                                Split(account=from_account, value=-amount, memo=""),
                            ],
                        )
                        msg = "CHF %s, %s [%s > %s]" % (
                            amount,
                            t.description,
                            from_account.name,
                            to_account.name,
                        )
                        book.save()
                        book.close()
                    except Exception as e:
                        error = True
                        messages.error(request, "Could not create Gnucash transaction: %s" % e)
                    if not error:
                        messages.success(request, "Added GnuCash transaction: %s" % (msg))
                    else:
                        with contextlib.suppress(builtins.BaseException):
                            book.close()
                if not error:
                    ## Update/add attribute
                    att.value = "Bezahlt"
                    att.date = form.cleaned_data["date"]
                    att.save()
                    messages.success(
                        request,
                        "Mitglieder Attribut hinzugefügt/aktualisiert: %s - %s [%s]"
                        % (att.date, att.value, att.member),
                    )
            elif form.cleaned_data["transaction"] in (
                "as_single",
                "as_extra",
                "as_founder",
                "development",
            ):
                if form.cleaned_data["transaction"] == "development":
                    count = 1
                    value = form.cleaned_data["amount"]
                    share_type = "Entwicklungsbeitrag"
                elif (
                    form.cleaned_data["amount"]
                    and float(form.cleaned_data["amount"]) % 200.00 == 0.0
                ):
                    value = 200
                    count = int(form.cleaned_data["amount"] / value)
                    if form.cleaned_data["transaction"] == "as_single":
                        share_type = "Anteilschein Einzelmitglied"
                    elif form.cleaned_data["transaction"] == "as_founder":
                        share_type = "Anteilschein Gründungsmitglied"
                    else:
                        share_type = "Anteilschein freiwillig"
                else:
                    error = True
                    messages.error(request, "Betrag ist kein Vielfaches von 200.-!")
                if not error:
                    share = Share(
                        name=form.cleaned_data["name"],
                        share_type=ShareType.objects.get(name=share_type),
                        state="bezahlt",
                        date=form.cleaned_data["date"],
                        quantity=count,
                        value=value,
                    )
                    share.save()
                    messages.info(
                        request,
                        "%sx CHF %s %s hinzugefügt - %s [%s]"
                        % (
                            count,
                            value,
                            share_type,
                            form.cleaned_data["date"],
                            form.cleaned_data["name"],
                        ),
                    )
            else:
                if form.cleaned_data["amount"]:
                    if len(form.cleaned_data["note"]):
                        note = form.cleaned_data["note"]
                    else:
                        note = None
                    ret_error = process_transaction(
                        form.cleaned_data["transaction"],
                        form.cleaned_data["date"],
                        form.cleaned_data["name"],
                        form.cleaned_data["amount"],
                        None,
                        note,
                    )
                    info = "%s: %s CHF %s [%s]" % (
                        form.cleaned_data["transaction"],
                        form.cleaned_data["date"],
                        form.cleaned_data["amount"],
                        form.cleaned_data["name"],
                    )
                    if not ret_error:
                        messages.success(request, "Buchung ausgeführt: %s" % (info))
                    else:
                        error = True
                        messages.error(
                            request, "FEHLER bei der Buchung: %s -- %s" % (info, ret_error)
                        )
                else:
                    error = True
                    messages.error(request, "Kein Betrag angegeben!")
    else:
        now = datetime.datetime.now()
        if now.month < 6:
            default_transaction = "fee%s" % (now.year - 1)
        else:
            default_transaction = "fee%s" % now.year
        form = TransactionForm(initial={"transaction": default_transaction})
    return render(
        request,
        "geno/transaction.html",
        {"form": form, "form_action": "/geno/transaction/", "error": error},
    )


@login_required
def invoice(request, action="create", key=None, key_type=None, consolidate=True):
    if not request.user.has_perm("geno.transaction"):
        return unauthorized(request)

    if action in ("overview", "detail"):
        if "invoice_filter" not in request.session or request.GET.get("reset_filter", "0") == "1":
            request.session["invoice_filter"] = {"category_filter": "_all"}
            if request.GET.get("reset_filter", "0") == "1":
                ## Reload to get rid of get request argument
                return HttpResponseRedirect(request.path)
        initial = request.session["invoice_filter"].copy()
        if action == "detail":
            if "search_detail" in initial:
                initial["search"] = initial["search_detail"]
            else:
                initial["search"] = ""
        if request.POST:
            form = InvoiceFilterForm(request.POST)
            if form.is_valid():
                if action == "detail":
                    request.session["invoice_filter"]["search_detail"] = form.cleaned_data[
                        "search"
                    ]
                else:
                    request.session["invoice_filter"]["search"] = form.cleaned_data["search"]
                request.session["invoice_filter"]["category_filter"] = form.cleaned_data[
                    "category_filter"
                ]
                request.session["invoice_filter"]["show_consolidated"] = form.cleaned_data[
                    "show_consolidated"
                ]
                if form.cleaned_data["date_from"]:
                    date_from = form.cleaned_data["date_from"].strftime("%d.%m.%Y")
                else:
                    date_from = ""
                if form.cleaned_data["date_to"]:
                    date_to = form.cleaned_data["date_to"].strftime("%d.%m.%Y")
                else:
                    date_to = ""
                request.session["invoice_filter"]["date_from"] = date_from
                request.session["invoice_filter"]["date_to"] = date_to
        else:
            form = InvoiceFilterForm(initial=initial)

    if action == "overview":
        if request.POST.get("consolidate"):
            consolidate_invoices()
        data = invoice_overview(request.session["invoice_filter"])
        table = InvoiceOverviewTable(data)
        table.order_by = "-total"
        RequestConfig(request, paginate={"per_page": 100}).configure(table)
        return render(
            request,
            "geno/table.html",
            {"title": "Debitoren Übersicht", "table": table, "form": form, "invoice_table": True},
        )
    elif action == "detail":
        # print(key_type)
        # print(key)
        if key_type == "c":
            obj = Contract.objects.get(pk=key)
        else:
            obj = Address.objects.get(pk=key)
        if request.POST.get("consolidate"):
            consolidate_invoices(obj)
        data = invoice_detail(obj, request.session["invoice_filter"])
        table = InvoiceDetailTable(data)
        RequestConfig(request, paginate={"per_page": 100}).configure(table)
        return render(
            request,
            "geno/table.html",
            {
                "title": "Detailansicht: %s" % (obj),
                "table": table,
                "form": form,
                "invoice_table": True,
                "breadcrumbs": [
                    {"name": "Debitoren Übersicht", "href": "/geno/invoice/overview/"}
                ],
            },
        )
    elif action in ("create", "download"):
        ret = []

        if action == "download":
            if key_type != "contract":
                raise RuntimeError("invoice(): Key type %s not implemented yet!" % key_type)
            ## Just download PDF of invoices for this contract
            download_only = key
            dry_run = True
        else:
            download_only = None
            if request.GET.get("dry_run") == "False":
                dry_run = False
            else:
                dry_run = True

        today = datetime.date.today()
        reference_date = datetime.date(today.year, today.month, 1)
        if request.GET.get("date", "") == "last_month":
            if today.month == 1:
                reference_date = datetime.date(today.year - 1, 12, 1)
            else:
                reference_date = datetime.date(today.year, today.month - 1, 1)
        elif request.GET.get("date", "") == "next_month":
            if today.month == 12:
                reference_date = datetime.date(today.year + 1, 1, 1)
            else:
                reference_date = datetime.date(today.year, today.month + 1, 1)
        elif len(request.GET.get("date", "")) == 10:
            reference_date = datetime.datetime.strptime(request.GET.get("date"), "%Y-%m-%d").date()

        ret.append(
            {
                "info": "Optionen:",
                "objects": ["Dry-run: %s" % dry_run, "Referenzdatum: %s" % reference_date],
            }
        )

        invoices = create_invoices(
            dry_run, reference_date, request.GET.get("single_contract", None), download_only
        )
        if isinstance(invoices, str):
            pdf_file = open("/tmp/%s" % invoices, "rb")
            resp = FileResponse(pdf_file, content_type="application/pdf")
            resp["Content-Disposition"] = "attachment; filename=%s" % invoices
            return resp
        if dry_run:
            invoices.append(
                "DRY-RUN: Zum effektiv ausführen, hier klicken: "
                '<a href="?dry_run=False&date=%s">AUSFÜHREN</a>.' % request.GET.get("date", "")
            )
        ret.append({"info": "GnuCash Rechnungen erstellen:", "objects": invoices})
        return render(
            request, "geno/messages.html", {"response": ret, "title": "Rechnungen erstellen"}
        )
    else:
        raise RuntimeError("Invoice action %s not implemented." % action)


## TODO: Refactor to ClassBased view
@login_required
def check_payments(request):
    if not request.user.has_perm("geno.canview_billing"):
        return unauthorized(request)

    ret = []

    now = datetime.datetime.now()
    members = Member.objects.exclude(date_leave__isnull=False)
    for member in members:
        warn = []
        ## Check if member has at least one share:
        if (
            get_active_shares()
            .filter(name=member.name)
            .filter(share_type=ShareType.objects.get(name="Anteilschein"))
            .count()
            < 1
        ):
            warn.append("Mitglied hat keine Anteilscheine (Beitritt: %s)." % member.date_join)
        ## Check if entry fee is paid:
        if member.date_join > datetime.date(2015, 1, 1):
            if (
                MemberAttribute.objects.filter(member=member)
                .filter(Q(value="Bezahlt (mit Eintritt)") | Q(value="Erlass (mit Eintritt)"))
                .count()
                < 1
            ):
                warn.append(
                    "Mitglied hat evtl. Eintrittsgebühr noch nicht bezahlt (Beitritt: %s)."
                    % member.date_join
                )

        ## Check membership fees
        for year in range(geno_settings.CHECK_MEMBERFEE_STARTYEAR, now.year):
            try:
                attribute = MemberAttributeType.objects.get(name="Mitgliederbeitrag %d" % year)
            except MemberAttributeType.DoesNotExist:
                continue
            if member.date_join < datetime.date(year, 1, 1):
                paid = (
                    MemberAttribute.objects.filter(member=member)
                    .filter(attribute_type=attribute)
                    .count()
                )
                if paid < 1:
                    warn.append("Mitgliedergebühr %d noch offen." % year)
                elif paid > 1:
                    warn.append("Mitgliedergebühr %d %d-fach bezahlt!" % (year, paid))
        if warn:
            doc = (
                Document.objects.filter(object_id=member.pk)
                .filter(content_type=ContentType.objects.get(app_label="geno", model="member"))
                .order_by("-ts_created")[0:1]
            )
            if doc:
                warn.append("Neustes Dokument: %s" % doc[0])
            ret.append({"info": str(member), "objects": warn})

    return render(request, "geno/messages.html", {"response": ret, "title": "Check Zahlungen"})


@login_required
def share_confirm(request):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    ## Find shares without documents (ignore single AS)
    stype_share = ShareType.objects.get(name="Anteilschein")
    try:
        stype_hypo = ShareType.objects.get(name="Hypothek")
    except ShareType.DoesNotExist:
        stype_hypo = None
    objects = []
    for s in (
        get_active_shares(interest=False)
        .filter(date__gt=datetime.date(2018, 7, 1))
        .exclude(share_type=stype_hypo)
        .order_by("-date")
    ):
        obj_data = {"obj": s, "info": "%s %dx %s" % (s.date, s.quantity, s.value)}
        if s.share_type == stype_share:
            obj_data["doctype"] = "shareconfirm"
            obj_data["info"] = "%s [Best. Anteilschein]" % obj_data["info"]
        doc = (
            Document.objects.filter(object_id=s.pk)
            .filter(content_type=ContentType.objects.get(app_label="geno", model="share"))
            .filter(doctype__name__startswith="shareconfirm")
        )
        if doc.count() == 0:
            objects.append(obj_data)
    options = {
        "beschreibung": "Bestätigungen Einzahlung Beteiligung",
        "link_url": "/geno/share/confirm",
    }
    return create_documents(request, "shareconfirm_req", objects, options)


@login_required
def member_confirm(request, doctype=None):
    if not request.user.has_perm("geno.add_document"):
        return unauthorized(request)

    if not doctype:
        raise ValueError("Missing doctype!")

    ## Find members with missing documents (after 2020-01-01)
    objects = []
    for m in Member.objects.filter(date_join__gt=datetime.date(2020, 1, 1)).exclude(
        date_leave__isnull=False
    ):
        doc = (
            Document.objects.filter(object_id=m.pk)
            .filter(content_type=ContentType.objects.get(app_label="geno", model="member"))
            .filter(doctype__name=doctype)
        )
        if doc.count() == 0:
            objects.append(
                {
                    "obj": m,
                    "doctype": doctype,
                    "info": "%s, Beitritt %s" % (m, m.date_join.strftime("%d.%m.%Y")),
                }
            )
    options = {
        "beschreibung": "Fehlende Dokumente erzeugen: %s" % doctype,
        "link_url": "/geno/member/confirm/%s/" % doctype,
    }
    return create_documents(request, doctype, objects, options)


## TODO: Refactor to ClassBased view
@login_required
def share_interest_transactions(request):
    if (
        not request.user.has_perm("geno.canview_share")
        or not request.user.has_perm("geno.canview_billing")
        or not request.user.has_perm("geno.transaction")
    ):
        return unauthorized(request)

    year_current = datetime.datetime.now().year
    year = year_current - 1

    stype_deposit = ShareType.objects.get(name="Depositenkasse")

    ret = []

    ## Try to guess if transactions have already been made
    count = (
        Share.objects.filter(is_interest_credit=True)
        .filter(date=datetime.date(year, 12, 31))
        .count()
    )
    if count:
        ret.append(
            {
                "info": "FEHLER: Es sieht so aus als ob die Zinsbuchungen schon ausgeführt "
                "wurden (%d Zins-Beteiligungen gefunden). Bitte überprüfen!" % count
            }
        )

    ## Open GnuCash book
    try:
        messages = []
        book = get_book(messages)
        if not book:
            raise Exception(messages[-1])
        acc_zins_darlehen = book.accounts(
            code=geno_settings.GNUCASH_ACC_INTEREST_LOAN
        )  ## Zinsaufwand Darlehen
        # print acc_zins_darlehen
        acc_zins_depositen = book.accounts(
            code=geno_settings.GNUCASH_ACC_INTEREST_DEPOSIT
        )  ## Zinsaufwand Depositenkasse
        # print acc_zins_depositen
        acc_verbindl_geno = book.accounts(
            code=geno_settings.GNUCASH_ACC_SHARES_INTEREST
        )  ## Verbindlichkeiten aus Finanzierung
        # print acc_verbindl_geno
        acc_verbindl_tax = book.accounts(
            code=geno_settings.GNUCASH_ACC_SHARES_INTEREST_TAX
        )  ## Verbindlichkeiten aus Verrechnungssteuer
        # print acc_verbindl_tax
        acc_depositen = book.accounts(
            code=geno_settings.GNUCASH_ACC_SHARES_DEPOSIT
        )  ## Depositenkasse
        # print acc_depositen
    except Exception as e:
        with contextlib.suppress(builtins.BaseException):
            book.close()
        ret.append(
            {
                "info": "FEHLER: Konnte GnuCash DB nicht öffnen oder Konten nicht finden! %s"
                % str(e)
            }
        )
        return render(
            request,
            "geno/messages.html",
            {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
        )

    ## Create transactions
    new_shares = []
    for adr in Address.objects.filter(active=True).order_by("name"):
        obj = []
        try:
            interest = share_interest_calc(adr, year)
        except Exception as e:
            ret.append({"info": "FEHLER bei der Zinsberechnung: %s" % str(e)})
            ret.append({"info": "Verarbeitung abgebrochen. Keine Änderungen gespeichert."})
            return render(
                request,
                "geno/messages.html",
                {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
            )
        if interest["total"][2] > 0:
            ## Darlehen normal
            interest_rate = interest["dates"][2][0]["interest_rate"]
            try:
                info = "Zinsgutschrift Darlehen: %s" % nformat(interest["total"][2])
                if interest["tax"][2] > 0:
                    info += " (VSt. %s -> Netto %s)" % (
                        nformat(interest["tax"][2]),
                        nformat(interest["pay"][2]),
                    )
                obj.append(info)
                if settings.GNUCASH:
                    t = Transaction(
                        post_date=datetime.date(year, 12, 31),
                        enter_date=datetime.datetime.now(),
                        currency=book.currencies(mnemonic="CHF"),
                        description="Zins %s%% auf Darlehen %d %s"
                        % (nformat(interest_rate), year, adr),
                    )
                    Split(
                        account=acc_zins_darlehen,
                        value=interest["total"][2],
                        memo="",
                        transaction=t,
                    )
                    Split(
                        account=acc_verbindl_geno,
                        value=-interest["pay"][2],
                        memo="",
                        transaction=t,
                    )
                    if interest["tax"][2] > 0:
                        Split(
                            account=acc_verbindl_tax,
                            value=-interest["tax"][2],
                            memo="",
                            transaction=t,
                        )
            except Exception as e:
                with contextlib.suppress(builtins.BaseException):
                    book.close()
                obj.append(str(e))
                ret.append(
                    {
                        "info": "%s: FEHLER: Konnte Transaktion nicht erstellen!" % adr,
                        "objects": obj,
                    }
                )
                ret.append({"info": "Verarbeitung abgebrochen. Keine Änderungen gespeichert."})
                return render(
                    request,
                    "geno/messages.html",
                    {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
                )

        if interest["total"][4] > 0:
            ## Darlehen spezial
            interest_rate = interest["dates"][4][0]["interest_rate"]
            try:
                info = "Zinsgutschrift Darlehen: %s" % nformat(interest["total"][4])
                if interest["tax"][4] > 0:
                    info += " (VSt. %s -> Netto %s)" % (
                        nformat(interest["tax"][4]),
                        nformat(interest["pay"][4]),
                    )
                obj.append(info)
                if settings.GNUCASH:
                    t = Transaction(
                        post_date=datetime.date(year, 12, 31),
                        enter_date=datetime.datetime.now(),
                        currency=book.currencies(mnemonic="CHF"),
                        description="Zins %s%% auf Darlehen %d %s"
                        % (nformat(interest_rate), year, adr),
                    )
                    Split(
                        account=acc_zins_darlehen,
                        value=interest["total"][4],
                        memo="",
                        transaction=t,
                    )
                    Split(
                        account=acc_verbindl_geno,
                        value=-interest["pay"][4],
                        memo="",
                        transaction=t,
                    )
                    if interest["tax"][4] > 0:
                        Split(
                            account=acc_verbindl_tax,
                            value=-interest["tax"][4],
                            memo="",
                            transaction=t,
                        )
            except Exception as e:
                with contextlib.suppress(builtins.BaseException):
                    book.close()
                obj.append(str(e))
                ret.append(
                    {
                        "info": "%s: FEHLER: Konnte Transaktion nicht erstellen!" % adr,
                        "objects": obj,
                    }
                )
                ret.append({"info": "Verarbeitung abgebrochen. Keine Änderungen gespeichert."})
                return render(
                    request,
                    "geno/messages.html",
                    {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
                )

        if interest["total"][3] > 0:
            ## Depositenkasse
            interest_rate = interest["dates"][3][0]["interest_rate"]
            try:
                info = "Zinsgutschrift Depositenkasse: %s" % nformat(interest["total"][3])
                if interest["tax"][3] > 0:
                    info += " (VSt. %s -> Netto %s)" % (
                        nformat(interest["tax"][3]),
                        nformat(interest["pay"][3]),
                    )
                obj.append(info)
                if settings.GNUCASH:
                    t = Transaction(
                        post_date=datetime.date(year, 12, 31),
                        enter_date=datetime.datetime.now(),
                        currency=book.currencies(mnemonic="CHF"),
                        description="Zins %s%% auf Depositenkasse %d %s"
                        % (nformat(interest_rate), year, adr),
                    )
                    Split(
                        account=acc_zins_depositen,
                        value=interest["total"][3],
                        memo="",
                        transaction=t,
                    )
                    Split(account=acc_depositen, value=-interest["pay"][3], memo="", transaction=t)
                    if interest["tax"][3] > 0:
                        Split(
                            account=acc_verbindl_tax,
                            value=-interest["tax"][3],
                            memo="",
                            transaction=t,
                        )
            except Exception as e:
                with contextlib.suppress(builtins.BaseException):
                    book.close()
                obj.append(str(e))
                ret.append(
                    {
                        "info": "%s: FEHLER: Konnte Transaktion nicht erstellen!" % adr,
                        "objects": obj,
                    }
                )
                ret.append({"info": "Verarbeitung abgebrochen. Keine Änderungen gespeichert."})
                return render(
                    request,
                    "geno/messages.html",
                    {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
                )

            try:
                new_shares.append(
                    Share(
                        name=adr,
                        share_type=stype_deposit,
                        date=datetime.date(year, 12, 31),
                        quantity=1,
                        value=interest["pay"][3],
                        is_interest_credit=True,
                        state="bezahlt",
                        note="Bruttozinsen %s%% Depositenkasse %d"
                        % (nformat(interest_rate), year),
                    )
                )
                obj.append(
                    "Erzeuge Zins-Beteiligung Depositenkasse (%s, %s)"
                    % (nformat(interest["pay"][3]), nformat(interest_rate))
                )
            except Exception as e:
                with contextlib.suppress(builtins.BaseException):
                    book.close()
                obj.append(str(e))
                ret.append(
                    {
                        "info": "%s: FEHLER: Konnte Zins-Beteiligung nicht erstellen!" % adr,
                        "objects": obj,
                    }
                )
                ret.append({"info": "Verarbeitung abgebrochen. Keine Änderungen gespeichert."})
                return render(
                    request,
                    "geno/messages.html",
                    {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
                )
        if obj:
            ret.append({"info": str(adr), "objects": obj})

    ## Commit transactions
    try:
        book.save()
    except Exception as e:
        ret.append(
            {
                "info": "FEHLER BEIM SPEICHERN: Konnte GnuCash Transaktionen nicht speichen! %s"
                % str(e)
            }
        )
        return render(
            request,
            "geno/messages.html",
            {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
        )
    ret.append({"info": "GnuCash Transaktionen GESPEICHERT!"})

    try:
        for s in new_shares:
            s.save()
    except Exception as e:
        ret.append(
            {
                "info": "FEHLER BEIM SPEICHERN: Konnte Zins-Beteiligungen nicht speichen! %s"
                % str(e)
            }
        )
        return render(
            request,
            "geno/messages.html",
            {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
        )
    ret.append({"info": "Zins-Beteiligungen GESPEICHERT!"})

    try:
        book.close()
    except Exception as e:
        ret.append(
            {
                "info": "WARNUNG: Konnte GnuCash Buchhaltung nicht ordnungsgemäss schliessen! %s"
                % str(e)
            }
        )

    return render(
        request,
        "geno/messages.html",
        {"response": ret, "title": "Zinsabrechnung %d buchen" % year},
    )


@login_required
def share_interest_download(request):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    year_current = datetime.datetime.now().year
    year = year_current - 1

    if request.GET.get("darlehen", "") == "yes":
        opt_darlehen = True
        output_tag = "Darlehenszins"
    else:
        opt_darlehen = False
        output_tag = "Zinsabrechnung"

    ## Spreadsheet
    import openpyxl
    from openpyxl.styles import Font

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=%s_%s_%d.xlsx" % (
        settings.GENO_FILENAME_STR,
        output_tag,
        year,
    )
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "%s %s %s" % (settings.GENO_FILENAME_STR, output_tag, year)
    ## Header
    columns = [
        ("A", "Name", 30),
        ("B", "Typ", 20),
        ("C", "Datum", 25),
        ("D", "Saldo CHF", 12),
        ("E", "Tage", 8),
        ("F", "Satz", 8),
        ("G", "Bruttozins", 12),
        ("H", "Zins Total", 12),
        ("I", "Steuerfrei", 12),
        ("J", "VSt. 35%", 12),
        ("K", "Gutschrift", 12),
    ]
    row_num = 0
    for col_num in range(len(columns)):
        c = ws.cell(row=row_num + 1, column=col_num + 1)
        c.value = columns[col_num][1]
        c.font = Font(bold=True)
        # set column width
        ws.column_dimensions[columns[col_num][0]].width = columns[col_num][2]
    row_num += 2

    sum_interest = 0
    sum_interest_notax = 0
    sum_interest_tax = 0
    sum_interest_pay = 0
    count = 0
    for adr in Address.objects.filter(active=True).order_by("name"):
        try:
            interest = share_interest_calc(adr, year)
        except Exception as e:
            messages.error(request, "FEHLER bei der Zinsberechnung: %s" % str(e))
            return HttpResponseRedirect("/admin/")
        darlehen_spezial = ""
        if opt_darlehen:
            ## Only sum of Darlehen
            total = interest["total"][2] + interest["total"][4]
            tax = interest["tax"][2] + interest["tax"][4]
            pay = interest["pay"][2] + interest["pay"][4]
            if interest["total"][4] > 0:
                darlehen_spezial = "/SPEZIAL"
        else:
            ## All
            total = interest["total_alltypes"]
            tax = interest["tax_alltypes"]
            pay = interest["pay_alltypes"]

        if total > 0:
            if total == pay:
                notax = pay
            else:
                notax = 0
            row = [
                str(adr),
                "TOTAL%s" % darlehen_spezial,
                "",
                "",
                "",
                "",
                "",
                total,
                notax,
                tax,
                pay,
            ]
            for col_num in range(len(row)):
                c = ws.cell(row=row_num + 1, column=col_num + 1)
                c.value = row[col_num]
                if not opt_darlehen:
                    c.font = Font(bold=True)
            row_num += 1
            sum_interest += total
            sum_interest_notax += notax
            sum_interest_tax += tax
            sum_interest_pay += pay
            count += 1

        if total > 0 and not opt_darlehen:
            for date_list in interest["dates"]:
                for d in date_list:
                    row = [
                        "",
                        str(d["type"]),
                        "%s - %s"
                        % (d["start"].strftime("%d.%m.%Y"), d["end"].strftime("%d.%m.%Y")),
                        d["amount"],
                        d["days"],
                        d["interest_rate"],
                        d["interest"],
                    ]
                    for col_num in range(len(row)):
                        c = ws.cell(row=row_num + 1, column=col_num + 1)
                        c.value = row[col_num]
                        # c.font = Font(bold = True)
                    row_num += 1
            row_num += 1

    ## Sum
    row_num += 1
    row = [
        "Anzahl/Summe:",
        count,
        "",
        "",
        "",
        "",
        "",
        sum_interest,
        sum_interest_notax,
        sum_interest_tax,
        sum_interest_pay,
    ]
    for col_num in range(len(row)):
        c = ws.cell(row=row_num + 1, column=col_num + 1)
        c.value = row[col_num]
        c.font = Font(bold=True)
    row_num += 1

    wb.save(response)
    return response


@login_required
def share_mailing(request):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    ret = []
    objects = []
    for adr in Address.objects.filter(active=True).order_by("name"):
        if not is_member(adr, date_mode="end_date"):
            ## Nichtmitglied
            # ret.append({'info': str(adr), 'objects': ['Nichtmitglied']})
            continue

        if not adr.city:
            ret.append({"info": str(adr), "objects": ["KEINE ADRESSE!"]})
            continue

        ## Flags
        share_mini = False
        loan = False
        deposit = False

        obj = []
        try:
            inter = share_interest_calc(adr, datetime.datetime.now().year)
        except Exception as e:
            messages.error(request, "FEHLER bei der Zinsberechnung: %s" % str(e))
            return HttpResponseRedirect("/admin/")
        deposit_betrag = ""
        if inter["end_amount"][0] > 1000:
            ## Anteilscheine > 5
            obj.append("AS: %d" % inter["end_amount"][0])
        else:
            ## Anteilscheine < 6
            obj.append("AS: %d [mini]" % inter["end_amount"][0])
            share_mini = True
        if inter["end_amount"][1]:
            ## Zinslose Darlehen
            obj.append("Darlehen zinslos: %d" % inter["end_amount"][1])
            loan = True
        if inter["end_amount"][2]:
            ## Verzinste Darlehen
            obj.append("Darlehen verzinst: %d" % inter["end_amount"][2])
            loan = True
        if inter["end_amount"][3]:
            ## Depositenkasse
            obj.append("Depositenkasse: %d" % inter["end_amount"][3])
            deposit_betrag = nformat(inter["end_amount"][3])
            deposit = True
        if inter["end_amount"][4]:
            ## Darlehen spezial
            obj.append("Darlehen spezial: %d" % inter["end_amount"][4])
            loan = True

        loan_info = []
        # loan_values = []
        # loan_due = []
        # loan_duenew = []
        if loan:
            letter = "mitDarlehen"
            for d in (
                get_active_shares()
                .filter(name=adr)
                .filter(
                    Q(share_type=ShareType.objects.get(name="Darlehen zinslos"))
                    | Q(share_type=ShareType.objects.get(name="Darlehen verzinst"))
                )
                .filter(is_interest_credit=False)
            ):
                # loan_values.append(nformat(d.value))
                duedate = d.date + relativedelta(years=d.duration)
                duedate_new = d.date + relativedelta(years=(d.duration + 5))
                # loan_due.append(duedate.strftime("%d.%m.%Y"))
                # loan_duenew.append(duedate_new.strftime("%d.%m.%Y"))
                loan_info.append(
                    {
                        "betrag": nformat(d.value),
                        "due": duedate.strftime("%d.%m.%Y"),
                        "duenew": duedate_new.strftime("%d.%m.%Y"),
                    }
                )
                obj.append(
                    "Darlehen-INFO: CHF %s,  %s  -> %s"
                    % (
                        nformat(d.value),
                        duedate.strftime("%d.%m.%Y"),
                        duedate_new.strftime("%d.%m.%Y"),
                    )
                )
        elif deposit:
            letter = "mitDeposito"
        elif share_mini:
            letter = "ohneBeitrag"
        else:
            letter = "mitAnteilsscheinen"
        obj.append("-> %s" % letter)

        ret.append({"info": str(adr), "objects": obj})
        objects.append(
            {
                "obj": adr,
                "info": "%s" % (letter),
                "extra_context": {
                    "loan_info": loan_info,
                    "deposit_betrag": deposit_betrag,
                    "filename_tag": letter,
                },
            }
        )

    options = {
        "beschreibung": "Mailings",
        "link_url": "/geno/share/mailing",
    }
    return create_documents(request, "mailing", objects, options)


## TODO: Refactor to ClassBased view
@login_required
def share_duedate_reminder(request):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    cutoff_date = timezone.now() + relativedelta(months=16)
    today = datetime.date.today()
    next_year = today.year + 1

    # ret = []
    objects = []
    for adr in Address.objects.filter(active=True):
        ## Check if we have a recent reminder document already
        try:
            last_reminder = (
                Document.objects.filter(object_id=adr.pk)
                .filter(content_type=ContentType.objects.get(app_label="geno", model="address"))
                .filter(doctype__name="loanreminder")
                .latest("ts_created")
            )
            last_reminder_cutoff_date = last_reminder.ts_created + relativedelta(months=16)
        except Document.DoesNotExist:
            last_reminder_cutoff_date = None

        share_contexts = []
        info = []
        ## Get active loans that have no end date
        for share in (
            get_active_shares()
            .filter(name=adr)
            .filter(share_type__name__startswith="Darlehen")
            .filter(date_end=None)
            .filter(is_interest_credit=False)
        ):
            startdate = share.date
            if share.date_due:
                duedate = share.date_due
                if share.duration:
                    startdate = share.date_due - relativedelta(years=share.duration)
            elif share.duration:
                duedate = share.date + relativedelta(years=share.duration)
            else:
                duedate = None
                info.append("WARNUNG: %s hat KEIN FÄLLIGKEITSDATUM!" % (share))
            if duedate and duedate < cutoff_date.date():
                if not last_reminder_cutoff_date or duedate >= last_reminder_cutoff_date.date():
                    info.append(
                        "%s[%s]: NEEDS REMINDER" % (nformat(share.quantity * share.value), duedate)
                    )
                    share_context = {"zaehler": ""}
                    share_context["betrag"] = nformat(share.quantity * share.value)
                    if share.duration:
                        share_context["laufzeit"] = "%s Jahre - " % share.duration
                    else:
                        share_context["laufzeit"] = ""
                    share_context["laufzeit"] += "%s – %s" % (
                        startdate.strftime("%d.%m.%Y"),
                        duedate.strftime("%d.%m.%Y"),
                    )
                    share_context["zinssatz"] = nformat(share.interest())
                    share_context["plus5jahre"] = (duedate + relativedelta(years=5)).strftime(
                        "%d.%m.%Y"
                    )
                    share_context["plus10jahre"] = (duedate + relativedelta(years=10)).strftime(
                        "%d.%m.%Y"
                    )
                    share_context["datum_zins_neu"] = "01.01.%s" % next_year
                    share_contexts.append(share_context)
                else:
                    info.append(
                        "%s[%s]: Already reminded (%s)"
                        % (
                            nformat(share.quantity * share.value),
                            duedate,
                            last_reminder.ts_created,
                        )
                    )
            else:
                info.append("%s[%s]: Not due" % (nformat(share.quantity * share.value), duedate))

        if len(share_contexts) > 1:
            counter = 1
            for sc in share_contexts:
                sc["zaehler"] = "(Darlehen %s von %s)" % (counter, len(share_contexts))
                counter += 1

        if share_contexts:
            # ret.append({'info': '%s' % (adr), 'objects': objects})
            objects.append(
                {
                    "obj": adr,
                    "info": "%s Darlehen: %s" % (len(share_contexts), " / ".join(info)),
                    "extra_context": {"darlehen": share_contexts},
                }
            )

    options = {"link_url": "/geno/share/duedate_reminder"}
    options["beschreibung"] = "Brief Erinnerung Darlehen"
    return create_documents(request, "loanreminder", objects, options)


## TODO: Refactor to ClassBased view
@login_required
def share_statement(request, date="previous_year", address=None):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    year_current = datetime.datetime.now().year
    if not date or date == "previous_year":
        year = year_current - 1
        enddate = datetime.date(year, 12, 31)
    elif date == "current_year":
        year = year_current
        enddate = datetime.date(year, 12, 31)
    else:
        enddate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        year = int(enddate.year)

    ## List all shares for one address
    # ret = []
    objects = []
    options = {"link_url": "/geno/share/statement/%s" % (enddate.strftime("%Y-%m-%d"))}
    checksum_interest_pay = 0
    checksum_interest_tax = 0
    checksum_count = 0
    skip_count = 0
    # for adr in Address.objects.filter(active=True).order_by('name'):
    if address:
        addresses = Address.objects.filter(pk=address)
        options["link_url"] = "%s/%s" % (options["link_url"], address)
    else:
        addresses = Address.objects
        ## TEST:
        # addresses = Address.objects.filter(Q(name='Test')|Q(first_name='Test'))
    for adr in addresses.filter(active=True).order_by("name"):
        # print("#### %s %s" % (adr.organization,adr.name))
        # shares = []
        try:
            statement_data = get_share_statement_data(adr, year, enddate)
        except Exception as e:
            messages.error(request, "FEHLER beim Erstellen des Kontoauszugs: %s" % str(e))
            return HttpResponseRedirect("/admin/")

        if statement_data["sect_interest"]:
            checksum_interest_tax += statement_data["s_tax"]
            checksum_interest_pay += statement_data["s_pay"]
        statement_data["s_tax"] = nformat(statement_data["s_tax"])
        statement_data["s_pay"] = nformat(statement_data["s_pay"])

        info = (
            "%s/%s, Darlehen(zinsl.): %s, Darlehen: %s, Depositen: %s/%s, "
            "VSt: %s, ZinsAuszahlung: %s, Zeilen: %d, %s + %s"
            % (
                statement_data["n_shares"],
                statement_data["s_shares"],
                statement_data["s_loan_no"],
                statement_data["s_loan"],
                statement_data["dep_start"],
                statement_data["dep_end"],
                statement_data["s_tax"],
                statement_data["s_pay"],
                statement_data["line_count"],
                statement_data["loan_no_duedates"],
                statement_data["loan_duedates"],
            )
        )
        # if statement_data['sect_loan'] or statement_data['sect_deposit']: ## TEST
        # if statement_data['loan_int'] or statement_data['sect_deposit']: ## TEST
        if (
            statement_data["sect_shares"]
            or statement_data["sect_loan"]
            or statement_data["sect_deposit"]
        ):
            if not statement_data["thankyou"]:
                skip_count += 1
            else:
                checksum_count += 1
                objects.append(
                    {
                        "obj": adr,
                        "info": "%d: %s" % (checksum_count, info),
                        "extra_context": statement_data,
                    }
                )

    options["beschreibung"] = (
        "Kontoauszüge %s [Anzahl=%d, VSt=%s, ZinsAuszahlung=%s, Anzahl ignoriert=%d]"
        % (
            year,
            checksum_count,
            nformat(checksum_interest_tax),
            nformat(checksum_interest_pay),
            skip_count,
        )
    )
    return create_documents(request, "statement", objects, options)


@login_required
def share_check(request, year="previous", address=None):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    report = check_rental_shares_report()
    header = [
        "Mietobjekt/Name",
        "AS Soll",
        "AS Reduktion",
        "AS benötigt",
        "AS bezahlt",
        "AS ausstehend",
        "AS Leerstand",
        "Min. Beleg.",
        "Beleg.",
        "Diff.",
        "Kinder",
        "Details",
    ]
    return export_data_to_xls(report, header=header)


## TODO: Refactor to ClassBased view
@login_required
def create_contracts(request, letter=False):
    if not request.user.has_perm("geno.canview_share") or not request.user.has_perm(
        "geno.canview_billing"
    ):
        return unauthorized(request)

    stock = {}
    stock["EG"] = "Erdgeschoss"
    stock["1.OG"] = "1. Obergeschoss"
    stock["2.OG"] = "2. Obergeschoss"
    stock["3.OG"] = "3. Obergeschoss"
    stock["4.OG"] = "4. Obergeschoss"
    stock["5.OG"] = "5. Obergeschoss"
    stock["6.OG"] = "6. Obergeschoss"
    stock["7.OG"] = "7. Obergeschoss"
    stock["8.OG"] = "8. Obergeschoss"
    stock["9.OG"] = "9. Obergeschoss"
    stock["1.UG"] = "1. Untergeschoss"
    stock["2.UG"] = "2. Untergeschoss"
    stock["3.UG"] = "3. Untergeschoss"
    stock["4.UG"] = "4. Untergeschoss"
    stock["5.UG"] = "5. Untergeschoss"
    stock["6.UG"] = "6. Untergeschoss"
    stock["7.UG"] = "7. Untergeschoss"
    stock["8.UG"] = "8. Untergeschoss"
    stock["9.UG"] = "9. Untergeschoss"

    objects = []
    for contract in Contract.objects.all():
        data = {"mietobjekt": ""}
        for rental_unit in contract.rental_units.filter(rental_type="Wohnung"):
            if data["mietobjekt"] != "":
                raise Exception("Currently only one rental unit is supported!")
            floor_str = stock.get(rental_unit.floor, rental_unit.floor)
            if floor_str:
                data["mietobjekt"] = "%s-Zimmer-Wohnung Nr. %s im %s" % (
                    rental_unit.rooms,
                    rental_unit.name,
                    floor_str,
                )
            else:
                data["mietobjekt"] = "%s-Zimmer-Wohnung Nr. %s" % (
                    rental_unit.rooms,
                    rental_unit.name,
                )
            data["filename_tag"] = "Wohnung_%s" % rental_unit.name
            data["miete_netto"] = nformat(rental_unit.rent_netto, 0)
            data["miete_brutto"] = nformat(
                (rental_unit.rent_netto if rental_unit.rent_netto else 0.0)
                + (rental_unit.nk if rental_unit.nk else 0.0)
                + (rental_unit.nk_electricity if rental_unit.nk_electricity else 0.0),
                0,
            )
            data["nk_akonto"] = nformat(rental_unit.nk, 0)
            data["nk_strom"] = nformat(rental_unit.nk_electricity, 0)
            data["mindestbelegung"] = nformat(rental_unit.min_occupancy, 0)
            data["pflichtanteil"] = nformat(rental_unit.share, 0)
            data["rate1"] = nformat(rental_unit.share / 2, 0)
            data["rate2"] = nformat(rental_unit.share / 2, 0)
        if data["mietobjekt"] == "":
            continue
        for rental_unit in contract.rental_units.filter(rental_type="Kellerabteil"):
            data["mietobjekt"] = (
                "%s, Kellerabteil Nr. %s (ungeheizt, kein kontrolliertes Raumklima)"
                % (data["mietobjekt"], rental_unit.name)
            )
        info = "%s" % (data["mietobjekt"])
        mieter = []
        mieter_txt = []
        for m in contract.contractors.all():
            mieter.append(
                {
                    "name": "%s %s" % (m.first_name, m.name),
                    "address": "%s, %s" % (m.street, m.city),
                }
            )
            mieter_txt.append(
                "%s %s\tBisherige Adresse: %s, %s" % (m.first_name, m.name, m.street, m.city)
            )
        data["mieter_txt"] = "\n".join(mieter_txt)
        data["mieter"] = mieter
        if len(mieter) == 1:
            data["MieterInnen"] = "Mieter*in"
        else:
            data["MieterInnen"] = "Mieter*innen"

        objects.append({"obj": contract, "info": "%s" % (info), "extra_context": data})

    if letter:
        options = {
            "beschreibung": "Mietverträge Begleitbrief",
            "link_url": "/geno/contract/create_letter",
        }
        return create_documents(request, "contract_letter", objects, options)
    else:
        options = {
            "beschreibung": "Mietverträge",
            "link_url": "/geno/contract/create",
        }
        return create_documents(request, "contract", objects, options)


@login_required
def create_documents(request, default_doctype, objects=None, options=None):
    if request.GET.get("makezip", "") == "yes":
        makezip = True
    else:
        makezip = False

    ret = []
    zipcount = 0
    zipfile_content = []

    try:
        default_doctype_obj = DocumentType.objects.get(name=default_doctype)
    except DocumentType.DoesNotExist:
        return render(
            request,
            "geno/messages.html",
            {
                "response": [
                    {
                        "info": 'FEHLER: Dokumenttyp "%s" existiert nicht. Bitte zuerst erstellen.'
                        % default_doctype
                    }
                ],
                "title": "Dokumente erzeugen",
            },
        )

    if not options:
        options = {"beschreibung": default_doctype_obj.description}

    if not objects:
        if default_doctype == "contract_check":
            objects = []
            for c in get_active_contracts():
                for ru in c.rental_units.all():
                    if ru.rental_type not in ("Gewerbe", "Lager", "Hobby", "Parkplatz"):
                        objects.append({"obj": c})
                        break
        else:
            return render(
                request,
                "geno/messages.html",
                {
                    "response": [
                        {"info": 'Keine Objekte gefunden (Dokumenttyp "%s").' % default_doctype}
                    ],
                    "title": "Dokumente erzeugen - %s" % options["beschreibung"],
                },
            )

    filenames = []
    for o in objects:
        zipcount += 1
        objects = []
        if "info" in o:
            objects.append(o["info"])
        ret.append({"info": str(o["obj"]), "objects": objects})
        if makezip:
            if "doctype" in o:
                doctype = o["doctype"]
                doctype_obj = DocumentType.objects.get(name=doctype)
            else:
                doctype = default_doctype
                doctype_obj = default_doctype_obj
            ## Create document
            if "extra_context" in o:
                data = get_context_data(doctype, o["obj"].pk, o["extra_context"])
            else:
                data = get_context_data(doctype, o["obj"].pk, {})
            filename = fill_template_pod(
                doctype_obj.template.file.path,
                context_format(data["context"]),
                output_format="odt",
            )
            if not filename:
                raise RuntimeError("Could not fill template")
            output_filename = data["visible_filename"]
            counter = 1
            while output_filename in filenames:
                counter += 1
                output_filename = "%s_%s%s" % (
                    data["visible_filename"][0:-4],
                    counter,
                    data["visible_filename"][-4:],
                )
            zipfile_content.append({"file": filename, "filename": output_filename})
            filenames.append(output_filename)
            if "content_object" in data:
                ## Attach document data to object
                d = Document(
                    name=output_filename,
                    doctype=doctype_obj,
                    data=json.dumps(data["context"]),
                    content_object=data["content_object"],
                )
                d.save()

    if makezip:
        ## Build ZIP-file from list of files
        file_like_object = io.BytesIO()
        zipfile_ob = zipfile.ZipFile(file_like_object, "w")
        for f in zipfile_content:
            # print "%s -> %s_%s" % (f['file'], f['member'].name.name,f['member'].name.first_name)
            zipfile_ob.write(f["file"], f["filename"])
        zipfile_ob.close()
        resp = HttpResponse(
            file_like_object.getvalue(), content_type="application/x-zip-compressed"
        )
        resp["Content-Disposition"] = "attachment; filename=%s" % "output.zip"
        return resp

    if zipcount > 0:
        link_text = "%s erstellen und herunterladen" % options["beschreibung"]
        link_url = options.get("link_url", request.path)
        ret.append(
            {
                "info": "Dokumente:",
                "objects": [
                    '<a href="%s?makezip=yes">%s (%d LibreOffice Dokumente in ZIP)</a>'
                    % (link_url, link_text, zipcount)
                ],
            }
        )
    else:
        ret.append({"info": "Keine zu erstellenden Dokumente gefunden."})

    return render(
        request,
        "geno/messages.html",
        {"response": ret, "title": "Dokumente erzeugen - %s" % options["beschreibung"]},
    )


## TODO: Refactor to ClassBased view
@login_required
def check_mailinglists(request):
    if not request.user.has_perm("geno.canview_member_mailinglists"):
        return unauthorized(request)

    if not hasattr(settings, "MAILMAN_API"):
        return render(
            request,
            "geno/messages.html",
            {
                "response": [{"info:FEHLER: Mailman-API ist nicht konfiguriert."}],
                "title": "Check Mailinglisten",
            },
        )

    mailman_client = mailmanclient.Client(
        settings.MAILMAN_API["url"], settings.MAILMAN_API["user"], settings.MAILMAN_API["password"]
    )
    ml_warnings = []
    ml_members = {}
    for ml in ("genossenschaft", "bewohnende", "gewerbemietende", "wohnpost"):
        mlist = mailman_client.get_list(f"{ml}@{settings.MAILMAN_API['lists_domain']}")
        ml_members[ml] = []  # member.email for member in mlist.members ]
        for member in mlist.members:
            ml_members[ml].append(member.email)
            if member.bounce_score:
                ml_warnings.append(
                    f"[{ml}] {member.email} has bounce_score = {member.bounce_score}"
                )
            if member.delivery_mode != "regular":
                ml_warnings.append(
                    f"[{ml}] {member.email} has delivery_mode = {member.delivery_mode}"
                )
            if member.role != "member":
                ml_warnings.append(f"[{ml}] {member.email} has role = {member.role}")
            if member.subscription_mode != "as_address":
                ml_warnings.append(
                    f"[{ml}] {member.email} has subscription_mode = {member.subscription_mode}"
                )
            # address: http://localhost:9001/3.0/addresses/aperson@example.com
            # bounce_score: 0
            # delivery_mode: regular
            # display_name: Anna Person
            # email: aperson@example.com
            # http_etag: ...
            # last_warning_sent: 0001-01-01T00:00:00
            # list_id: ant.example.com
            # member_id: 4
            # role: member
            # self_link: http://localhost:9001/3.0/members/4
            # subscription_mode: as_address
            # total_warnings_sent: 0
            # user: http://localhost:9001/3.0/users/3

    ignore_emails = settings.GENO_CHECK_MAILINGLISTS["ignore_emails"]

    ret = []

    ## TODO: Also check gewerbe?
    ## Get bewohnende and check Bewohnenden-ML
    bewohnende = []
    bewohnende_email = []
    bewohnende_missing = []
    for c in get_active_contracts():
        include = False
        for ru in c.rental_units.all():
            if ru.rental_type not in ("Gewerbe", "Lager", "Hobby", "Parkplatz"):
                include = True
                break
        if include:
            for adr in c.contractors.all():
                if adr not in bewohnende:
                    bewohnende.append(adr)
            ## Add children that have an email address
            for child in c.children.exclude(name__email__exact=""):
                if child.name not in bewohnende:
                    bewohnende.append(child.name)
    for adr in bewohnende:
        if not adr.email:
            bewohnende_missing.insert(0, f"IGNORIERE {adr} (KEINE Email-Adresse)")
        elif adr.email in bewohnende_email:
            bewohnende_missing.insert(0, f"IGNORIERE {adr} (DOPPELTE Email-Adresse {adr.email})")
        else:
            bewohnende_email.append(adr.email)
            if adr.email in ml_members["bewohnende"]:
                ml_members["bewohnende"].remove(adr.email)
            else:
                ## Bewohner*in nicht in bewohnenden-ML
                bewohnende_missing.append(adr.email)

    ## Get members and check Genossenschaft-ML
    members_email = []
    genossenschaft_missing = []
    wohnpost_missing = []
    for member in Member.objects.all():
        if not is_member(member.name):
            continue
        if not member.name.email:
            genossenschaft_missing.insert(0, f"IGNORIERE {member.name} (KEINE Email-Adresse)")
        elif member.name.email in members_email:
            genossenschaft_missing.insert(
                0, f"IGNORIERE {member.name} (DOPPELTE Email-Adresse {member.name.email})"
            )
        else:
            members_email.append(member.name.email)
            if member.name.email in ml_members["genossenschaft"]:
                ml_members["genossenschaft"].remove(member.name.email)
            else:
                ## Member not in geno-ML
                genossenschaft_missing.append(member.name.email)
            if (
                member.name.email not in ml_members["wohnpost"]
                and member.name.email not in ignore_emails
            ):
                wohnpost_missing.append(member.name.email)

    ## Bewohnende / Gewerbemietende, welche weder auf Geno-Liste noch auf Wohnpost sind
    wohnpost_and_geno_missing = []
    for email in ml_members["bewohnende"]:
        if (
            email not in ml_members["wohnpost"]
            and email not in wohnpost_missing
            and email not in ignore_emails
        ):
            wohnpost_and_geno_missing.append(email)
    for email in ml_members["gewerbemietende"]:
        if (
            email not in ml_members["wohnpost"]
            and email not in wohnpost_missing
            and email not in wohnpost_and_geno_missing
            and email not in ignore_emails
        ):
            wohnpost_and_geno_missing.append(email)

    ## Get active/unsubscribed/bounced subscribsers from CreateSend
    cs_newsletter = createsend.List(list_id=settings.CREATESEND_LIST_ID_NEWSLETTER)
    cs_newsletter.auth({"api_key": settings.CREATESEND_API_KEY})

    cs_newsletter_unsubscribed = []
    page = 1
    num_pages = 1
    while page <= num_pages:
        res = cs_newsletter.unsubscribed(page=page, page_size=1000)
        num_pages = res.NumberOfPages
        page += 1
        for sub in res.Results:
            cs_newsletter_unsubscribed.append(sub.EmailAddress.lower())

    cs_newsletter_bounced = []
    page = 1
    num_pages = 1
    while page <= num_pages:
        res = cs_newsletter.bounced(page=page, page_size=1000)
        num_pages = res.NumberOfPages
        page += 1
        for sub in res.Results:
            cs_newsletter_bounced.append(sub.EmailAddress.lower())

    cs_newsletter_deleted = []
    page = 1
    num_pages = 1
    while page <= num_pages:
        res = cs_newsletter.deleted(page=page, page_size=1000)
        num_pages = res.NumberOfPages
        page += 1
        for sub in res.Results:
            cs_newsletter_deleted.append(sub.EmailAddress.lower())

    cs_newsletter_active = []
    page = 1
    num_pages = 1
    while page <= num_pages:
        res = cs_newsletter.active(page=page, page_size=1000)
        num_pages = res.NumberOfPages
        page += 1
        for sub in res.Results:
            cs_newsletter_active.append(sub.EmailAddress.lower())

    newsletter_missing_cs = []
    newsletter_extra_cs_unsubscribed = []
    newsletter_extra_cs_bounced = []
    newsletter_extra_cs_deleted = []
    for email in members_email:
        if email in cs_newsletter_unsubscribed:
            newsletter_extra_cs_unsubscribed.append(email)
        elif email in cs_newsletter_bounced:
            newsletter_extra_cs_bounced.append(email)
        elif email in cs_newsletter_deleted:
            newsletter_extra_cs_deleted.append(email)
        elif email not in cs_newsletter_active:
            newsletter_missing_cs.append(email)

    ret.append({"info": "Mitglied nicht in genossenschaft-ML:", "objects": genossenschaft_missing})
    ret.append(
        {
            "info": "In genossenschaft-ML aber nicht Mitglied:",
            "objects": ml_members["genossenschaft"],
        }
    )
    ret.append({"info": "Bewohnende aber nicht in bewohnende-ML:", "objects": bewohnende_missing})
    ret.append(
        {"info": "In bewohnende-ML aber nicht Bewohnende:", "objects": ml_members["bewohnende"]}
    )
    ret.append(
        {"info": "Mitglied aber NICHT in Newsletter(CS):", "objects": newsletter_missing_cs}
    )
    ret.append(
        {
            "info": "Mitglied aber UNSUBSCRIBED in Newsletter(CS):",
            "objects": newsletter_extra_cs_unsubscribed,
        }
    )
    ret.append(
        {
            "info": "Mitglied aber BOUNCED in Newsletter(CS):",
            "objects": newsletter_extra_cs_bounced,
        }
    )
    ret.append(
        {
            "info": "Mitglied aber DELETED in Newsletter(CS):",
            "objects": newsletter_extra_cs_deleted,
        }
    )
    ret.append(
        {
            "info": "In genossenschaft-ML aber nicht in Wohnpost (%s):" % len(wohnpost_missing),
            "objects": wohnpost_missing,
        }
    )
    ret.append(
        {
            "info": "Bewohnende/Gewerbemietende weder in genossenschaft-ML noch in Wohnpost (%s):"
            % len(wohnpost_and_geno_missing),
            "objects": wohnpost_and_geno_missing,
        }
    )
    ret.append({"info": "Mailman warnings:", "objects": ml_warnings})
    return render(request, "geno/messages.html", {"response": ret, "title": "Check Mailinglisten"})


## TODO: Refactor to ClassBased view
@login_required
def run_maintenance_tasks(request):
    if not request.user.has_perm("geno.admin_import"):
        return unauthorized(request)

    ret = []
    # ret.append({'info': 'Creating new users:', 'objects': create_users()})

    return render(
        request, "geno/messages.html", {"response": ret, "title": "Run maintenance tasks"}
    )


def send_member_mail_filter_rental(form, member_list):
    adr_list = []
    for contract in get_active_contracts():
        rental = []
        for ru in contract.rental_units.all():
            if (
                form.cleaned_data["select_rentaltype"] == "all"
                or form.cleaned_data["select_rentaltype"] == ru.rental_type
                or (
                    form.cleaned_data["select_rentaltype"] == "all_nobusiness"
                    and ru.rental_type not in ["Gewerbe", "Lager", "Hobby", "Parkplatz"]
                )
            ):
                rental.append(ru.name)
        if rental:
            for adr in contract.contractors.all():
                if adr.pk not in adr_list:
                    ## Filter by generic attribute: TODO: move this filter to be additive...
                    include = True
                    if form.cleaned_data["filter_genattribute"] != "none":
                        genatt = (
                            GenericAttribute.objects.filter(
                                name=form.cleaned_data["filter_genattribute"]
                            )
                            .filter(addresses=adr)
                            .first()
                        )
                        if genatt:
                            genatt_val = genatt.value
                        else:
                            genatt_val = "--OHNE--"
                        if form.cleaned_data["filter_genattribute_value"] != genatt_val:
                            include = False
                    if include:
                        adr_list.append(adr.pk)
                        member_list.append(
                            {
                                "id": adr.pk,
                                "address_id": adr.pk,
                                "contract_id": contract.id,
                                "member": str(adr),
                                "extra_info": "/".join(rental),
                                "member_type": "address",
                            }
                        )
                    # print('%s: %s' % (adr,'/'.join(rental)))
    return []  # No error


def filter_select_document_nostatement(form, adr_list):
    try:
        doctype_statement = DocumentType.objects.get(name="statement")
    except DocumentType.DoesNotExist:
        return adr_list
    date_6months_ago = timezone.now() - relativedelta(months=6)
    result = []
    for adr in adr_list:
        exclude = False
        if (
            "select_document" in form.cleaned_data
            and form.cleaned_data["select_document"] == "nostatement"
        ):
            docs = (
                Document.objects.filter(doctype=doctype_statement)
                .filter(addresses=adr)
                .filter(ts_created__gt=date_6months_ago)
            )
            if len(docs):
                exclude = True
        if not exclude:
            result.append(adr)
    return result


def send_member_mail_filter_addresses(form, member_list):
    for adr in filter_select_document_nostatement(form, Address.objects.filter(active=True)):
        member_list.append(
            {
                "id": adr.pk,
                "address_id": adr.pk,
                "member": str(adr),
                "extra_info": None,
                "member_type": "address",
            }
        )
    return []  # No error


def send_member_mail_filter_shares(form, member_list):
    addresses = []
    stype_filter = None
    stype_exclude = None

    if form.cleaned_data["select_sharetype"] == "shares":
        stype_filter = list(ShareType.objects.filter(name__startswith="Anteilschein"))
        if not stype_filter:
            return ["Beteiligungstypen nicht gefunden."]
    elif form.cleaned_data["select_sharetype"] == "loan_deposit":
        stype_filter = list(ShareType.objects.filter(name__startswith="Darlehen"))
        stype_filter.extend(list(ShareType.objects.filter(name="Depositenkasse")))
        if not stype_filter:
            return ["Beteiligungstypen nicht gefunden."]
    elif form.cleaned_data["select_sharetype"] == "with_interest":
        stype_filter = list(ShareType.objects.filter(name__startswith="Darlehen verzinst"))
        stype_filter.extend(list(ShareType.objects.filter(name="Depositenkasse")))
        if not stype_filter:
            return ["Beteiligungstypen nicht gefunden."]
    else:
        stype_exclude = list(ShareType.objects.filter(name="Darlehen spezial"))
        stype_exclude.extend(list(ShareType.objects.filter(name="Hypothek")))

    # print(stype_filter)

    shares = get_active_shares()
    if stype_filter:
        shares = shares.filter(share_type__in=stype_filter)
    if stype_exclude:
        shares = shares.exclude(share_type__in=stype_exclude)
    for share in shares:
        if share.name not in addresses:
            addresses.append(share.name)
    for adr in filter_select_document_nostatement(form, addresses):
        member_list.append(
            {
                "id": adr.pk,
                "address_id": adr.pk,
                "member": str(adr),
                "extra_info": None,
                "member_type": "address",
            }
        )
    return []


def send_member_mail_filter_members(form, member_list):
    errors = []
    members = Member.objects.all()
    if "ignore_join_date" in form.cleaned_data and form.cleaned_data["ignore_join_date"]:
        members = members.exclude(date_join__gt=form.cleaned_data["ignore_join_date"])
    if form.cleaned_data["select_flag_01"] == "true":
        members = members.filter(flag_01=True)
    elif form.cleaned_data["select_flag_01"] == "false":
        members = members.filter(flag_01=False)
    if form.cleaned_data["select_flag_02"] == "true":
        members = members.filter(flag_02=True)
    elif form.cleaned_data["select_flag_02"] == "false":
        members = members.filter(flag_02=False)
    if form.cleaned_data["select_flag_03"] == "true":
        members = members.filter(flag_03=True)
    elif form.cleaned_data["select_flag_03"] == "false":
        members = members.filter(flag_03=False)
    if form.cleaned_data["select_flag_04"] == "true":
        members = members.filter(flag_04=True)
    elif form.cleaned_data["select_flag_04"] == "false":
        members = members.filter(flag_04=False)
    if form.cleaned_data["select_flag_05"] == "true":
        members = members.filter(flag_05=True)
    elif form.cleaned_data["select_flag_05"] == "false":
        members = members.filter(flag_05=False)
    try:
        stype01 = ShareType.objects.get(name="Anteilschein Einzelmitglied")
    except ShareType.DoesNotExist:
        stype01 = None
    try:
        stype02 = ShareType.objects.get(name="Anteilschein Gründungsmitglied")
    except ShareType.DoesNotExist:
        stype02 = None
    for member in members:
        ## Filter active membership
        if not is_member(member.name):
            continue
        ## Filter out members without shares
        if "share_paid_01" in form.cleaned_data and form.cleaned_data["share_paid_01"]:
            share = get_active_shares().filter(share_type=stype01).filter(name=member.name).first()
            if not share:
                continue
        ## Filter out members with shares
        if "share_unpaid" in form.cleaned_data and form.cleaned_data["share_unpaid"]:
            share = (
                get_active_shares()
                .filter(Q(share_type=stype01) | Q(share_type=stype02))
                .filter(name=member.name)
                .first()
            )
            if share:
                continue
        ## Filter attributes (if set in form)
        att_info = []
        if form.cleaned_data["select_attributeA"]:
            attA = MemberAttribute.objects.filter(member=member).filter(
                attribute_type=form.cleaned_data["select_attributeA"]
            )
            if len(attA) > 1:
                errors.append(
                    "%s - ERROR: MORE THAN ONE ATTRIBUTE FOUND! %s -> %s, %s"
                    % (
                        member,
                        form.cleaned_data["select_attributeA"],
                        attA[0].value,
                        attA[1].value,
                    )
                )
                continue
            if (
                len(attA) == 1 and attA[0].value != form.cleaned_data["select_attributeA_value"]
            ) or (len(attA) == 0 and form.cleaned_data["select_attributeA_value"] != "--OHNE--"):
                ## has attribute but wrong value, or, has no attribute but one is required
                continue
            if len(attA) == 0:
                att_info.append("A: (kein Attribut)")
            else:
                att_info.append("A: %s [%s]" % (attA[0].value, attA[0].date))
        if form.cleaned_data["select_attributeB"]:
            attB = MemberAttribute.objects.filter(member=member).filter(
                attribute_type=form.cleaned_data["select_attributeB"]
            )
            if len(attB) > 1:
                errors.append(
                    "%s - ERROR: MORE THAN ONE ATTRIBUTE FOUND! %s -> %s, %s"
                    % (
                        member,
                        form.cleaned_data["select_attributeB"],
                        attB[0].value,
                        attB[1].value,
                    )
                )
                continue
            if (
                len(attB) == 1 and attB[0].value != form.cleaned_data["select_attributeB_value"]
            ) or (len(attB) == 0 and form.cleaned_data["select_attributeB_value"] != "--OHNE--"):
                ## has attribute but wrong value, or, has no attribute but one is required
                continue
            if len(attB) == 0:
                att_info.append("B: (kein Attribut)")
            else:
                att_info.append("B: %s [%s]" % (attB[0].value, attB[0].date))
        ## Add member
        member_list.append(
            {
                "id": member.pk,
                "address_id": member.name.pk,
                "member": str(member),
                "extra_info": "/".join(att_info),
                "member_type": "member",
            }
        )
    return errors


def send_member_mail_filter_by_invoice(form, member_list):
    errors = []
    if "filter_invoice" not in form.cleaned_data or form.cleaned_data["filter_invoice"] == "none":
        return errors
    count = 0
    for member in member_list:
        query = Invoice.objects.filter(person__id=member["address_id"], invoice_type="Invoice")
        if (
            "filter_invoice_category" in form.cleaned_data
            and form.cleaned_data["filter_invoice_category"]
        ):
            query = query.filter(invoice_category=form.cleaned_data["filter_invoice_category"])
        if "filter_invoice_consolidated" in form.cleaned_data:
            if form.cleaned_data["filter_invoice_consolidated"] == "true":
                query = query.filter(consolidated=True)
            elif form.cleaned_data["filter_invoice_consolidated"] == "false":
                query = query.filter(consolidated=False)
        if (
            "filter_invoice_daterange_min" in form.cleaned_data
            and form.cleaned_data["filter_invoice_daterange_min"]
        ):
            query = query.filter(date__gt=form.cleaned_data["filter_invoice_daterange_min"])
        if (
            "filter_invoice_daterange_max" in form.cleaned_data
            and form.cleaned_data["filter_invoice_daterange_max"]
        ):
            query = query.filter(date__lt=form.cleaned_data["filter_invoice_daterange_max"])
        if query.count():
            if form.cleaned_data["filter_invoice"] == "exclude":
                member["id"] = None  # exclude
        else:
            if form.cleaned_data["filter_invoice"] == "include":
                member["id"] = None  # exclude
        if member["id"]:
            count += 1
    if count == 0:
        errors.append("Keine Empfänger:innen gefunden, welche diesen Filterkriterien entsprechen.")
    return errors


## TODO: Refactor to ClassBased view
@login_required
def send_member_mail(request):
    if not request.user.has_perm("geno.send_mail"):
        return unauthorized(request)

    initial = {}
    ret = {"errors": [], "show_results": False}
    errors = []
    form = MemberMailForm(request.POST or None, initial=initial)
    if request.method == "POST":
        if form.is_valid():
            ## Filter members
            request.session["members"] = []

            if form.cleaned_data["base_dataset"] == "renters":
                errors = send_member_mail_filter_rental(form, request.session["members"])
                ## Filter for rental_type
            elif form.cleaned_data["base_dataset"] == "addresses":
                ## Filter for documents
                errors = send_member_mail_filter_addresses(form, request.session["members"])
            elif form.cleaned_data["base_dataset"] == "shares":
                errors = send_member_mail_filter_shares(form, request.session["members"])
            elif form.cleaned_data["base_dataset"] == "active_members":
                ## Filter members
                errors = send_member_mail_filter_members(form, request.session["members"])
            else:
                errors.append("Ungültiger Basis-Datensatz")
            ## Filter by invoice existance
            errors.extend(send_member_mail_filter_by_invoice(form, request.session["members"]))
            if not errors:
                return HttpResponseRedirect("/geno/member/send_mail/select/")
        ret["show_results"] = True
        for error in errors:
            ret["errors"].append({"info": error})
    return render(
        request,
        "geno/member_send_mail.html",
        {
            "response": ret,
            "title": "Dokumente/Mailings erstellen/versenden",
            "info": "Schritt 1: Empfänger:innen filtern",
            "form": form,
            "form_action": "/geno/member/send_mail/",
        },
    )


@login_required
def send_member_mail_select(request):
    if not request.user.has_perm("geno.send_mail"):
        return unauthorized(request)

    if "members" not in request.session:
        return HttpResponseRedirect("/geno/member/send_mail/")

    initial = {}
    form = MemberMailSelectForm(
        request.POST or None, initial=initial, members=request.session["members"]
    )
    if request.method == "POST":
        # print(form.data)
        if form.is_valid():
            request.session["select_members"] = form.cleaned_data["select_members"]
            return HttpResponseRedirect("/geno/member/send_mail/action/")
    return render(
        request,
        "geno/member_send_mail.html",
        {
            "response": {},
            "title": "Dokumente/Mailings erstellen/versenden",
            "info": "Schritt 2: Empfänger:innen auswählen",
            "form": form,
            "form_action": "/geno/member/send_mail/select/",
        },
    )


## TODO: Refactor to ClassBased view
@login_required
def send_member_mail_action(request):
    if not request.user.has_perm("geno.send_mail"):
        return unauthorized(request)

    initial = {"email_copy": settings.GENO_DEFAULT_EMAIL}
    ret = {}
    form = MemberMailActionForm(request.POST or None, initial=initial)
    if request.method == "POST":
        # print(form.data)
        if form.is_valid():
            form.cleaned_data["members"] = []
            for m in request.session["members"]:
                if str(m["id"]) in request.session["select_members"]:
                    form.cleaned_data["members"].append(m)
            ret = send_member_mail_process(form.cleaned_data)
            if isinstance(ret, HttpResponse):
                return ret
            ret["show_results"] = True

    return render(
        request,
        "geno/member_send_mail.html",
        {
            "response": ret,
            "title": "Dokumente/Mailings erstellen/versenden",
            "info": "Schritt 3: Aktionen ausführen",
            "form": form,
            "form_action": "/geno/member/send_mail/action/",
        },
    )


@login_required
def send_contract_mail(request):
    ret = []
    email_copy = settings.TEST_MAIL_RECIPIENT
    # email_copy = None
    commit = True
    count = 0
    counted = {}

    return render(
        request,
        "geno/messages.html",
        {
            "response": [{"info": "Funktion zur Zeit deaktiviert."}],
            "title": "Versand and Mieter*innen",
        },
    )

    with open("/home/wsadmin/einzug.json") as f:
        data = json.load(f)

    for c in get_active_contracts():
        for ru in c.rental_units.all():
            emails = []
            adrs = []
            obj = []
            termine = []
            has_data = False
            if ru.name in data and ru.name not in ("408", "104", "112", "405"):
                counted[ru.name] = True
                count += 1
                has_data = True
                for d in data[ru.name]["moving"]:
                    obj.append("Zügeltermin: %s, %s" % (d["date"], d["access"]))
                    termine.append("%s, %s" % (d["date"], d["access"]))
                if not termine:
                    termine.append("Noch kein Termin festgelegt.")
                for adr in c.contractors.all():
                    if adr.email:
                        if adr.email not in emails:
                            emails.append(adr.email)
                            obj.append("Email an: %s" % adr.email)
                            if commit or ru.name in (
                                "011",
                                "002",
                                "408",
                                "002",
                                "010",
                                "404",
                                "504",
                                "104",
                                "205",
                                "395",
                                "008",
                                "310",
                                "006",
                            ):
                                adrs.append(adr)
                    else:
                        obj.append("WARNUNG: Keine Email für %s" % adr)

            for adr in adrs:
                context = {"termin_uebergabe": data[ru.name]["handover"], "termine": termine}
                context.update(adr.get_context())
                mail_recipient = adr.get_mail_recipient()
                mail_subject = "Übergabetermin Wohnung %s" % ru.name
                mail_template = loader.get_template("geno/contract_email.html")
                mail_text = mail_template.render(context)
                if email_copy and mail_recipient != email_copy:
                    bcc = [
                        email_copy,
                    ]
                else:
                    bcc = None

                mails_sent = 0
                try:
                    mail = EmailMultiAlternatives(
                        mail_subject,
                        mail_text,
                        f'"{settings.GENO_NAME}" <{settings.SERVER_EMAIL}>',
                        [mail_recipient],
                        bcc,
                    )
                    mail.attach_alternative(mail_text, "text/html")
                    mails_sent = mail.send()
                except SMTPException as e:
                    obj.append(
                        "Konnte mail an %s nicht schicken!!! SMTP-Fehler: %s"
                        % (escape(mail_recipient), e)
                    )
                except Exception as e:
                    obj.append(
                        "Konnte mail an %s nicht schicken!!! Allgemeiner Fehler: %s"
                        % (escape(mail_recipient), e)
                    )
                if mails_sent == 1:
                    obj.append("Email an %s geschickt." % (escape(mail_recipient)))

            if has_data:
                ret.append(
                    {
                        "info": "Wohnung %s: %s" % (ru.name, data[ru.name]["handover"]),
                        "objects": obj,
                    }
                )

    for d in data:
        if d not in counted:
            ret.append({"info": "WARNING: Not counted/found: %s" % d})

    ret.append({"info": "Count wohnungen = %s" % count, "objects": []})
    return render(
        request, "geno/messages.html", {"response": ret, "title": "Versand and Mieter*innen"}
    )


@login_required
def transaction_upload(request):
    if not request.user.has_perm("geno.transaction"):
        return unauthorized(request)

    initial = {}
    ret = []
    import_message = ""
    form = TransactionUploadFileForm(request.POST or None, request.FILES, initial=initial)
    if request.method == "POST":
        # print form.data
        if form.is_valid():
            # if not request.FILES:
            #    return HttpResponseRedirect('/geno/transaction_upload/process/')
            if "file" in request.FILES:
                uploaded_file = request.FILES["file"]
                transaction_data = process_transaction_file(request.FILES["file"])

                if transaction_data["error"]:
                    messages.error(
                        request, "Konnte Datei nicht verarbeiten: %s" % transaction_data["error"]
                    )
                    logger.error(
                        f"Transaction upload: Error while processing {uploaded_file}: "
                        f"{transaction_data['error']}"
                    )
                elif transaction_data["type"].startswith("camt.053") or transaction_data[
                    "type"
                ].startswith("camt.054"):
                    import_message = "Import von Buchungen aus %s:" % uploaded_file
                    ret = process_sepa_transactions(transaction_data["data"])
                    if len(ret["success"]):
                        logger.info(
                            f"Transaction upload: Imported {len(ret['success'])} records "
                            f"from {uploaded_file}."
                        )
                else:
                    messages.error(
                        request,
                        "Konnte Datei nicht verarbeiten: Unbekannter typ %s"
                        % transaction_data["type"],
                    )
                    logger.error(
                        f"Transaction upload: Error while processing {uploaded_file}: "
                        f"Invalid type {transaction_data['type']}"
                    )

            else:
                messages.error(request, "Konnte Datei nicht hochladen.")

    return render(
        request,
        "geno/transaction_upload.html",
        {
            "import_message": import_message,
            "import_items": ret,
            "item_name": "Buchungen",
            "title": "Bankauszug verarbeiten",
            "form": form,
            "form_action": "/geno/transaction_upload/",
        },
    )


@login_required
def transaction_upload_process(request):
    if not request.user.has_perm("geno.transaction"):
        return unauthorized(request)

    initial = {}
    ret = []
    info_text = ""
    get_next = False
    transaction = None

    if request.method == "POST":
        transaction = request.session["last_transaction"]
        form = TransactionUploadProcessForm(request.POST, initial=initial, transaction=transaction)
        if form.is_valid():
            if form.cleaned_data["transaction"] == "ignore":
                get_next = True
            else:
                note = form.cleaned_data["note"]
                if form.cleaned_data["extra_info"]:
                    if note:
                        note = "%s / %s" % (note, form.cleaned_data["extra_info"])
                    else:
                        note = form.cleaned_data["extra_info"]
                error = process_transaction(
                    form.cleaned_data["transaction"],
                    form.cleaned_data["date"],
                    form.cleaned_data["name"],
                    form.cleaned_data["amount"],
                    form.cleaned_data["save_sender"],
                    note,
                )
                if error:
                    messages.error(request, error)
                else:
                    messages.info(
                        request,
                        "Gebucht: %s/%s/%s/Fr. %s"
                        % (
                            transaction["date"],
                            transaction["person"],
                            transaction["note"],
                            transaction["amount"],
                        ),
                    )
                    get_next = True
        else:
            messages.error(request, "Form is invalid")
    else:
        get_next = True

    while get_next and "transaction_data" in request.session:
        if request.session["transaction_data"]:
            transaction = request.session["transaction_data"].pop()
            request.session["last_transaction"] = transaction
            initial = guess_transaction(transaction)
            info_text = "<ul><li>%s</li><li>%s</li><li>Fr. %s</li></ul>" % (
                transaction["person"],
                transaction["note"],
                transaction["amount"],
            )
            if initial["process"]:
                get_next = False
        else:
            info_text = "<ul><li>KEINE WEITEREN TRANSAKTIONEN MEHR GEFUNDEN</li></ul>"
            transaction = None
            get_next = False

    form = TransactionUploadProcessForm(None, initial=initial, transaction=transaction)
    return render(
        request,
        "geno/transaction_upload.html",
        {
            "response": ret,
            "title": "Bankauszug verarbeiten",
            "info": "Schritt 2: Buchungsaktionen auswählen",
            "form": form,
            "form_action": "/geno/transaction_upload/process/",
            "info_text": info_text,
        },
    )


@login_required
def transaction_testdata(request):
    if not settings.DEMO:
        return unauthorized(request)
    data = generate_demo_camt053_file()
    filename = f"camt053_demo_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    response = HttpResponse(data, content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def invoice_manual(request):
    if not request.user.has_perm("geno.transaction"):
        return unauthorized(request)

    error = False
    email_template = None
    InvoiceFormset = formset_factory(ManualInvoiceLineForm, extra=0)
    if request.method == "POST":
        form = ManualInvoiceForm(request.POST)
        formset = InvoiceFormset(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            ## TODO: Use InvoiceCreator to do this
            invoice_category = form.cleaned_data["category"]
            address = form.cleaned_data["address"]
            invoice_date = form.cleaned_data["date"]

            lines_count = 0
            total_amount = 0
            invoice_lines = []
            error = False
            comment = []
            for line in formset.cleaned_data:
                if line["amount"]:
                    if not len(line["text"]) or not line["date"]:
                        messages.error(
                            request,
                            "Zeile mit Betrag aber ohne Datum/Beschreibung! "
                            "Bitte eingeben oder Betrag löschen.",
                        )
                        error = True
                        break
                    line["date"] = line["date"].strftime("%d.%m.%Y")
                    line["total"] = nformat(line["amount"])
                    invoice_lines.append(line)
                    lines_count += 1
                    total_amount += line["amount"]
                    comment.append("%s CHF %s" % (line["text"], line["total"]))

            if not lines_count:
                messages.error(
                    request,
                    "Keine Rechnungspositionen eingegeben! Bitte mindestens eine Zeile ausfüllen.",
                )
                error = 1

            if (
                not error
                and "submit_action_pdf" in request.POST
                or "submit_action_mail" in request.POST
            ):
                dry_run = False
                if "submit_action_mail" in request.POST:
                    ## Send email
                    email_template = "email_invoice.html"

                invoice = add_invoice(
                    None,
                    invoice_category,
                    invoice_category.name,
                    invoice_date,
                    total_amount,
                    address=address,
                    comment="/".join(comment),
                )
                if isinstance(invoice, str):
                    messages.error(request, "Konnte Rechnungs-Objekt nicht erzeugen: %s" % invoice)
                    error = 1
                else:
                    invoice_id = invoice.id

            else:
                ## Test/Preview
                dry_run = True
                invoice_id = 9999999999

            if not error:
                ref_number = get_reference_nr(invoice_category, address.id, invoice_id)
                output_filename = "Rechnung_%s_%s_%s.pdf" % (
                    invoice_category.name,
                    invoice_date.strftime("%Y%m%d"),
                    esr.compact(ref_number),
                )
                context = address.get_context()
                if invoice_category.name == "Geschäftsstelle":
                    context["betreff"] = "Rechnung"
                else:
                    context["betreff"] = "Rechnung %s" % invoice_category.name
                context["extra_text"] = form.cleaned_data["extra_text"]
                context["invoice_date"] = invoice_date.strftime("%d.%m.%Y")
                context["invoice_duedate"] = (invoice_date + relativedelta(months=1)).strftime(
                    "%d.%m.%Y"
                )
                context["invoice_nr"] = invoice_id
                context["show_liegenschaft"] = False
                context["contract_info"] = None
                context["sect_rent"] = False
                context["sect_generic"] = True
                context["generic_info"] = invoice_lines
                context["s_generic_total"] = nformat(total_amount)
                context["qr_amount"] = total_amount
                context["qr_extra_info"] = "Rechnung %s" % context["invoice_nr"]
                context["preview"] = dry_run

                email_subject = "%s Nr. %s/%s" % (
                    context["betreff"],
                    context["invoice_nr"],
                    context["invoice_date"],
                )

                (ret, mails_sent, mail_recipient) = create_qrbill(
                    ref_number,
                    address,
                    context,
                    output_filename,
                    render,
                    email_template,
                    email_subject,
                    dry_run,
                )

                info = "%s CHF %s Nr. %s/%s, %s" % (
                    address,
                    total_amount,
                    context["invoice_nr"],
                    context["invoice_date"],
                    context["betreff"],
                )
                if ret:
                    print("ERROR MSG")
                    messages.error(
                        request, "Fehler beim erzeugen der Rechnung für %s: %s" % (info, ret)
                    )
                elif email_template:
                    if mails_sent == 1:
                        messages.success(
                            request,
                            "Email '%s' mit QR-Rechnung an %s geschickt. %s"
                            % (email_subject, mail_recipient, output_filename),
                        )
                    else:
                        messages.error(
                            request,
                            "FEHLER beim Versenden des Emails '%s' mit QR-Rechnung an %s! %s."
                            % (email_subject, mail_recipient, output_filename),
                        )
                else:
                    pdf_file = open("/tmp/%s" % output_filename, "rb")
                    resp = FileResponse(pdf_file, content_type="application/pdf")
                    resp["Content-Disposition"] = "attachment; filename=%s" % output_filename
                    return resp
    else:
        form = ManualInvoiceForm(initial={"date": datetime.date.today()})
        formset = InvoiceFormset(
            initial=[
                {"date": datetime.date.today()},
                {"date": datetime.date.today()},
                {"date": datetime.date.today()},
                {"date": datetime.date.today()},
                {"date": datetime.date.today()},
            ]
        )

    return render(
        request,
        "geno/invoice_manual.html",
        {"form": form, "formset": formset, "form_action": "/geno/invoice/", "error": error},
    )


@login_required
def rental_unit_list_tenants(request, export_xls=True):
    bewohnende = []
    bewohnende_mit_kinder_in_wohnung = []
    data = []
    include_subcontracts = request.GET.get("include_subcontracts", False)
    print('rental_unit_list_tenants', export_xls, include_subcontracts)
    data_fields = [
        "ru_name",
        "ru_type",
        "ru_floor",
        "ru_rooms",
        "ru_area",
        "organization",
        "name",
        "first_name",
        "title",
        "email",
        "child",
        "child_age",
        "child_presence",
        "date_birth",
        "city",
        "street",
        "tel1",
        "tel2",
        "hometown",
        "occupation",
        "membership_date",
        "emonitor_id",
    ]
    for c in get_active_contracts(include_subcontracts=include_subcontracts):
        is_wohnen = False
        for ru in c.rental_units.all():
            if ru.rental_type not in ("Gewerbe", "Lager", "Hobby"):
                is_wohnen = True
                break
        if c.children.exists():
            is_kinder = True
        else:
            is_kinder = False
        if is_wohnen:
            for adr in c.contractors.all():
                if adr not in bewohnende:
                    bewohnende.append(adr.email)
                if is_kinder and adr not in bewohnende_mit_kinder_in_wohnung:
                    bewohnende_mit_kinder_in_wohnung.append(adr.email)

        ## Create data objects
        for ru in c.rental_units.all():
            for adr in c.contractors.all():
                obj = lambda: None
                obj._fields = data_fields
                obj.ru_name = ru.name
                obj.ru_type = ru.rental_type
                obj.ru_floor = ru.floor
                obj.ru_rooms = ru.rooms
                obj.ru_area = ru.area
                obj.organization = adr.organization
                obj.name = adr.name
                obj.first_name = adr.first_name
                obj.title = adr.title
                obj.email = adr.email
                obj.child = False
                obj.child_age = None
                obj.child_presence = None
                obj.date_birth = adr.date_birth
                obj.city = adr.city
                obj.street = adr.street
                obj.tel1 = adr.telephone
                obj.tel2 = adr.mobile
                obj.hometown = adr.hometown
                obj.occupation = adr.occupation
                obj.emonitor_id = adr.emonitor_id
                try:
                    obj.membership_date = Member.objects.get(name=adr).date_join.strftime(
                        "%d.%m.%Y"
                    )
                except Member.DoesNotExist:
                    obj.membership_date = None
                if len("%s %s" % (obj.name, obj.first_name)) > 32:
                    print("WARNING: Name longer than 32 chars: %s %s" % (obj.name, obj.first_name))
                    logger.warning("Name longer than 32 chars: %s %s" % (obj.name, obj.first_name))

                data.append(obj)
            for child in c.children.all():
                obj = lambda: None
                obj._fields = data_fields
                obj.ru_name = ru.name
                obj.ru_type = ru.rental_type
                obj.ru_floor = ru.floor
                obj.ru_rooms = ru.rooms
                obj.ru_area = ru.area
                obj.organization = child.name.organization
                obj.name = child.name.name
                obj.first_name = child.name.first_name
                obj.title = child.name.title
                obj.email = child.name.email
                obj.child = True
                obj.child_age = child.age()
                obj.child_presence = child.presence
                obj.date_birth = child.name.date_birth
                obj.city = child.name.city
                obj.street = child.name.street
                obj.tel1 = child.name.telephone
                obj.tel2 = child.name.mobile
                obj.hometown = child.name.hometown
                obj.occupation = child.name.occupation
                obj.emonitor_id = child.emonitor_id
                obj.membership_date = None
                if len("%s %s" % (obj.name, obj.first_name)) > 32:
                    logger.warning("Name longer than 32 chars: %s %s" % (obj.name, obj.first_name))
                data.append(obj)

    if export_xls:
        return export_data_to_xls(
            data, title="Bewohnendenspiegel", header={}, filename_suffix="bewohnendenspiegel"
        )

    ret = []
    ret.append({"info": "Bewohnende (%d)" % len(bewohnende), "objects": bewohnende})
    ret.append(
        {
            "info": "Bewohnende in Wohnungen mit Kinder (%d)"
            % len(bewohnende_mit_kinder_in_wohnung),
            "objects": bewohnende_mit_kinder_in_wohnung,
        }
    )

    return render(
        request,
        "geno/messages.html",
        {"response": ret, "title": "Mieter*innenspiegel (WORK IN PROGRESS!)"},
    )


@login_required
def rental_unit_list_units(request, export_xls=True):
    data = []
    data_fields = [
        "ru_name",
        "ru_type",
        "ru_floor",
        "ru_area",
        "ru_area_add",
        "ru_height",
        "ru_rooms",
        "ru_occ",
        "n_adults",
        "n_children",
        "ru_nk",
        "ru_nk_electricity",
        "ru_rent_netto",
        "name",
        "first_name",
        "email",
        "name2",
        "first_name2",
        "other_names",
        "children",
        "contract_date",
        "comment",
    ]

    for ru in RentalUnit.objects.filter(active=True):
        obj = lambda: None
        obj._fields = data_fields
        if ru.label:
            obj.ru_name = "%s %s" % (ru.name, ru.label)
        else:
            obj.ru_name = "%s %s" % (ru.name, ru.rental_type)
        obj.ru_type = ru.rental_type
        obj.ru_floor = ru.floor

        # obj.ru_label = ru.label
        obj.ru_area = ru.area
        obj.ru_area_add = ru.area_add
        obj.ru_height = ru.height
        obj.ru_rooms = ru.rooms
        obj.ru_occ = ru.min_occupancy
        obj.n_adults = 0
        obj.n_children = 0
        obj.ru_nk = ru.nk
        obj.ru_nk_electricity = ru.nk_electricity
        obj.ru_rent_netto = ru.rent_netto

        ## Default values
        obj.name = "(Leerstand)"
        obj.first_name = ""
        obj.email = ""
        obj.name2 = ""
        obj.first_name2 = ""
        obj.contract_date = ""
        obj.comment = ""
        other_names = []
        children = []
        comments = []

        contracts = get_active_contracts().filter(rental_units__id__exact=ru.id)
        n_contracts = contracts.count()
        if n_contracts > 0:
            if n_contracts > 1:
                comments.append("ACHTUNG: MEHR ALS 1 VERTRAG!")
                print("WARNING: Rental unit %s has %d contracts!" % (ru, n_contracts))
                logger.warning("Rental unit %s has %d contracts!" % (ru, n_contracts))
            count = 0
            contract = contracts.first()
            if contract.main_contact:
                if contract.main_contact.organization:
                    obj.name = contract.main_contact.organization
                    obj.first_name = "%s %s" % (
                        contract.main_contact.first_name,
                        contract.main_contact.name,
                    )
                else:
                    obj.name = contract.main_contact.name
                    obj.first_name = contract.main_contact.first_name
                obj.email = contract.main_contact.email
                count += 1
            for adr in contract.contractors.all():
                if adr == contract.main_contact:
                    continue
                if adr.organization:
                    str_name = adr.organization
                    str_first_name = "%s %s" % (adr.first_name, adr.name)
                    str_full_name = "%s/%s %s" % (adr.organization, adr.first_name, adr.name)
                else:
                    str_name = adr.name
                    str_first_name = adr.first_name
                    str_full_name = "%s %s" % (adr.first_name, adr.name)
                if count == 0:
                    obj.name = str_name
                    obj.first_name = str_first_name
                    obj.email = adr.email
                elif count == 1:
                    obj.name2 = str_name
                    obj.first_name2 = str_first_name
                else:
                    other_names.append(str_full_name)
                count += 1
            obj.n_adults = count
            obj.contract_date = contract.date.strftime("%d.%m.%Y")

            for child in contracts.first().children.all():
                children.append(
                    "%s %s (%s)" % (child.name.first_name, child.name.name, child.age())
                )

        obj.other_names = ", ".join(other_names)
        obj.children = ", ".join(children)
        obj.n_children = len(children)
        obj.comment = ", ".join(comments)

        data.append(obj)

    if export_xls:
        return export_data_to_xls(
            data, title="Bewohnendenspiegel", header={}, filename_suffix="bewohnendenspiegel"
        )

    ret = []

    return render(
        request,
        "geno/messages.html",
        {"response": ret, "title": "Mietobjektespiegel (WORK IN PROGRESS!)"},
    )


@login_required
def rental_unit_list_create_documents(request, doc="mailbox"):
    if request.GET.get("makezip", "") == "yes":
        makezip = True
    else:
        makezip = False

    ret = []
    zipcount = 0
    zipfile_content = []
    if doc == "mailbox":
        options = {"beschreibung": "Briefkasten", "link_url": "/geno/rental/units/mailbox"}
    elif doc == "protocol":
        options = {"beschreibung": "Protokoll", "link_url": "/geno/rental/units/protocol"}
    else:
        raise RuntimeError("Unknown doc in rental_unit_list_create_documents '%s'." % doc)
    try:
        doctype = DocumentType.objects.get(name=doc)
        template = doctype.template.file.path
    except DocumentType.DoesNotExist:
        ret.append({"info": f"FEHLER: Dokumenttyp {doc} nicht gefunden."})
        return render(
            request,
            "geno/messages.html",
            {
                "response": ret,
                "title": "Mietobjekt-Dokumente erzeugen - %s" % options["beschreibung"],
            },
        )

    for ru in RentalUnit.objects.filter(active=True):
        context = {"title": ru.name}

        if ru.floor == "Keller":
            continue

        first_names = {}
        count_names = 0
        count_first_names = 0
        mietpartei = []

        contracts = get_active_contracts().filter(rental_units__id__exact=ru.id)
        n_contracts = contracts.count()
        if n_contracts > 0:
            if n_contracts > 1:
                print("WARNING: Rental unit %s has %d contracts!" % (ru, n_contracts))
                logger.warning("Rental unit %s has %d contracts!" % (ru, n_contracts))
            contract = contracts.first()
            for adr in contract.contractors.all():
                if adr.organization:
                    str_name = adr.organization
                    str_first_name = None
                    mietpartei.insert(0, str_name)
                else:
                    str_name = adr.name
                    str_first_name = adr.first_name
                    mietpartei.append("%s %s" % (str_first_name, str_name))
                if str_name not in first_names:
                    first_names[str_name] = []
                    count_names += 1
                if str_first_name:
                    first_names[str_name].append(str_first_name)
                    count_first_names += 1

            children_first_names = []
            for child in contracts.first().children.all():
                if child.name.name not in first_names:
                    first_names[child.name.name] = []
                    count_names += 1
                if child.name.first_name:
                    first_names[child.name.name].append(child.name.first_name)
                    children_first_names.append(child.name.first_name)
                    count_first_names += 1
            if children_first_names:
                if len(mietpartei) >= 10:
                    mietpartei = [mietpartei[0]] + [
                        ", ".join(x) for x in zip(mietpartei[1::2], mietpartei[2::2])
                    ]
                mietpartei.append("Kinder: %s" % ", ".join(children_first_names))

        if not first_names:
            continue

        lines = []
        for name in sorted(first_names):
            if first_names[name]:
                txt = ", %s" % (" & ".join(first_names[name]))
            else:
                txt = ""
            lines.append({"bold": name, "normal": txt})
        if len(mietpartei) > 10:
            raise RuntimeError("Mietpartei too long (%s lines)." % len(mietpartei))
        for _i in range(len(mietpartei), 10):
            mietpartei.append("")
        context["lines"] = lines
        context["mietpartei"] = mietpartei
        context["mietbeginn"] = contract.date.strftime("%d.%m.%Y")
        context["wohnungsnr"] = ru.name
        context["zimmer"] = ru.rooms

        zipcount += 1
        ret.append({"info": context["title"], "objects": context["mietpartei"]})
        if makezip:
            filename = fill_template_pod(template, context, output_format="odt")
            if not filename:
                raise RuntimeError("Could not fill template")
            zipfile_content.append(
                {
                    "file": filename,
                    "filename": "%s_%s.odt" % (options["beschreibung"], context["title"]),
                }
            )

    if makezip:
        ## Build ZIP-file from list of files
        file_like_object = io.BytesIO()
        zipfile_ob = zipfile.ZipFile(file_like_object, "w")
        for f in zipfile_content:
            # print "%s -> %s_%s" % (f['file'], f['member'].name.name,f['member'].name.first_name)
            zipfile_ob.write(f["file"], f["filename"])
        zipfile_ob.close()
        resp = HttpResponse(
            file_like_object.getvalue(), content_type="application/x-zip-compressed"
        )
        resp["Content-Disposition"] = "attachment; filename=%s" % "output.zip"
        return resp

    if zipcount > 0:
        link_text = "%s erstellen und herunterladen" % options["beschreibung"]
        ret.append(
            {
                "info": "Dokumente:",
                "objects": [
                    '<a href="%s?makezip=yes">%s (%d LibreOffice Dokumente in ZIP)</a>'
                    % (options["link_url"], link_text, zipcount)
                ],
            }
        )
    else:
        ret.append({"info": "Keine zu erstellenden Dokumente gefunden."})

    return render(
        request,
        "geno/messages.html",
        {"response": ret, "title": "Mietobjekt-Dokumente erzeugen - %s" % options["beschreibung"]},
    )


@login_required
def check_portal_users(request):
    if "portal" not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured(
            "check_portal_users() requires the portal app, with is not installed/enabled."
        )
    users = portal_auth.check_address_user_auth()
    ret = [
        {"info": "Benutzer ohne Login-Erlaubnis", "objects": users},
    ]
    return render(request, "geno/messages.html", {"response": ret, "title": "Benutzer überprüfen"})


@login_required
def check_duplicate_invoices(request):
    ret = [
        {"info": "Rechnungs-Duplikate", "objects": get_duplicate_invoices()},
    ]
    return render(
        request, "geno/messages.html", {"response": ret, "title": "Rechnungen überprüfen"}
    )


@login_required
def odt2pdf_form(request):
    initial = {}
    form = TransactionUploadFileForm(request.POST or None, request.FILES, initial=initial)
    if request.method == "POST":
        if form.is_valid():
            tmpdir = "/tmp/odt2pdf"
            if not os.path.isdir(tmpdir):
                os.mkdir(tmpdir)
            tmp_file = tempfile.NamedTemporaryFile(
                suffix=".odt", prefix="django_odt2pdf_input_", dir=tmpdir, delete=False
            )
            with open(tmp_file.name, "wb+") as destination:
                for chunk in request.FILES["file"].chunks():
                    destination.write(chunk)
            # resp = HttpResponse(odt2pdf(tmp_file.name), content_type = "application/pdf")
            pdf_file_path = odt2pdf(tmp_file.name, request.user.get_username())
            pdf_file = open(pdf_file_path, "rb")
            pdf_file_name = request.FILES["file"].name[0:-4]
            resp = FileResponse(pdf_file, content_type="application/pdf")
            resp["Content-Disposition"] = "attachment; filename=%s.pdf" % pdf_file_name
            if os.path.isfile(tmp_file.name):
                os.remove(tmp_file.name)
            if os.path.isfile(pdf_file_path):
                os.remove(pdf_file_path)
            return resp
    return render(
        request,
        "geno/upload_form.html",
        {
            "response": None,
            "title": "ODT in PDF umwandeln",
            "info": "LibreOffice Datei (.odt) hochladen",
            "form": form,
            "form_action": "/geno/odt2pdf/",
        },
    )


@login_required
def webstamp_form(request):
    ret = []
    download_redirect = None
    ## Get available stamps
    stamp_names = {
        "A-GROSS-ENV": "A-Post Grossbrief (C4, bis 500g)",
        "A-GROSS-SCHWER-ENV": "A-Post Grossbrief schwer (C4, 500-1000g)",
        "A-STANDARD-ENV": "A-Post Standardbrief (bis C5, 100g)",
        "B-STANDARD-ENV": "B-Post Standardbrief (bis C5, 100g)",
        "ECONOMY-EURO1-50g-ENV": "Europa Economy (bis C5, 50g)",
    }
    initial = {"stamp_type": "A-STANDARD-ENV"}
    cmd_out = subprocess.run(["/usr/local/bin/webstamp"], stdout=subprocess.PIPE)
    tmpdir = "/tmp/webstamp"
    type_list = False
    stamps = {}
    pattern = re.compile(r"^\s+- (?P<type>\S+)\s+\((?P<num>\d+) available")
    for line in cmd_out.stdout.decode("utf-8").splitlines():
        # print(line)
        if line == "   stamp types:":
            type_list = True
        elif type_list:
            m = pattern.search(line)
            if m.group("type") and m.group("num"):
                stamp_type = m.group("type")
                stamp_name = stamp_names.get(stamp_type, stamp_type)
                stamps[stamp_type] = "%s: %d verfügbar" % (stamp_name, int(m.group("num")))

    if request.method == "GET" and request.GET.get("get_download"):
        download_redirect = "/geno/webstamp/?download=%s" % request.GET.get("get_download")
    elif request.method == "GET" and request.GET.get("download"):
        tmp_file_name = request.GET.get("download")
        tmp_file_path = os.path.normpath(os.path.join(tmpdir, tmp_file_name))
        if not tmp_file_path.startswith(tmpdir):
            raise PermissionDenied()
        if os.path.isfile(tmp_file_path):
            pdf_file_name = "PDF_frankiert"
            resp = FileResponse(open(tmp_file_path, "rb"), content_type="application/pdf")
            resp["Content-Disposition"] = "attachment; filename=%s.pdf" % pdf_file_name
            os.remove(tmp_file_path)
            return resp
        else:
            raise Http404(f"File {tmp_file_name} not found.")
    if request.method == "POST":
        form = WebstampForm(request.POST, request.FILES, initial=initial, stamps_available=stamps)
        if form.is_valid():
            if not os.path.isdir(tmpdir):
                os.mkdir(tmpdir)
            tmp_files = []
            files = form.cleaned_data["files"]
            for f in files:
                tmp_file = tempfile.NamedTemporaryFile(
                    suffix=".pdf", prefix="django_webstamp_input_", dir=tmpdir, delete=False
                )
                with open(tmp_file.name, "wb+") as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                tmp_files.append(tmp_file.name)
            stamp_type = form.cleaned_data["stamp_type"]
            cmd_out = subprocess.run(
                ["/usr/local/bin/webstamp", "-t", stamp_type] + tmp_files, stdout=subprocess.PIPE
            )
            # print(cmd_out.stdout.decode('utf-8'))
            ret.append(
                {
                    "info": "Webstamp output:",
                    "objects": ["<pre>%s</pre>" % cmd_out.stdout.decode("utf-8")],
                }
            )
            ## Check if output files are there
            success = True
            for f in tmp_files:
                outfile = f[0:-4] + "_stamp.pdf"
                if os.path.isfile(outfile):
                    os.rename(outfile, f)
                else:
                    success = False
                    break
            if success:
                ## Concatenate stamped PDFs and return one PDF with all pages.
                tmp_file = tempfile.NamedTemporaryFile(
                    suffix=".pdf", prefix="django_webstamp_output_", dir=tmpdir, delete=False
                )
                pdfcat_out = subprocess.run(
                    ["pdftk"] + tmp_files + ["cat", "output", tmp_file.name],
                    stdout=subprocess.PIPE,
                )
                # print(pdfcat_out.stdout.decode('utf-8'))
                ret.append(
                    {
                        "info": "PDFtk output:",
                        "objects": ["<pre>%s</pre>" % pdfcat_out.stdout.decode("utf-8")],
                    }
                )
                for f in tmp_files:
                    os.remove(f)
                if os.path.isfile(tmp_file.name):
                    return redirect(
                        "/geno/webstamp/?get_download=%s" % os.path.basename(tmp_file.name)
                    )
    else:
        form = WebstampForm(initial=initial, stamps_available=stamps)
    return render(
        request,
        "geno/generic_upload.html",
        {
            "response": ret,
            "title": "PDFs frankieren",
            "info": (
                "PDF Dateien hochladen. Die erste Seite wird frankiert (Fenster-Couvert links)"
            ),
            "form": form,
            "form_action": "/geno/webstamp/",
            "download_redirect": download_redirect,
        },
    )


def oauth_client_test(request, action="start"):
    ret = []

    ## Secondary portal
    # base_url = settings.PORTAL_SECONDARY_HOST
    ## Main portal
    base_url = settings.BASE_URL

    client_id = ""
    client_secret = ""
    redirect_uri = f"{base_url}/geno/oauth_client/callback/"
    authorize_url = base_url + "/o/authorize/"
    access_token_url = base_url + "/o/token/"
    resource_url = base_url + "/portal/me/"

    ret.append({"info": "current django user: %s" % request.user})

    if action == "login":
        ## Start Authorization
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
        authorization_url, state = oauth.authorization_url(authorize_url)
        request.session["test_oauth_state"] = state
        request.session["test_oauth_origin_url"] = request.get_full_path()
        print("Redirecting to authorization URL: %s" % authorization_url)
        return redirect(authorization_url)
    elif action == "callback":
        oauth = OAuth2Session(
            client_id, state=request.session["test_oauth_state"], redirect_uri=redirect_uri
        )
        token = oauth.fetch_token(
            access_token_url,
            client_secret=client_secret,
            authorization_response=request.build_absolute_uri(
                settings.BASE_URL + request.get_full_path()
            ),
        )
        print("Got token: %s" % token)
        ## Save token to session
        request.session["test_oauth_token"] = token
        return redirect("/geno/oauth_client/test/")
    elif action == "access":
        if "test_oauth_token" not in request.session:
            ## Login first
            print("No token in session -> redirect to login")
            return oauth_client_test(request, action="login")

        access_token = request.session["test_oauth_token"]
        oauth = OAuth2Session(client_id, token=access_token)
        try:
            response = oauth.get(resource_url)
        except TokenExpiredError:
            try:
                ret.append({"info": "Refreshing token"})
                extra = {"client_id": client_id, "client_secret": client_secret}
                new_token = oauth.refresh_token(access_token_url, **extra)
                response = oauth.get(resource_url)
                ## Save token to session
                request.session["test_oauth_token"] = new_token
            except Exception:
                ## Could not refresh token
                print("Could not refresh token -> redirect to login")
                return oauth_client_test(request, action="login")

        if response.status_code == 200:
            ret.append({"info": "Response: %s" % response.json()})
            # for item in response.json():
            #    ret.append({'info': '%s' % (item)})
        else:
            ret.append(
                {
                    "info": "HTTP response status_code ist not 200!",
                    "objects": [
                        "status_code: %s" % response.status_code,
                    ],
                }
            )
    else:  ## Start
        if "test_oauth_token" in request.session:
            print("Forgeting token.")
            del request.session["test_oauth_token"]
        return oauth_client_test(request, action="login")
    return render(request, "geno/messages.html", {"response": ret, "title": "Oauth Client Test"})


def preview_template(request):
    invoice_category_id = request.GET.get("invoice_category", None)
    contract_id = request.GET.get("contract", None)
    if invoice_category_id and contract_id:
        invoice_category = InvoiceCategory.objects.get(id=invoice_category_id)
        mail_template = invoice_category.email_template.get_template()
        contract = Contract.objects.get(id=contract_id)
        address = contract.get_contact_address()
        context = address.get_context()
        mail_text_html = mail_template.render(Context(context))
        return HttpResponse(mail_text_html)
    else:
        return HttpResponse("Vorschau wird noch nicht unterstützt.")


def registration(request, registration_id=None):
    template_data = {}
    template_data["forms"] = process_registration_forms(request, selector=registration_id)
    return render(request, "website/registration_form.html", template_data)
