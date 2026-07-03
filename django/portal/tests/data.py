import datetime

from oauth2_provider.models import get_application_model

from geno.models import Address, Building, Member, Tenant
from geno.tests.base import GenoAdminTestCase
from portal.models import OAuthAppPermissionRule, OAuthAppSettings, TenantAdmin

Application = get_application_model()


def create_tenantbuildings(cls):
    cls.tenantbuildings = []
    cls.tenantbuildings.append(Building.objects.create(name="TenantBuilding1"))
    cls.tenantbuildings.append(Building.objects.create(name="TenantBuilding2"))


def create_tenantadmins(cls):
    cls.tenantadmins = []
    usr = cls.UserModel.objects.create_user(
        username="tenantadmin1", password="secret", email="tenantadmin1@example.com"
    )
    adr = Address.objects.create(name="Tenantadmin1", user=usr, email="tenantadmin1@example.com")
    Member.objects.create(name=adr, date_join=datetime.date(1900, 1, 1))
    ta = TenantAdmin.objects.create(name=adr)
    ta.buildings.set(
        [
            cls.tenantbuildings[0],
        ]
    )
    ta.save()
    cls.tenantadmins.append(ta)


def create_tenants(cls):
    create_tenantbuildings(cls)
    create_tenantadmins(cls)

    cls.tenants = []
    adr = Address.objects.create(name="Tenant1", email="tenant1@example.com")
    cls.tenants.append(Tenant.objects.create(name=adr, building=cls.tenantbuildings[0]))
    adr = Address.objects.create(name="Tenant2", email="tenant2@example.com")
    cls.tenants.append(Tenant.objects.create(name=adr, building=cls.tenantbuildings[0]))


def create_oauth_apps(cls: type[GenoAdminTestCase]):
    cls.oauth_apps = {
        "nosettings": Application.objects.create(name="NoSettings"),
        "norules": Application.objects.create(name="NoSettings"),
        "allow_all": Application.objects.create(name="AllowAll"),
        "admin_group_only": Application.objects.create(name="AdminGroup"),
        "renters_only": Application.objects.create(name="RentersOnly"),
        "renter_or_tenant": Application.objects.create(name="RenterOrTenant"),
        "member_or_admin": Application.objects.create(name="MemberOrAdmin"),
        "member_and_admin": Application.objects.create(name="MemberAndAdmin"),
        "member_not_tenant": Application.objects.create(name="MemberNotTenant"),
        "all_but_admins": Application.objects.create(name="AllButAdmins"),
    }
    for key, app in cls.oauth_apps.items():
        if key not in ("nosettings",):
            OAuthAppSettings.objects.create(application=app)

    # Allow all
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["allow_all"].oauthappsettings, order=10, action="allow"
    )

    # Admin group only
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["admin_group_only"].oauthappsettings,
        order=10,
        action="allow",
        group=cls.admin_group,
    )

    # Renters only
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["renters_only"].oauthappsettings,
        order=10,
        action="allow",
        role="renter",
    )

    # Renter or Tenant
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["renter_or_tenant"].oauthappsettings,
        order=10,
        action="allow",
        role="renter",
    )
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["renter_or_tenant"].oauthappsettings,
        order=20,
        action="allow",
        role="community",  # The role for tenants is "community" in the current implementation!
    )

    # Member OR Admin
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["member_or_admin"].oauthappsettings,
        order=10,
        action="allow",
        role="member",
        group=cls.admin_group,
        role_or_group_must_match=True,
    )

    # Member AND Admin
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["member_and_admin"].oauthappsettings,
        order=10,
        action="allow",
        role="member",
        group=cls.admin_group,
    )

    # Member/Renter AND NOT Tenant
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["member_not_tenant"].oauthappsettings,
        order=10,
        action="deny",
        role="community",  # community includes tenants and renters
    )
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["member_not_tenant"].oauthappsettings,
        order=20,
        action="allow",
        role="member",
    )

    # All but Admins
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["all_but_admins"].oauthappsettings,
        order=10,
        action="deny",
        group=cls.admin_group,
    )
    OAuthAppPermissionRule.objects.create(
        application_settings=cls.oauth_apps["all_but_admins"].oauthappsettings,
        order=20,
        action="allow",
    )
