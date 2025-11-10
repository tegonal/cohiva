import datetime
import json
import logging

from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required  # , user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django_tables2 import RequestConfig
from oauth2_provider.decorators import protected_resource
from wagtail.models import Site as WagtailSite
from wagtail.views import serve as wagtail_serve

import portal.auth as portal_auth
from geno.models import Address, Building, Tenant
from geno.utils import send_error_mail, send_info_mail

from .forms import (
    PortalPasswordResetForm,
    TenantAdminEditForm,
    TenantAdminTableFilterForm,
    TenantAdminUploadForm,
)
from .models import TenantAdmin
from .portal_admin import (
    deactivate_tenants,
    prepare_add_tenants,
    process_tenant_file,
    send_invitation_mails,
)
from .rocketchat import RocketChatContrib
from .tables import TenantAdminTable

logger = logging.getLogger("access_portal")

UserModel = auth.get_user_model()


## Determine portal/site name from hostname and initialize template data accordingly
def template_from_portal_site(request):
    if request.get_host() == settings.PORTAL_SECONDARY_HOST:
        template_data = {"portal_name": settings.PORTAL_SECONDARY_NAME}
        template_data["template_base"] = "portal/base_secondary.html"
        template_data["email_signature"] = f"Siedlung {settings.PORTAL_SECONDARY_NAME}"
        template_data["base_url"] = "https://%s" % settings.PORTAL_SECONDARY_HOST
    else:
        template_data = {"portal_name": settings.COHIVA_SITE_NICKNAME}
        template_data["template_base"] = "portal/base.html"
        template_data["meta_description"] = f"Mitglieder-Portal {settings.COHIVA_SITE_NICKNAME}"
        template_data["background_image"] = settings.PORTAL_BACKGROUND
        template_data["support_email"] = settings.GENO_DEFAULT_EMAIL
        template_data["email_signature"] = settings.GENO_NAME
        template_data["geno_name"] = settings.GENO_NAME
        template_data["base_url"] = "%s" % settings.BASE_URL
    return template_data


@sensitive_post_parameters("password")
def login(request):
    template_data = template_from_portal_site(request)
    portal_name = template_data["portal_name"]

    if request.method == "POST":
        if "register" in request.POST:
            return render(request, "portal/password_reset.html", template_data)
        if "next" in request.POST:
            template_data["next"] = request.POST["next"]
        username = request.POST["username"]
        password = request.POST["password"]
        if "@" in username:
            ## Assume email -> map to user
            user_with_email = UserModel.objects.filter(email=username).first()
            if user_with_email:
                logger.info(
                    '%s [%s] - Mapping email "%s" to username "%s" for login.'
                    % (
                        request.META["REMOTE_ADDR"],
                        portal_name,
                        username,
                        user_with_email.username,
                    )
                )
                username = user_with_email.username
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_info = portal_auth.authorize(user, request.get_host())
                if not auth_info["user_id"]:
                    template_data["login_error"] = "Keine Berechtigung für diesen Zugang."
                    logger.error(
                        "%s [%s] - Login DENIED: %s"
                        % (request.META["REMOTE_ADDR"], portal_name, auth_info["reason"])
                    )
                else:
                    auth.login(request, user)
                    logger.info(
                        "%s [%s] - Login successful. u=%s redirect=%s"
                        % (
                            request.META["REMOTE_ADDR"],
                            portal_name,
                            username,
                            request.POST["next"],
                        )
                    )
                    if request.POST["next"] and url_has_allowed_host_and_scheme(
                        request.POST["next"], allowed_hosts=None
                    ):
                        return redirect(request.POST["next"])
                    else:
                        return redirect("/portal/")
            else:
                # Return a 'disabled account' error message
                template_data["login_error"] = (
                    "Der Zugang ist momentan deaktiviert. Bitte versuche es später nochmals."
                )
                logger.error(
                    "%s [%s] - Disabled account warning. u=%s"
                    % (request.META["REMOTE_ADDR"], portal_name, username)
                )
        else:
            # Return an 'invalid login' error message.
            template_data["login_error"] = (
                "Das eingegebene Passwort oder der Benutzername ist ungültig. Bitte versuche es nochmals."
            )
            logger.warning(
                "%s [%s] - Invalid password. u=%s"
                % (request.META["REMOTE_ADDR"], portal_name, username)
            )
    else:
        template_data["next"] = request.GET.get("next", "/portal/")
    return render(request, "portal/login.html", template_data)


def logout(request):
    template_data = template_from_portal_site(request)
    logger.info(
        "%s - %s Logout user=%s." % (request.META["REMOTE_ADDR"], request.get_host(), request.user)
    )
    auth.logout(request)
    template_data["login_success"] = "Du hast dich erfolgreich abgemeldet."
    return render(request, "portal/login.html", template_data)


class PasswordResetViewHostbased(auth.views.PasswordResetView):
    def get_form_kwargs(self):
        """Add hostname to kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs.update({"host": self.request.get_host()})
        return kwargs

    def form_valid(self, form):
        ret = super().form_valid(form)
        if form.redirect_url:
            ## Redirect to URL provided by form processing.
            return HttpResponseRedirect(form.redirect_url)
        return ret

    def get(self, request, *args, **kwargs):
        if request.GET.get("autosubmit"):
            ## Auto-submit with email
            form_kwargs = self.get_form_kwargs()
            form_kwargs["data"] = self.request.GET
            form_class = self.get_form_class()
            form = form_class(**form_kwargs)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        return self.render_to_response(self.get_context_data())


def password_reset(request):
    template_data = template_from_portal_site(request)
    view = PasswordResetViewHostbased.as_view(
        template_name="portal/password_reset.html",
        email_template_name="portal/password_reset_email.html",
        subject_template_name="portal/password_reset_subject.txt",
        success_url="/portal/password_reset/done/",
        extra_context=template_data,
        extra_email_context=template_data,
        form_class=PortalPasswordResetForm,
    )
    return view(request)


def password_reset_done(request):
    template_data = template_from_portal_site(request)
    view = auth.views.PasswordResetDoneView.as_view(
        template_name="portal/password_reset_done.html", extra_context=template_data
    )
    return view(request)


def password_reset_confirm(request, **kwargs):
    template_data = template_from_portal_site(request)
    view = auth.views.PasswordResetConfirmView.as_view(
        template_name="portal/password_reset_confirm.html",
        success_url="/portal/reset/done/",
        extra_context=template_data,
    )
    return view(request, **kwargs)


def password_reset_complete(request):
    template_data = template_from_portal_site(request)
    view = auth.views.PasswordResetCompleteView.as_view(
        template_name="portal/password_reset_complete.html", extra_context=template_data
    )
    return view(request)


def unauthorized(request):
    c = {
        "response": [{"info": "Sie haben keine Berechtigung für diese Aktion."}],
        "title": "Keine Berechtigung",
    }
    return render(request, "geno/default.html", c)


@login_required
def home(request, message=None):
    template_data = template_from_portal_site(request)
    if (
        not request.user.is_anonymous
        and TenantAdmin.objects.filter(name__user=request.user).count()
    ):
        template_data["is_tenant_admin"] = True
    if template_data["portal_name"] == settings.PORTAL_SECONDARY_NAME:
        if message:
            template_data["message"] = message
        return render(request, "portal/secondary.html", template_data)
    # view = RedirectView.as_view(url='/portal/home/', permanent=False)
    # return view(request)
    # check_address_user_auth()
    return redirect("/portal/home/")


def portal_cms_serve(request: WSGIRequest, path: str = ""):
    # Manually assign the "portal" site to requests that are routed to this view
    portal_site = WagtailSite.objects.filter(
        Q(hostname__startswith="portal") | Q(hostname__endswith="portal")
    ).first()
    if portal_site:
        request._wagtail_site = portal_site
    else:
        raise Http404("Keine Portal Site im CMS gefunden.")
    print("CMS serve " + path)
    return wagtail_serve(request, path)


@protected_resource(scopes=["username", "email", "realname"])
def oauth_identity(request):
    profile = portal_auth.get_oauth_profile(request)
    if not profile:
        return HttpResponse("Unauthorized", status=401)
    else:
        return HttpResponse(
            json.dumps(profile),
            content_type="application/json",
        )


def debug_middleware(get_response):
    def middleware(request):
        print(request.body)
        print(request.scheme)
        print(request.method)
        # print(request.META)
        response = get_response(request)
        print(response)
        print(response.content)
        return response

    return middleware


@login_required
def tenant_admin_table(request):
    template_data = template_from_portal_site(request)
    if "success_msg" in request.session:
        template_data["success_msg"] = request.session["success_msg"]
        del request.session["success_msg"]
    if "error_msg" in request.session:
        template_data["error_msg"] = request.session["error_msg"]
        del request.session["error_msg"]
    if request.user.is_anonymous:
        logger.error(
            "%s - tenant_admin_table(): no anonymous access" % (request.META["REMOTE_ADDR"])
        )
        return home(request, message="FEHLER: Unerlaubter Zugriff.")
    try:
        tenant_admin = TenantAdmin.objects.get(name__user=request.user)
    except TenantAdmin.DoesNotExist:
        logger.error(
            "%s - tenant_admin_table(): no tenant admin found for user %s"
            % (request.META["REMOTE_ADDR"], request.user.username)
        )
        return home(request, message="FEHLER: Keine Berechtigung für diese Aktion.")

    tenant_admin_buildings = list(tenant_admin.buildings.all())

    if request.POST:
        template_data["form"] = TenantAdminTableFilterForm(request.POST)
    else:
        template_data["form"] = TenantAdminTableFilterForm()
        # form = TenantAdminListTableForm(initial=initial)
    tenants = Tenant.objects.filter(active=True).filter(building__in=tenant_admin_buildings)
    if template_data["form"].is_valid():
        search = template_data["form"].cleaned_data["search"]
        tenants = tenants.filter(
            Q(name__name__icontains=search)
            | Q(name__first_name__icontains=search)
            | Q(name__email__icontains=search)
            | Q(name__organization__icontains=search)
        )
        if request.POST.get("submit_action"):
            selection = request.POST.getlist("selection")
            if not selection:
                template_data["error_msg"] = (
                    "Es müssen Objekte aus der Liste ausgewählt werden um Aktionen durchzuführen."
                )
            else:
                if template_data["form"].cleaned_data["action"] == "deactivate":
                    ret = deactivate_tenants(selection)
                    if isinstance(ret, str):
                        template_data["error_msg"] = ret
                    else:
                        template_data["success_msg"] = (
                            "Es wurden %s Nutzer:innen deaktiviert." % ret
                        )
                elif template_data["form"].cleaned_data["action"] == "invite":
                    ret = send_invitation_mails(selection)
                    if isinstance(ret, str):
                        template_data["error_msg"] = ret
                    else:
                        template_data["success_msg"] = (
                            "Es wurden %s Einladungs-Mails verschickt." % ret
                        )
                else:
                    template_data["error_msg"] = "Es wurde keine gültige Aktion ausgewählt."

    template_data["table"] = TenantAdminTable(tenants)
    # template_data['table'].order_by = "-total"
    RequestConfig(request, paginate={"per_page": 100}).configure(template_data["table"])
    template_data["section_title"] = "Nutzer:innen Administration"
    return render(request, "portal/table.html", template_data)


@login_required
def tenant_admin_edit(request, tenant_id=None):
    template_data = template_from_portal_site(request)
    if request.user.is_anonymous:
        logger.error(
            "%s - tenant_admin_edit(): no anonymous access" % (request.META["REMOTE_ADDR"])
        )
        return home(request, message="FEHLER: Unerlaubter Zugriff.")
    try:
        tenant_admin = TenantAdmin.objects.get(name__user=request.user)
    except TenantAdmin.DoesNotExist:
        logger.error(
            "%s - tenant_admin_edit(): no tenant admin found for user %s"
            % (request.META["REMOTE_ADDR"], request.user.username)
        )
        return home(request, message="FEHLER: Keine Berechtigung für diese Aktion.")

    if tenant_admin.buildings.count() == 1:
        building = tenant_admin.buildings.first()
    else:
        return home(request, message="FEHLER: Multi-Building Admin not implemented yet.")

    if tenant_id:
        template_data["tenant_id"] = tenant_id
        template_data["section_title"] = "Nutzer:in ändern"
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
            initial = {
                "name": tenant.name.name,
                "first_name": tenant.name.first_name,
                "email": tenant.name.email,
                "send_invitation": False,
            }
        except Tenant.DoesNotExist:
            template_data["error"] = "Nutzer:in nicht gefunden."
            initial = {}
    else:
        template_data["section_title"] = "Nutzer:in hinzufügen"
        initial = {}

    if request.POST:
        form = TenantAdminEditForm(request.POST)
        if form.is_valid():
            if tenant_id:
                ## Update adr
                adr = tenant.name
                error = None
                ## Check that email is unique
                try:
                    other_adr = Address.objects.get(email=form.cleaned_data["email"])
                    if adr != other_adr:
                        error = (
                            "Nutzer:in mit Email %s existiert bereits."
                            % form.cleaned_data["email"]
                        )
                except Address.MultipleObjectsReturned:
                    logger.error(
                        "Multiple addresses with same email: %s" % (form.cleaned_data["email"])
                    )
                    error = (
                        "Die Email %s ist bereits mehrfach registriert."
                        % (form.cleaned_data["email"])
                    )
                except Address.DoesNotExist:
                    pass

                if error:
                    template_data["error"] = error
                else:
                    logger.info(
                        "Updating address: %s -> %s, %s -> %s, %s -> %s"
                        % (
                            adr.name,
                            form.cleaned_data["name"],
                            adr.first_name,
                            form.cleaned_data["first_name"],
                            adr.email,
                            form.cleaned_data["email"],
                        )
                    )
                    adr.name = form.cleaned_data["name"]
                    adr.first_name = form.cleaned_data["first_name"]
                    adr.email = form.cleaned_data["email"]
                    adr.save()
                    request.session["success_msg"] = "Nutzer:in %s %s gespeichert." % (
                        adr.first_name,
                        adr.name,
                    )
                    return redirect("/portal/tenant-admin/")
            else:
                ## Add
                check = prepare_add_tenants(
                    [
                        {
                            "Name": form.cleaned_data["name"],
                            "Vorname": form.cleaned_data["first_name"],
                            "Email": form.cleaned_data["email"],
                        }
                    ]
                )
                if check["tenants_unchanged"]:
                    template_data["error"] = "Nutzer:in existiert bereits."
                elif check["tenants_ignore"]:
                    template_data["error"] = check["tenants_ignore"][0]["reason"]
                else:
                    user = check["tenants_add"][0]
                    if "tenant_id" in user:
                        ## Re-activate tenant
                        new_tenant = Tenant.objects.get(id=user["tenant_id"])
                        new_tenant.active = True
                        logger.info("Re-activating tenant %s: %s" % (user["Email"], new_tenant))
                    else:
                        if "address_id" in user:
                            adr = Address.objects.get(id=user["address_id"])
                            logger.info(
                                "Adding new tenant %s with existing address %s."
                                % (user["Email"], adr)
                            )
                        else:
                            adr = Address(
                                name=user["Name"], first_name=user["Vorname"], email=user["Email"]
                            )
                            adr.save()
                            logger.info(
                                "Adding new tenant %s and address %s." % (user["Email"], adr)
                            )
                        new_tenant = Tenant(
                            name=adr,
                            building=building,
                            notes="Erstellt im Nutzer:innen-Backend von %s am %s"
                            % (request.user, datetime.datetime.now()),
                        )
                    new_tenant.save()
                    request.session["success_msg"] = "Nutzer:in %s %s hinzugefügt." % (
                        user["Vorname"],
                        user["Name"],
                    )
                    return redirect("/portal/tenant-admin/")

    else:
        form = TenantAdminEditForm(initial=initial)

    template_data["form"] = form
    return render(request, "portal/tenant_edit.html", template_data)


@login_required
def tenant_admin_upload(request):
    template_data = template_from_portal_site(request)
    if request.user.is_anonymous:
        logger.error(
            "%s - tenant_admin_edit(): no anonymous access" % (request.META["REMOTE_ADDR"])
        )
        return home(request, message="FEHLER: Unerlaubter Zugriff.")
    try:
        TenantAdmin.objects.get(name__user=request.user)
    except TenantAdmin.DoesNotExist:
        logger.error(
            "%s - tenant_admin_edit(): no tenant admin found for user %s"
            % (request.META["REMOTE_ADDR"], request.user.username)
        )
        return home(request, message="FEHLER: Keine Berechtigung für diese Aktion.")

    form = TenantAdminUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            if request.FILES:
                data = process_tenant_file(
                    request.FILES["csv_file"]
                )  # , form.cleaned_data['replace_existing'])
            else:
                data = {"error": "Keine Datei gefunden."}
            if "error" in data:
                template_data["error"] = data["error"]
            else:
                request.session["tenants_add"] = data["tenants_add"]
                request.session["tenants_ignore"] = data["tenants_ignore"]
                request.session["tenants_delete"] = data["tenants_delete"]
                request.session["tenants_unchanged"] = data["tenants_unchanged"]
                # request.session['send_invitation'] = form.cleaned_data['send_invitation']
                return HttpResponseRedirect("/portal/tenant-admin/upload/commit")

    template_data["form"] = form
    template_data["multipart_form"] = True
    template_data["submit_button_text"] = "Weiter"
    template_data["section_title"] = "Nutzer:innen importieren"
    return render(request, "portal/tenant_edit.html", template_data)


@login_required
def tenant_admin_upload_commit(request):
    template_data = template_from_portal_site(request)
    if request.user.is_anonymous:
        logger.error(
            "%s - tenant_admin_edit(): no anonymous access" % (request.META["REMOTE_ADDR"])
        )
        return home(request, message="FEHLER: Unerlaubter Zugriff.")
    try:
        tenant_admin = TenantAdmin.objects.get(name__user=request.user)
    except TenantAdmin.DoesNotExist:
        logger.error(
            "%s - tenant_admin_edit(): no tenant admin found for user %s"
            % (request.META["REMOTE_ADDR"], request.user.username)
        )
        return home(request, message="FEHLER: Keine Berechtigung für diese Aktion.")

    if request.method == "POST":
        if "cancel" in request.POST:
            del request.session["tenants_add"]
            del request.session["tenants_ignore"]
            del request.session["tenants_delete"]
            del request.session["tenants_unchanged"]
            return HttpResponseRedirect("/portal/tenant-admin/")

        if tenant_admin.buildings.count() == 1:
            building = tenant_admin.buildings.first()
        else:
            return home(request, message="FEHLER: Multi-Building Admin not implemented yet.")

        count_add = 0
        for user in request.session["tenants_add"]:
            if "tenant_id" in user:
                ## Re-activate tenant
                new_tenant = Tenant.objects.get(id=user["tenant_id"])
                new_tenant.active = True
                logger.info("Re-activating tenant %s: %s" % (user["Email"], new_tenant))
            else:
                if "address_id" in user:
                    adr = Address.objects.get(id=user["address_id"])
                    logger.info(
                        "Adding new tenant %s with existing address %s." % (user["Email"], adr)
                    )
                else:
                    adr = Address(
                        name=user["Name"], first_name=user["Vorname"], email=user["Email"]
                    )
                    adr.save()
                    logger.info("Adding new tenant %s and address %s." % (user["Email"], adr))
                new_tenant = Tenant(
                    name=adr,
                    building=building,
                    notes="Erstellt durch Nutzer:innen-Upload von %s am %s"
                    % (request.user, datetime.datetime.now()),
                )
            new_tenant.save()
            count_add += 1

        del request.session["tenants_add"]
        del request.session["tenants_ignore"]
        del request.session["tenants_delete"]
        del request.session["tenants_unchanged"]

        if count_add:
            request.session["success_msg"] = "%s Nutzer:innen hinzugefügt." % (count_add)
            return HttpResponseRedirect("/portal/tenant-admin/")
        else:
            request.session["error_msg"] = "Keine Änderungen"
            return HttpResponseRedirect("/portal/tenant-admin/")

    template_data["form"] = None
    template_data["adding"] = request.session["tenants_add"]
    template_data["ignore"] = request.session["tenants_ignore"]
    template_data["delete"] = request.session["tenants_delete"]
    template_data["unchanged"] = request.session["tenants_unchanged"]
    template_data["submit_button_text"] = "Aktionen ausführen"
    template_data["section_title"] = "Nutzer:innen importieren"
    return render(request, "portal/tenant_edit.html", template_data)


def tenant_admin_get_rc_users(rocket, template_data):
    ## Get all RC users
    rc_users = {}
    ret = rocket.users_list(count=0).json()
    if not ret["success"]:
        template_data["error"] = "Can't get user list: %s" % ret.get("error", "Unknown error")
        return None
    for user in ret["users"]:
        if "username" in user:
            rc_users[user["username"]] = user
        else:
            template_data["warning"].append(
                f"Ignoring user without username: {user.get('name', 'Unknown')}/{user.get('_id', '-')}"
            )
    template_data["log"].append("Loaded %d Rocket.Chat users." % len(rc_users))
    return rc_users


def tenant_admin_perform_actions(action_list, rocket, rc_users, template_data, dry_run=False):
    add_team_members = {}
    for item in action_list:
        action = item.split("_")
        if action[0] in ("addtoteam", "deactivate", "activate"):
            tenant_id = action[1]
            try:
                tenant = Tenant.objects.get(id=tenant_id)
            except Tenant.DoesNotExist:
                template_data["warning"].append(f"Nutzer:in mit ID {tenant_id} nicht gefunden.")
                logger.warning(f"Nutzer:in mit ID {tenant_id} nicht gefunden.")
                continue
            if tenant.name.user.username in rc_users:
                if action[0] == "addtoteam":
                    if tenant.building.team not in add_team_members:
                        add_team_members[tenant.building.team] = []
                    add_team_members[tenant.building.team].append(
                        {"userId": rc_users[tenant.name.user.username]["_id"], "roles": ["member"]}
                    )
                elif action[0] in ("deactivate", "activate"):
                    if action[0] == "deactivate":
                        set_to = False
                        set_msg = "deaktiviert"
                        set_msg2 = "Deaktivieren"
                    else:
                        set_to = True
                        set_msg = "aktiviert"
                        set_msg2 = "Aktivieren"
                    if dry_run:
                        template_data["success"].append(
                            f"DRY-RUN: Chat-Benutzer {tenant.name.user.username} {set_msg}."
                        )
                    else:
                        ret = rocket.users_set_active_status(
                            rc_users[tenant.name.user.username]["_id"],
                            set_to,
                            confirmRelinquish=True,
                        ).json()
                        if ret["success"]:
                            rc_users[tenant.name.user.username]["active"] = ret["user"]["active"]
                            if ret["user"]["active"] == set_to:
                                template_data["success"].append(
                                    f"Chat-Benutzer {tenant.name.user.username} {set_msg}."
                                )
                                logger.info(
                                    f"Chat-Benutzer {tenant.name.user.username} {set_msg}."
                                )
                            else:
                                template_data["warning"].append(
                                    f"Chat-Benutzer {tenant.name.user.username} (ID {rc_users[tenant.name.user.username]['_id']}) konnte NICHT {set_msg} werden."
                                )
                                logger.warning(
                                    f"Chat-Benutzer {tenant.name.user.username} (ID {rc_users[tenant.name.user.username]['_id']}) konnte NICHT {set_msg} werden."
                                )
                        else:
                            if "error" not in ret:
                                ret["error"] = "Unbekannter Fehler"
                            template_data["warning"].append(
                                f"Fehler beim {set_msg2} des Chat-Benutzers {tenant.name.user.username} (ID {rc_users[tenant.name.user.username]['_id']}): {ret['error']}"
                            )
                            logger.error(
                                f"Fehler beim {set_msg2} des Chat-Benutzers {tenant.name.user.username} (ID {rc_users[tenant.name.user.username]['_id']}): {ret['error']}"
                            )
                    ## Removing from team is not required, since deactivated users don't show up in teams anymore. If they are re-activated they still belong to the team.
                    # if tenant.building.team:
                    #    ret = rocket.contrib_remove_team_member(tenant.building.team, rc_users[tenant.name.user.username]["_id"]).json()
                    #    if ret['success']:
                    #        template_data['success'].append(f'Chat-Benutzer {tenant.name.user.username} wurde vom Team {tenant.building.team} entfernt.')
                    #    else:
                    #        if 'error' not in ret:
                    #            ret['error'] = "Unbekannter Fehler"
                    #        template_data['warning'].append(f'Chat-Benutzers {tenant.name.user.username} (ID {rc_users[tenant.name.user.username]["_id"]}) konnte NICHT vom Team {tenant.building.team} entfernt werden: {ret["error"]}')
                    ## TODO: Do we also need to force a logout of the user? How?
            else:
                template_data["warning"].append(
                    f"Rocket.Chat Benutzername {tenant.name.user.username} nicht gefunden für Nutzer:in mit ID {tenant_id}."
                )
                logger.warning(
                    f"Rocket.Chat Benutzername {tenant.name.user.username} nicht gefunden für Nutzer:in mit ID {tenant_id}."
                )
        else:
            template_data["warning"].append(f"Unbekannte Aktion: {action[0]}")
            logger.warning(f"Unbekannte Aktion: {action[0]}")
    for team in add_team_members:
        if dry_run:
            template_data["success"].append(
                f"DRY-RUN: {len(add_team_members[team])} Nutzer:innen zum Team {team} hinzugefügt."
            )
        else:
            ret = rocket.contrib_add_team_members(team, add_team_members[team]).json()
            if ret["success"]:
                template_data["success"].append(
                    f"{len(add_team_members[team])} Nutzer:innen zum Team {team} hinzugefügt."
                )
                logger.info(
                    f"{len(add_team_members[team])} Nutzer:innen zum Team {team} hinzugefügt."
                )
            else:
                if "error" not in ret:
                    ret["error"] = "Unbekannter Fehler"
                template_data["warning"].append(
                    f"Konnte nicht alle {len(add_team_members[team])} Nutzer:innen NICHT zum Team {team} hinzufügen: {ret['error']}"
                )
                logger.error(
                    f"Konnte nicht alle {len(add_team_members[team])} Nutzer:innen NICHT zum Team {team} hinzufügen: {ret['error']}"
                )


def tenant_admin_get_actions(rocket, rc_users, template_data):
    actions = []
    ## A) Check if all users have been added to the corresponding team in RC.
    rc_teams = {}
    for building in Building.objects.filter(active=True).exclude(team=""):
        # pprint(rocket.me().json())
        # teams = rocket.contrib_list_all_teams().json()
        # pprint(teams)
        ret = rocket.contrib_get_team_members(team_name=building.team, count=0).json()
        # pprint(ret)
        if not ret["success"]:
            if "error" in ret:
                template_data["error"] = "Can't get team members for team %s: %s" % (
                    building.team,
                    ret["error"],
                )
            else:
                template_data["error"] = "Can't get team members for team: %s: Unknown error" % (
                    building.team
                )
            return None
        rc_teams[building.team] = {}
        for member in ret["members"]:
            # pprint(member)
            # break
            # template_data['log'].append("Found user: %s" % member['user']['username'])
            rc_teams[building.team][member["user"]["username"]] = member[
                "user"
            ]  ## _id, name, username

        template_data["log"].append(
            "=== CHECKING team %s (%d members) ===" % (building.team, len(rc_teams[building.team]))
        )

        for tenant in Tenant.objects.filter(building=building, active=True):
            if tenant.name.user:
                if tenant.name.user.username not in rc_teams[building.team]:
                    if (
                        tenant.name.user.username in rc_users
                        and rc_users[tenant.name.user.username]["active"]
                    ):
                        template_data["log"].append(
                            "Tenant %s is NOT member of team %s (%s)"
                            % (tenant, building.team, tenant.name.user.username)
                        )
                        actions.append(
                            {
                                "formfield_name": "addtoteam_%s" % tenant.id,
                                "formfield_label": "%s zu Team %s hinzufügen"
                                % (tenant, building.team),
                            }
                        )
                    # else:
                    #    template_data['log'].append("Tenant %s has no (active) Rocket.Chat user yet (%s)" % (tenant, tenant.name.user.username))
                # else:
                #    template_data['log'].append("Tenant %s is member of team (%s)" % (tenant, tenant.name.user.username))
            # else:
            #    template_data['log'].append("Tenant %s has no user yet." % tenant)

    ## B) Check if users in RC need to be deactivated or re-activated.
    template_data["log"].append("=== CHECKING for re-/deactivated tenants ===")
    for tenant in Tenant.objects.all():
        if tenant.name.user and tenant.name.user.username in rc_users:
            if not tenant.active and rc_users[tenant.name.user.username]["active"]:
                template_data["log"].append(
                    f"Deactivated tenant {tenant} is not deactivated in chat."
                )
                actions.append(
                    {
                        "formfield_name": f"deactivate_{tenant.id}",
                        "formfield_label": f"{tenant} im Chat deaktivieren.",
                    }
                )
            elif tenant.active and not rc_users[tenant.name.user.username]["active"]:
                template_data["log"].append(f"Activated tenant {tenant} is deactivated in chat.")
                actions.append(
                    {
                        "formfield_name": f"activate_{tenant.id}",
                        "formfield_label": f"{tenant} im Chat re-aktivieren.",
                    }
                )

    return actions


@login_required
def tenant_admin_maintenance(request):
    template_data = template_from_portal_site(request)
    if request.user.is_anonymous:
        logger.error(
            "%s - tenant_admin_edit(): no anonymous access" % (request.META["REMOTE_ADDR"])
        )
        return home(request, message="FEHLER: Unerlaubter Zugriff.")
    try:
        TenantAdmin.objects.get(name__user=request.user)
    except TenantAdmin.DoesNotExist:
        logger.error(
            "%s - tenant_admin_edit(): no tenant admin found for user %s"
            % (request.META["REMOTE_ADDR"], request.user.username)
        )
        return home(request, message="FEHLER: Keine Berechtigung für diese Aktion.")

    template_data["log"] = []

    rc_login = settings.ROCKETCHAT_API[settings.PORTAL_SECONDARY_NAME]
    rocket = RocketChatContrib(rc_login["user"], rc_login["pass"], server_url=rc_login["url"])

    ## Get all RC users
    rc_users = tenant_admin_get_rc_users(rocket, template_data)
    if not rc_users:
        return render(request, "portal/tenant_maintenance.html", template_data)

    ## Perform actions that were selected in the form
    template_data["success"] = []
    template_data["warning"] = []
    if request.method == "POST":
        action_list = []
        for key, value in request.POST.items():
            if not value or key in ("csrfmiddlewaretoken", "commit"):
                ## Skip actions that were not selected
                continue
            action_list.append(key)
        tenant_admin_perform_actions(action_list, rocket, rc_users, template_data)

    ## Build form with pending actions
    actions = tenant_admin_get_actions(rocket, rc_users, template_data)
    if not actions:
        return render(request, "portal/tenant_maintenance.html", template_data)
    formfields = {}
    for action in actions:
        formfields[action["formfield_name"]] = forms.BooleanField(
            label=action["formfield_label"], required=False, initial=True
        )
    if len(formfields):
        formclass = type("TenantMaintenanceForm", (forms.Form,), formfields)
        template_data["form"] = formclass(request.POST or None)
        template_data["submit_button_text"] = "Ausführen"

    return render(request, "portal/tenant_maintenance.html", template_data)


def cron_maintenance(request):
    template_data = {"log": [], "success": [], "warning": [], "error": None}

    ## Rocket Chat: Get users, get and perform pending actions.
    rc_login = settings.ROCKETCHAT_API[settings.PORTAL_SECONDARY_NAME]
    rocket = RocketChatContrib(rc_login["user"], rc_login["pass"], server_url=rc_login["url"])

    rc_users = tenant_admin_get_rc_users(rocket, template_data)
    if rc_users is None:
        return JsonResponse(
            {"status": "ERROR", "error": template_data["error"], "log": template_data["log"]}
        )

    actions = tenant_admin_get_actions(rocket, rc_users, template_data)
    if actions is None:
        return JsonResponse(
            {"status": "ERROR", "error": template_data["error"], "log": template_data["log"]}
        )

    tenant_admin_perform_actions(
        [a["formfield_name"] for a in actions], rocket, rc_users, template_data
    )

    return JsonResponse(
        {
            "status": "OK",
            "success": template_data["success"],
            "warning": template_data["warning"],
            "log": template_data["log"],
        }
    )


@csrf_exempt
def rocket_chat_webhook(request, webhook_name=None):
    ## Check and get request data
    # pprint(request.META)
    # pprint(list(request.GET.items()))
    # pprint(list(request.POST.items()))
    # pprint(request.headers)
    if request.method != "POST":
        logger.error("No POST request.")
        return HttpResponseBadRequest("No POST request.")
    try:
        data = json.loads(request.body)
        # pprint(data)
    except:
        logger.error("Can't load JSON data: %s" % request.body)
        send_error_mail(
            "rocket.chat webhook - invalid json", "Can't load JSON data: %s" % request.body
        )
        return HttpResponseBadRequest("Can't load JSON data.")

    if "token" not in data or data["token"] != settings.ROCKETCHAT_WEBHOOK_TOKEN:
        logger.error("No valid token: %s" % data)
        send_error_mail("rocket.chat webhook - no valid token", "No valid token: %s" % data)
        return HttpResponseBadRequest("No valid token.")

    if webhook_name == "test":
        return rocket_chat_process_test(data)
    elif webhook_name == "new_user":
        return rocket_chat_process_new_user(data)
    elif webhook_name.startswith("autorespond"):
        return rocket_chat_process_autorespond(data, webhook_name)
    else:
        logger.error("Invalid webhook_name: %s" % webhook_name)
        send_error_mail(
            "rocket.chat webhook - invalid webhook_name", "Invalid webhook_name: %s" % webhook_name
        )
        return HttpResponseBadRequest("Invalid webhook name.")


def rocket_chat_process_test(data):
    send_info_mail("rocket.chat webhook - test", "Received data: %s" % str(data))
    return JsonResponse({"status": "NOACTION", "reason": "test"})


def rocket_chat_process_autorespond(data, webhook_name):
    # Example data:
    # {
    #  "token": "xzyegbnqlf",
    #  "bot": false,
    #  "channel_id": "uGHu6eoEaRg8GDqWrzXtwcpsfXGjY8FxJr",
    #  "message_id": "I677PU7eI9kZmfgtp",
    #  "timestamp": "2024-06-05T10:46:21.165Z",
    #  "user_id": "XyzwcpsfXGjY8FxJr",
    #  "user_name": "test",
    #  "text": "Test1",
    #  "siteUrl": "https://chat.example.com"
    # }
    if webhook_name in getattr(settings, "ROCKETCHAT_WEBHOOK_AUTORESPONDER", {}):
        logger.info(f"Sent {webhook_name} to {data['user_name']} on {data['siteUrl']}")
        send_info_mail(
            "rocket.chat webhook - autoresponder",
            f"Sent {webhook_name} to {data['user_name']} on {data['siteUrl']}. Message was: {data['text']}",
        )
        return JsonResponse(
            {"text": settings.ROCKETCHAT_WEBHOOK_AUTORESPONDER[webhook_name]["text"]}
        )
    else:
        logger.warning(
            f"No autorespond message configured for {webhook_name}. Not sending a response to {data['user_name']} on {data['siteUrl']}."
        )
        send_error_mail(
            "rocket.chat webhook - autoresponder",
            f"No autorespond message configured for {webhook_name}. Not sending a response to {data['user_name']} on {data['siteUrl']}. Message was: {data['text']}",
        )
        return JsonResponse(
            {"status": "NOACTION", "reason": "No autoresponder message configured."}
        )


def rocket_chat_process_new_user(data):
    # Example request:
    # {
    #  "token": "xzy97jlct5",
    #  "bot": false,
    #  "timestamp": "2023-09-19T14:44:00.436Z",
    #  "user_id": "zyxWponBQPNR7jpkM",
    #  "user_name": "test",
    #  "user": {
    #    "_id": "zyxWponBQPNR7jpkM",
    #    "createdAt": "2023-09-19T14:44:00.436Z",
    #    "services": {
    #      "portal": {
    #        "_OAuthCustom": true,
    #        "serverURL": "https://portal.example.com/",
    #        "accessToken": "RVzJgXRpxiHY8cTifCIFSPveMC37lA",
    #        "expiresAt": 1695170635204,
    #        "refreshToken": "ROaTJzNGMonDJAJK2KFA5kn3qNKyir",
    #        "id": "Portal_260",
    #        "username": "test",
    #        "email": "test@example.com",
    #        "name": "Test User"
    #      }
    #    },
    #    "type": "user",
    #    "status": "offline",
    #    "active": true,
    #    "name": "Test User",
    #    "emails": [
    #      {
    #        "address": "test@example.com",
    #        "verified": true
    #      }
    #    ],
    #    "username": "test",
    #    "email": "test@example.com",
    #    "_updatedAt": "2023-09-19T14:44:00.438Z"
    #  }
    if "user_id" not in data:
        ## Workaround because of https://github.com/RocketChat/Rocket.Chat/issues/36348
        json_resp = cron_maintenance(None)
        resp = json_resp.content.decode()
        logger.warning(
            f"No user_id in JSON data: {data}. "
            f"Called cron_maintenance as workaround. Result: {resp}"
        )
        # logger.error("No user_id in JSON data: %s" % data)
        send_error_mail(
            "rocket.chat webhook - no user_id",
            f"No user_id in JSON data: {data}\n"
            f"Called cron_maintenance as workaround. Result: {resp}",
        )
        return json_resp
        # return HttpResponseBadRequest("No user_id in request.")

    ## Get username or email or id
    if "user_name" in data:
        user_name = data["user_name"]
    elif "user" in data and "email" in data["user"]:
        user_name = data["user"]["email"]
    else:
        user_name = data["user_id"]

    ## Get team name for new user
    user = UserModel.objects.filter(username=user_name).first()
    if not user:
        logger.info("New user is not in DB: %s" % user_name)
        send_info_mail(
            "rocket.chat webhook - new user not in DB", "New user is not in DB: %s" % user_name
        )
        return JsonResponse(
            {"status": "NOACTION", "reason": "User %s not in database." % user_name}
        )
    tenant = Tenant.objects.filter(name__user=user).first()
    if not tenant:
        logger.info("New user is not tenant: %s" % user_name)
        send_info_mail(
            "rocket.chat webhook - new user not tenant", "New user is not tenant: %s" % user_name
        )
        return JsonResponse({"status": "NOACTION", "reason": "User %s is not tenant." % user_name})
    if not tenant.building.team:
        logger.info("New user has no team: %s" % user_name)
        send_info_mail(
            "rocket.chat webhook - new user without team", "New user has no team: %s" % user_name
        )
        return JsonResponse(
            {"status": "NOACTION", "reason": "New user %s has no team." % user_name}
        )

    ## Take action (TODO: Check if member of team -> get Team id)
    ## Add user to team through rocket.chat API
    team_name = tenant.building.team
    try:
        rc_login = settings.ROCKETCHAT_API[settings.PORTAL_SECONDARY_NAME]
        rocket = RocketChatContrib(rc_login["user"], rc_login["pass"], server_url=rc_login["url"])
        # pprint(rocket.me().json())
        # teams = rocket.contrib_list_all_teams().json()
        # pprint(teams)
        ret = rocket.contrib_add_team_members(
            team_name=team_name, members=[{"userId": data["user_id"], "roles": ["member"]}]
        ).json()
        # pprint(ret)
        if not ret["success"]:
            if "error" in ret:
                error_str = ret["error"]
            else:
                error_str = "Unknown error"
            logger.error(
                "Could not add user %s (id %s) to team %s: %s"
                % (user_name, data["user_id"], team_name, error_str)
            )
            send_error_mail(
                "rocket.chat webhook - could not add new user to team!",
                "Could not add user %s (id %s) to team %s: %s"
                % (user_name, data["user_id"], team_name, error_str),
            )
            return JsonResponse({"status": "ERROR", "reason": "Could not add user to team."})
    except:
        logger.error(
            "Could not add user %s (id %s) to team %s: %s"
            % (user_name, data["user_id"], team_name, "Error while accessing rocket.chat API.")
        )
        send_error_mail(
            "rocket.chat webhook - could not add new user to team!",
            "Could not add user %s (id %s) to team %s: %s"
            % (user_name, data["user_id"], team_name, "Error while accessing rocket.chat API."),
        )
        return HttpResponseNotFound("Error while accessing rocket.chat API.")

    logger.info("Added user %s (id %s) to team %s." % (user_name, data["user_id"], team_name))
    send_info_mail(
        "rocket.chat webhook - new user added to team",
        "Added user %s (id %s) to team %s." % (user_name, data["user_id"], team_name),
    )
    return JsonResponse({"status": "OK"})
