import logging

from django.conf import settings
from django.http import HttpResponseForbidden
from oauth2_provider.models import get_application_model
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.views import AuthorizationView

from geno.models import Address
from geno.utils import is_member, is_renting
from portal.models import (
    OAuthAppNoPermissionsConfigured,
    OAuthAppPermissionDenied,
    OAuthAppSettings,
)

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


def get_oauth_profile(request, app: type[Application] | None = None):
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
        auth_info = authorize(user, host, app)
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


def authorize(user, host=None, app=None):
    if user.username in getattr(settings, "PORTAL_BANNED_USERS", []):
        return {"user_id": None, "reason": "banned user %s" % user.username}

    if not hasattr(user, "address"):
        return {"user_id": None, "reason": "user %s has no address" % user.username}

    return authorize_address(user.address, user.id, host=host, app=app)


def authorize_address(address, uid, host=None, app=None):
    name = "%s %s" % (address.first_name, address.name)
    if host == settings.PORTAL_SECONDARY_HOST:
        ## Secondary portal
        # - User must have an active address and be an active tenant or tenant-admin.
        # - OAuth app authorization is not allowed.
        if app:
            return {
                "user_id": None,
                "reason": "OAuth logins are not allowed on the secondary portal.",
            }
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
        ## Main portal
        # - User must have an active address.
        # - OAuth app authorization is done with permission settings (or with legacy rules
        #   that the user must be a member, have an active contract or special login permission
        #   if no permission rules are present).
        user_id = "%s_%s" % (settings.GENO_ID, uid)
        if not address.active:
            return {"user_id": None, "reason": "inactive address %s" % address}
        if app:
            try:
                OAuthAppSettings.objects.get(application=app).authorize(address.user)
            except (OAuthAppSettings.DoesNotExist, OAuthAppNoPermissionsConfigured):
                ## Use legacy rules
                if (
                    not address.login_permission
                    and not is_member(address)
                    and not is_renting(address)
                ):
                    return {"user_id": None, "reason": "non-member/non-renter %s" % address}
            except OAuthAppPermissionDenied:
                return {
                    "user_id": None,
                    "reason": f"Access to {app.name} is not allowed for {address}",
                }
        else:
            if not address.login_permission and not is_member(address) and not is_renting(address):
                if hasattr(address, "address_tenant") and address.address_tenant:
                    ## Tenants should use the secondary portal
                    return {"user_id": None, "reason": "Redirect to secondary portal."}
                logger.info(f"Granting access to portal for non-member/non-renter {address}")
    ## Grant access
    return {
        "user_id": user_id,
        "name": name,
        "given_name": address.first_name,
        "family_name": address.name,
    }


class CohivaAuthorizationView(AuthorizationView):
    def get(self, request, *args, **kwargs):
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

        prompt = request.GET.get("prompt")
        if prompt != "login" and not get_oauth_profile(request, app):
            return HttpResponseForbidden(f"Access denied for {app.name}.")

        return super().get(request, *args, **kwargs)


class CohivaOAuth2Validator(OAuth2Validator):
    # Set `oidc_claim_scope = None` to ignore scopes that limit which claims to return,
    # otherwise the OIDC standard scopes are used.

    def get_claim_dict(self, request):
        profile = get_oauth_profile(request, app=request.client)
        if not profile:
            # Unauthorized
            return {}
        claims = super().get_claim_dict(request)
        claims["sub"] = profile["id"]
        claims.update(
            {
                "given_name": profile["given_name"],
                "family_name": profile["family_name"],
                "name": profile["name"],
                "preferred_username": profile["username"],
                "email": profile["email"],
            }
        )
        return claims

    def get_discovery_claims(self, request):
        return ["sub", "given_name", "family_name", "name", "preferred_username", "email"]
