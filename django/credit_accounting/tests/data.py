from credit_accounting.models import Account, AccountOwner, Vendor, VendorAdmin
from geno.models import Address


def create_vendors(cls):
    vendor_address = Address.objects.create(
        organization="Vendor1-Name",
        street_name="Vendor-Street",
        house_number="8",
        city_zipcode="9999",
        city_name="Vendor-City",
    )
    cls.vendors = []
    cls.vendors.append(
        Vendor.objects.create(
            name="Vendor1",
            api_secret="secret1111",
            qr_address=vendor_address,
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

    ## Account owners
    cls.account_owner_address = Address.objects.create(
        organization="Owner1-Name",
        street_name="Owner-Street",
        house_number="8",
        city_zipcode="9999",
        city_name="Owner-City",
    )
    AccountOwner.objects.create(
        name=cls.credit_accounts[1], owner_object=cls.account_owner_address
    )
