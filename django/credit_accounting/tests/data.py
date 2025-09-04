from credit_accounting.models import Account, Vendor, VendorAdmin
from geno.models import Address


def create_vendors(cls):
    cls.vendors = []
    cls.vendors.append(
        Vendor.objects.create(
            name="Vendor1",
            api_secret="secret1111",
            qr_name="Vendor1-Name",
            qr_line1="Vendor1-Address",
            qr_line2="Vendor1-City",
            qr_iban="CH6431961000004421557",
        )
    )
    cls.vendors.append(Vendor.objects.create(name="Vendor2", api_secret="secret2222"))


def create_vendoradmins(cls):
    adr = Address.objects.create(name="Vendor1Admin", user=cls.su)
    cls.vendoradmins = []
    cls.vendoradmins.append(VendorAdmin.objects.create(name=adr, vendor=cls.vendors[0]))


def create_accounts(cls):
    create_vendors(cls)
    create_vendoradmins(cls)

    cls.credit_accounts = []
    cls.credit_accounts.append(
        Account.objects.create(name="V1_Acc1", pin="101", vendor=cls.vendors[0])
    )
    cls.credit_accounts.append(
        Account.objects.create(name="V1_Acc2", pin="102", vendor=cls.vendors[0])
    )
    cls.credit_accounts.append(
        Account.objects.create(name="V1_Acc3", pin="103", vendor=cls.vendors[0])
    )
    cls.credit_accounts.append(
        Account.objects.create(name="V2_Acc1", pin="201", vendor=cls.vendors[1])
    )
    cls.credit_accounts.append(
        Account.objects.create(name="V2_Acc2", pin="202", vendor=cls.vendors[1])
    )
