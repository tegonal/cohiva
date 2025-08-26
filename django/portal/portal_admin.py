import csv
import logging
from io import StringIO

from django.conf import settings
from django.contrib import auth
from django.utils import timezone

from geno.models import Address, Tenant

from .forms import PortalPasswordResetForm

logger = logging.getLogger("access_portal")


def send_invitation_mails(id_list):
    success_count = 0
    errors = []

    UserModel = auth.get_user_model()
    email_field_name = UserModel.get_email_field_name()
    for tenant_id in id_list:
        try:
            t = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            errors.append("Nutzer:in mit ID %s nicht gefunden." % tenant_id)
            continue

        context = {
            "portal_name": settings.PORTAL_SECONDARY_NAME,
            "anrede": "%s %s" % (t.name.first_name, t.name.name),
            "base_url": "https://%s" % settings.PORTAL_SECONDARY_HOST,
            "email_signature": settings.PORTAL_SECONDARY_SIGNATURE,
        }

        form = PortalPasswordResetForm(settings.PORTAL_SECONDARY_HOST, {"email": t.name.email})
        if form.is_valid():
            if t.name.user:
                ## Send email for existing users
                message_template = "portal/password_invitation_email_existing_user.html"
            else:
                ## Create user and send email
                message_template = "portal/password_invitation_email.html"
                if UserModel._default_manager.filter(
                    **{
                        "%s__iexact" % email_field_name: t.name.email,
                        "is_active": True,
                    }
                ).count():
                    errors.append(
                        "Es existiert bereits ein anderer Benutzer mit der Email-Adresse %s. Konnte diesen Benutzer nicht erstellen/keine Einladung senden."
                        % t.name.email
                    )
                    continue
            form.save(
                subject_template_name="portal/password_invitation_subject.txt",
                email_template_name=message_template,
                extra_email_context=context,
            )
            success_count += 1
            t.invitation_date = timezone.now()
            t.save()
        else:
            errors.append("Invalid form for %s." % t.name.email)
    if errors:
        if success_count:
            return (
                "Es wurden %s Emails verschickt, aber es sind folgende Fehler aufgetreten:<br>%s"
                % (success_count, "<br>".join(errors))
            )
        else:
            return (
                "Es wurden keine Emails verschickt. Es sind folgende Fehler aufgetreten:<br>%s"
                % ("<br>".join(errors))
            )
    else:
        return success_count


def deactivate_tenants(id_list):
    success_count = 0
    errors = []

    for tenant_id in id_list:
        try:
            t = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            errors.append("Nutzer:in mit ID %s nicht gefunden." % tenant_id)
            continue
        t.active = False
        t.save()
        logger.info("Deactivated tenant: %s (id=%s)" % (t, tenant_id))
        success_count += 1

    if errors:
        if success_count:
            return (
                "Es wurden %s Nutzer:innen deaktiviert, aber es sind folgende Fehler aufgetreten:<br>%s"
                % (success_count, "<br>".join(errors))
            )
        else:
            return (
                "Es wurden keine Nutzer:innen deaktiviert. Es sind folgende Fehler aufgetreten:<br>%s"
                % ("<br>".join(errors))
            )
    else:
        return success_count


def process_tenant_file(uploadfile, replace_existing=False):
    if uploadfile.size > 50 * 1024 * 1024:
        return {"error": "Datei ist zu gross!"}

    csvdata = uploadfile.read()
    try:
        csvstring = csvdata.decode("utf-8")
    except UnicodeDecodeError:
        csvstring = csvdata.decode("iso8859")
    dialect = csv.Sniffer().sniff(csvstring[0 : min(1024, len(csvstring))])
    csvreader = csv.reader(StringIO(csvstring), dialect)
    header = True

    columns = {"Name": None, "Vorname": None, "Email": None}
    data = []

    for row in csvreader:
        if header:
            for i, val in enumerate(row):
                val = val.strip()
                if val in columns:
                    columns[val] = i
            for c in columns:
                if columns[c] is None:
                    return {"error": "Spalte mit Überschrift '%s' nicht gefunden." % c}
            header = False
        else:
            d = {}
            empty = None
            allempty = True
            for c in columns:
                d[c] = row[columns[c]].strip()
                if d[c] == "":
                    empty = c
                else:
                    allempty = False
            if not allempty:
                if empty:
                    return {"error": "Leere Spalte '%s' bei Datensatz %s." % (empty, row)}
                else:
                    data.append(d)

    return prepare_add_tenants(data)


def prepare_add_tenants(data):
    tenants_add = []
    tenants_ignore = []
    tenants_delete = []
    tenants_unchanged = []

    UserModel = auth.get_user_model()
    email_field_name = UserModel.get_email_field_name()

    new_emails = []

    for user in data:
        ## Check if tenant exists already
        try:
            tenant = Tenant.objects.get(name__email=user["Email"])
            if tenant.name.name == user["Name"] and tenant.name.first_name == user["Vorname"]:
                if not tenant.active:
                    ## Re-activate tenant
                    user["tenant_id"] = tenant.id
                    tenants_add.append(user)
                else:
                    tenants_unchanged.append(user)
            else:
                user["reason"] = (
                    "Nutzer:in mit Email %s existiert bereits mit anderem Namen: %s %s"
                    % (tenant.name.email, tenant.name.first_name, tenant.name.name)
                )
                tenants_ignore.append(user)
            continue
        except Tenant.MultipleObjectsReturned:
            logger.error("Multiple tentants with same email: %s" % (user["Email"]))
            user["reason"] = (
                "Es existieren bereits mehrere Nutzer:innen mit Email %s." % (user["Email"])
            )
            tenants_ignore.append(user)
            continue
        except Tenant.DoesNotExist:
            pass

        ## Check if we have address already
        try:
            adr = Address.objects.get(email=user["Email"])
            if adr.name == user["Name"] and adr.first_name == user["Vorname"]:
                user["address_id"] = adr.id
                tenants_add.append(user)
            else:
                user["reason"] = (
                    "Die Email %s ist bereits mit anderem Namen registriert: '%s' '%s'"
                    % (adr.email, adr.first_name, adr.name)
                )
                tenants_ignore.append(user)
            continue
        except Address.MultipleObjectsReturned:
            logger.error("Multiple addresses with same email: %s" % (user["Email"]))
            user["reason"] = "Die Email %s ist bereits mehrfach registriert." % (user["Email"])
            tenants_ignore.append(user)
            continue
        except Address.DoesNotExist:
            pass

        ## Make sure we don't have a user with that email already
        if UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: user["Email"],
                "is_active": True,
            }
        ).count():
            user["reason"] = "User mit Email %s existiert bereits." % (user["Email"])
            tenants_ignore.append(user)
        elif user["Email"] in new_emails:
            user["reason"] = "Email %s doppelt in der Liste vorhanden." % (user["Email"])
            tenants_ignore.append(user)
        else:
            new_emails.append(user["Email"])
            tenants_add.append(user)

    return {
        "tenants_add": tenants_add,
        "tenants_ignore": tenants_ignore,
        "tenants_delete": tenants_delete,
        "tenants_unchanged": tenants_unchanged,
    }
