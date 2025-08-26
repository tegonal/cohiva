from django.conf import settings

from geno.models import Address
from geno.utils import is_member, is_renting


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
    return {"user_id": user_id, "name": name}
