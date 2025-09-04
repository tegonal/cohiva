import datetime

from geno.models import Address, Building, Member, Tenant
from portal.models import TenantAdmin


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
