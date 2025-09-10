import logging

from django.conf import settings
from django.http import HttpResponseForbidden
from oauth2_provider.models import get_application_model
from oauth2_provider.views import AuthorizationView

from geno.models import Address
from geno.utils import is_member, is_renting

Application = get_application_model()
logger = logging.getLogger("access_portal")


def check_address_user_auth():
    unauth_addr = []
    for adr in Address.objects.all():
        if adr.user:
            auth_info = authorize(adr.user)
            if not auth_info["user_id"]:
                auth_info = authorize(adr.user, host=settings.PORTAL_SECONDARY_HOST)
            if not auth_info["user_id"]:
                unauth_addr.append(
                    "Address with unauthorized user: %s [%s]" % (adr, adr.user.username)
                )
    return unauth_addr


def get_oauth_profile(request):
    try:
        # django.http.Request
        user = request.resource_owner
        host = request.get_host()
        remote_addr = request.META["REMOTE_ADDR"]
    except AttributeError:
        # OCID request is oauthlib.common.Request
        user = request.user
        host = request.headers.get("HOST", "")
        remote_addr = request.headers.get("REMOTE_ADDR", "")
    if user.is_authenticated:
        auth_info = authorize(user, host)
        if not auth_info["user_id"]:
            logger.warning(
                "%s - %s get_oauth_profile(): DENIED: %s"
                % (remote_addr, host, auth_info["reason"])
            )
            return None

        if settings.DEBUG:
            auth_info["user_id"] = "%s_test" % (auth_info["user_id"])
        logger.info(
            "%s - %s get_oauth_profile(): send identity user_id=%s, username=%s, email=%s, name=%s"
            % (
                remote_addr,
                host,
                auth_info["user_id"],
                user.username,
                user.email,
                auth_info["name"],
            )
        )
        return {
            "id": auth_info["user_id"],
            "username": user.username,
            "email": user.email,
            "name": auth_info["name"],
            "given_name": auth_info["given_name"],
            "family_name": auth_info["family_name"],
        }
    else:
        logger.error(
            "%s - %s get_oauth_profile(): DENIED: not authenticated u=%s"
            % (remote_addr, host, user.username)
        )
        return None


def authorize(user, host=None):
    if user.username in getattr(settings, "PORTAL_BANNED_USERS", []):
        return {"user_id": None, "reason": "banned user %s" % user.username}

    if not hasattr(user, "address"):
        return {"user_id": None, "reason": "user %s has no address" % user.username}

    return authorize_address(user.address, user.id, host=host)


def authorize_address(address, uid, host=None):
    name = "%s %s" % (address.first_name, address.name)
    if host == settings.PORTAL_SECONDARY_HOST:
        ## Secondary portal: User must have active address and active tenant or tenant-admin.
        if hasattr(address, "address_tenant") or hasattr(address, "address_tenantadmin"):
            user_id = "%s_%s" % (settings.PORTAL_SECONDARY_NAME, uid)
            active_tenant = hasattr(address, "address_tenant") and address.address_tenant.active
            active_tenantadmin = (
                hasattr(address, "address_tenantadmin") and address.address_tenantadmin.active
            )
            if not address.active or not (active_tenant or active_tenantadmin):
                return {"user_id": None, "reason": "inactive address or tenant %s" % address}
        else:
            return {"user_id": None, "reason": "%s is not tenant" % address}
    else:
        ## Main portal: User must have active address and must be a member or have an active contract.
        user_id = "%s_%s" % (settings.GENO_ID, uid)
        if not address.active:
            return {"user_id": None, "reason": "inactive address %s" % address}
        if not address.login_permission and not is_member(address) and not is_renting(address):
            return {"user_id": None, "reason": "non-member/non-renter %s" % address}
    ## Grant access
    return {
        "user_id": user_id,
        "name": name,
        "given_name": address.first_name,
        "family_name": address.name,
    }


class CohivaAuthorizationView(AuthorizationView):
    def dispatch(self, request, *args, **kwargs):
        # Fetch the OAuth2 Application
        client_id = request.GET.get("client_id")
        try:
            app = Application.objects.get(client_id=client_id)
        except Application.DoesNotExist:
            return HttpResponseForbidden("Invalid client")

        # Example: deny specific users access to a specific app
        # denied_users = ["blocked@example.com", "user2@example.com"]
        #
        # if user.email in denied_users and app.name == "My PWA":
        #    return HttpResponseForbidden("Access denied for this application.")

        if not get_oauth_profile(request):
            return HttpResponseForbidden(f"Access denied for {app.name}.")

        return super().dispatch(request, *args, **kwargs)
