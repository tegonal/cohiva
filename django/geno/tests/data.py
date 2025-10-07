import datetime

from django.contrib.auth.models import User

# from dateutil.relativedelta import relativedelta
from django.utils import timezone

## django-filer stuff
from geno.models import (
    Address,
    Building,
    Child,
    ContentTemplate,
    ContentTemplateOption,
    ContentTemplateOptionType,
    Contract,
    DocumentType,
    InvoiceCategory,
    Member,
    RegistrationEvent,
    RegistrationSlot,
    RentalUnit,
    Share,
    ShareType,
    Tenant,
)


def create_users(cls):
    cls.su = User.objects.create_superuser(
        username="superuser", password="secret", email="admin@example.com"
    )


def create_prototype_users(cls):
    ## Prototype users for different roles
    cls.prototypes = {
        "external": {},
        "tenant": {},
        "member": {},
        "renter": {},
        "renter_nonmember": {},
        "inactive": {},
    }
    for p, proto in cls.prototypes.items():
        proto["user"] = cls.UserModel.objects.create_user(
            username=f"user.{p}", password="secret", email=f"{p}@example.com"
        )
        proto["address"] = Address.objects.create(
            name=p, first_name=f"{p}_first", user=proto["user"], email=f"{p}@example.com"
        )

    ## Make tenant
    building = Building.objects.create(name="Test")
    Tenant.objects.create(name=cls.prototypes["tenant"]["address"], building=building)

    ## Make members
    for role in ("member", "renter"):
        Member.objects.create(
            name=cls.prototypes[role]["address"], date_join=datetime.date(2000, 1, 1)
        )

    ## Make renters
    renter_addresses = list(
        item["address"] for key, item in cls.prototypes.items() if key.startswith("renter")
    )
    ru = RentalUnit.objects.create(
        name="Test",
        rental_type="Wohnung",
        building=building,
        area=100,
        height=3,
        volume=300,
        rooms=4,
        min_occupancy=3,
        nk=100,
        rent_netto=1000,
        share=10000,
    )
    contract = Contract.objects.create(
        comment="Test", state="unterzeichnet", date=datetime.date(2000, 1, 1)
    )
    contract.rental_units.set([ru])
    contract.contractors.set(renter_addresses)
    contract.save()

    cls.prototypes["renter"]["rental_unit"] = ru
    cls.prototypes["renter"]["contract"] = contract

    ## Make inactive
    cls.prototypes["inactive"]["address"].active = False
    cls.prototypes["inactive"]["address"].save()


def create_templates(cls):
    create_templateoptions(cls)
    o = cls.contenttemplateoptions

    cls.contenttemplates = []
    template_file = cls.addFilerFile(
        "geno/tests/template_test.odt", filename="TestTemplate_Document.odt"
    )

    ct = ContentTemplate.objects.create(
        name="All Options", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(sum(o.values(), []))
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="Simple", template_type="OpenDocument", file=template_file
    )
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="Statement", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(o["statement"])
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="Bill", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(o["billing"] + o["bill-default"])
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="Member Bill", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(o["billing"] + o["bill-member"])
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="QR-Bill", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(o["billing"] + o["bill-default"] + o["iban"] + o["qr-info"])
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="QR-Bill Noamount", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(o["billing"] + o["iban"])
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="QR-Bill Ref", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(
        o["billing"] + o["bill-default"] + o["qr-iban"] + o["qr-info"] + o["qr-info-rental"]
    )
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="QR-Bill Ref Contract", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(
        o["billing"]
        + o["bill-default"]
        + o["qr-iban-contract"]
        + o["qr-info"]
        + o["qr-info-rental"]
    )
    ct.save()
    cls.contenttemplates.append(ct)

    ct = ContentTemplate.objects.create(
        name="QR-Bill Ref Contract Noamount", template_type="OpenDocument", file=template_file
    )
    ct.template_context.set(o["billing"] + o["qr-iban-contract"] + o["qr-info-rental"])
    ct.save()
    cls.contenttemplates.append(ct)

    template_file = cls.addFilerFile("cohiva/tests/B1.pdf", filename="TestPDF_B1.pdf")
    ct = ContentTemplate.objects.create(name="Test PDF1", template_type="File", file=template_file)
    cls.contenttemplates.append(ct)

    template_file = cls.addFilerFile("cohiva/tests/C1.pdf", filename="TestPDF_C1.pdf")
    ct = ContentTemplate.objects.create(name="Test PDF2", template_type="File", file=template_file)
    cls.contenttemplates.append(ct)

    cls.email_templates = [
        ContentTemplate.objects.create(
            name="Email-Text",
            template_type="Email",
            text="{{anrede}}\n\nDies ist ein Test für {{dich}}.",
        ),
        ContentTemplate.objects.create(
            name="Email-HTML-Rechnung",
            template_type="Email",
            text="<html><body><p>{{anrede}}</p><p>Anbei die Rechnung.</p></body></html>",
        ),
    ]


def create_templateoptions(cls):
    cls.contenttemplateoptions = {
        "statement": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="share_statement_context")
            )
        ],
        "billing": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="billing_context")
            )
        ],
        "iban": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_account"),
                value="CH5604835012345678009",
            )
        ],
        "qr-iban": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_account"),
                value="CH6431961000004421557",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_invoice_type_id"),
                value="77",
            ),
        ],
        "qr-iban-contract": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_account"),
                value="CH6431961000004421557",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_invoice_type_id"),
                value="12",
            ),
        ],
        "qr-info": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_info"),
                value="QR-Infotext {{jahr}}",
            )
        ],
        "qr-info-rental": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="qrbill_rental_unit_in_extra_info")
            )
        ],
        "bill-default": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_text_default"),
                value="Standard-Rechnungstext",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_amount_default"),
                value="9.95",
            ),
        ],
        "bill-member": [
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="share_count_context_var"),
                value="share_count",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="share_count_sharetype"),
                value="Anteilschein freiwillig",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_text_memberflag_01"),
                value="Rechnung-Flag01",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_amount_memberflag_01"),
                value="10.00",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_text_memberflag_02"),
                value="Rechnung-Flag02",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_amount_memberflag_02"),
                value="20.00",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_text_memberflag_03"),
                value="Rechnung-Flag03",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_amount_memberflag_03"),
                value="30.00",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_text_memberflag_04"),
                value="Rechnung-Flag04",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_amount_memberflag_04"),
                value="40.00",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_text_memberflag_05"),
                value="Rechnung-Flag05",
            ),
            ContentTemplateOption.objects.create(
                name=ContentTemplateOptionType.objects.get(name="bill_amount_memberflag_05"),
                value="50.00",
            ),
        ],
    }


def create_documenttypes(cls):
    cls.documenttypes = [
        DocumentType.objects.create(
            name="invoice", description="QR-Rechnung", template=cls.contenttemplates[0]
        ),
    ]


def create_invoicecategories(cls):
    cls.invoicecategories = [
        InvoiceCategory.objects.create(name="Member Invoice", reference_id=77),
        InvoiceCategory.objects.create(
            name="Mietzins wiederkehrend",
            reference_id=10,
            linked_object_type="Contract",
            email_template=cls.email_templates[1],
        ),
        InvoiceCategory.objects.create(
            name="Nebenkostenabrechnung", reference_id=12, linked_object_type="Contract"
        ),
        InvoiceCategory.objects.create(
            name="Nebenkosten Akonto ausserordentlich",
            reference_id=13,
            linked_object_type="Contract",
        ),
    ]


def create_members(cls):
    create_addresses(cls)
    cls.members = []
    cls.members.append(
        Member.objects.create(
            name=cls.addresses[0], flag_01=True, date_join=datetime.date(2001, 1, 15)
        )
    )
    cls.members.append(
        Member.objects.create(
            name=cls.addresses[1], flag_02=True, date_join=datetime.date(2002, 1, 15)
        )
    )
    cls.members.append(
        Member.objects.create(
            name=cls.addresses[2], flag_03=True, date_join=datetime.date(2003, 1, 15)
        )
    )
    cls.members.append(
        Member.objects.create(
            name=cls.addresses[3], flag_04=True, date_join=datetime.date(2004, 1, 15)
        )
    )
    cls.members.append(
        Member.objects.create(
            name=cls.addresses[4], flag_05=True, date_join=datetime.date(2005, 1, 15)
        )
    )
    cls.members.append(
        Member.objects.create(
            name=cls.addresses[5], flag_05=True, date_join=datetime.date(2006, 1, 15)
        )
    )


def create_addresses(cls):
    cls.addresses = []
    cls.addresses.append(
        Address.objects.create(
            name="Muster",
            first_name="Hans",
            email="hans.muster@example.com",
            title="Herr",
            formal="Sie",
            street_name="Beispielweg",
            house_number="1",
            city_zipcode="3000",
            city_name="Bern",
        )
    )
    cls.addresses.append(
        Address.objects.create(
            name="Muster",
            first_name="Anna",
            email="anna.muster@example.com",
            title="Frau",
            formal="Du",
            street_name="Beispielweg",
            house_number="1",
            city_zipcode="3000",
            city_name="Bern",
        )
    )
    cls.addresses.append(
        Address.objects.create(
            organization="WBG Test",
            email="wbgtest@example.com",
            title="Org",
            formal="Du",
            street_name="Beispielweg",
            house_number="1",
            city_zipcode="3000",
            city_name="Bern",
        )
    )
    cls.addresses.append(
        Address.objects.create(
            organization="WBG Test",
            name="Bitterer",
            first_name="Ernst",
            email="ernst@example.com",
            title="Herr",
            formal="Du",
            street_name="Beispielweg",
            house_number="1",
            city_zipcode="3000",
            city_name="Bern",
        )
    )
    cls.addresses.append(Address.objects.create(name="Noaddress", first_name="Harry"))
    cls.addresses.append(
        Address.objects.create(name="Dontuseme", first_name="Sally", title="Frau")
    )


def create_children(cls):
    cls.children = []
    adr = Address.objects.create(
        name="Muster", first_name="Anne", date_birth=datetime.date(2018, 9, 2)
    )
    cls.children.append(Child.objects.create(name=adr, presence=7.0))
    adr = Address.objects.create(
        name="Muster", first_name="Joel", date_birth=datetime.date(2021, 3, 2)
    )
    cls.children.append(Child.objects.create(name=adr, presence=7.0))


def create_shares(cls):
    create_sharetypes(cls)
    cls.shares = []
    for st in cls.sharetypes[0:8]:
        if st.name in ("Darlehen zinslos", "Darlehen verzinst", "Darlehen spezial", "Hypothek"):
            duration = 5
        else:
            duration = None
        for adr in cls.addresses[0:5]:
            cls.shares.append(
                Share.objects.create(
                    name=adr,
                    share_type=st,
                    state="bezahlt",
                    date=datetime.date(2000, 2, 15),
                    value=1000,
                    duration=duration,
                )
            )

    ## Anteilschein freiwillig
    cls.shares.append(
        Share.objects.create(
            name=cls.addresses[0],
            share_type=cls.sharetypes[8],
            state="bezahlt",
            date=datetime.date(2011, 11, 11),
            value=500,
        )
    )


def create_sharetypes(cls):
    cls.sharetypes = []
    cls.sharetypes.append(ShareType.objects.create(name="Anteilschein"))
    cls.sharetypes.append(ShareType.objects.create(name="Darlehen zinslos"))
    cls.sharetypes.append(ShareType.objects.create(name="Darlehen verzinst"))
    cls.sharetypes.append(ShareType.objects.create(name="Depositenkasse"))
    cls.sharetypes.append(ShareType.objects.create(name="Darlehen spezial"))
    cls.sharetypes.append(ShareType.objects.create(name="Hypothek"))
    cls.sharetypes.append(ShareType.objects.create(name="Anteilschein Einzelmitglied"))
    cls.sharetypes.append(ShareType.objects.create(name="Anteilschein Gründungsmitglied"))
    cls.sharetypes.append(ShareType.objects.create(name="Anteilschein freiwillig"))


def create_registrationevents(cls):
    cls.registrationevents = []
    cls.registrationevents.append(
        RegistrationEvent.objects.create(
            name="Public Test-Registration, 10 places", publication_type="public"
        )
    )
    cls.registrationslots = []
    now = timezone.localtime(timezone.now())
    # event_date = now + relativedelta(months=1)
    event_date = now.replace(year=now.year + 1, month=9, day=1, hour=17, minute=0, second=0)
    cls.registrationslots.append(
        RegistrationSlot.objects.create(
            name=event_date, max_places=10, event=cls.registrationevents[0]
        )
    )


def create_buildings(cls, count=2):
    cls.buildings = []
    for i in range(count):
        cls.buildings.append(Building.objects.create(name=f"Musterweg {i + 1}"))


def create_rentalunits(cls):
    create_buildings(cls)

    cls.rentalunits = []
    cls.rentalunits.append(
        RentalUnit.objects.create(
            name="001a",
            rental_type="Wohnung",
            building=cls.buildings[0],
            area=100,
            height=3,
            volume=300,
            rooms=4,
            min_occupancy=3,
            nk=100,
            rent_netto=1000,
            share=10000,
        )
    )
    cls.rentalunits.append(
        RentalUnit.objects.create(
            name="001b",
            rental_type="Wohnung",
            building=cls.buildings[0],
            area=20,
            height=3,
            volume=60,
            rooms=1,
            min_occupancy=1,
            nk=20,
            rent_netto=200,
            share=4000,
        )
    )
    cls.rentalunits.append(
        RentalUnit.objects.create(
            name="G001",
            rental_type="Gewerbe",
            building=cls.buildings[0],
            area=200,
            height=5,
            volume=1000,
            nk=300,
            rent_netto=2200,
            share=25000,
        )
    )
    cls.rentalunits.append(
        RentalUnit.objects.create(
            name="G002",
            rental_type="Gewerbe",
            building=cls.buildings[0],
            area=50,
            height=5,
            volume=250,
            nk=120,
            rent_netto=580,
            share=7000,
        )
    )
    cls.rentalunits.append(
        RentalUnit.objects.create(
            name="L001",
            rental_type="Lager",
            building=cls.buildings[0],
            area=10,
            height=4,
            volume=40,
            nk=20,
            rent_netto=130,
            share=1500,
        )
    )
    cls.rentalunits.append(
        RentalUnit.objects.create(
            name="L002",
            rental_type="Lager",
            building=cls.buildings[0],
            area=30,
            height=4,
            volume=120,
            nk=60,
            rent_netto=390,
            share=4500,
        )
    )


def create_contracts(cls):
    create_rentalunits(cls)

    cls.contracts = []

    contract = Contract.objects.create(
        comment="Contract with two rental units",
        state="unterzeichnet",
        date=datetime.date(2001, 4, 1),
    )
    contract.rental_units.set(cls.rentalunits[0:2])
    contract.contractors.set(cls.addresses[0:2])
    contract.children.set(cls.children[0:2])
    contract.save()
    cls.contracts.append(contract)
