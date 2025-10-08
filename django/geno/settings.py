from django.conf import settings

## Settings following the pattern from
## https://djangopatterns.readthedocs.io/en/latest/configuration/configure_app.html

TRANSACTION_MEMBERFEE_STARTYEAR = getattr(settings, "GENO_TRANSACTION_MEMBERFEE_STARTYEAR", None)
CHECK_MEMBERFEE_STARTYEAR = getattr(settings, "GENO_CHECK_MEMBERFEE_STARTYEAR", 9999)

## Maximal number of Links/Backlinks for Objects
MAX_LINKS_DISPLAY = getattr(settings, "GENO_MAX_LINKS_DISPLAY", 100)

## App specific reference numbers
REFERENCE_NR_APPS = getattr(
    settings,
    "GENO_REFERENCE_NR_APPS",
    {
        1: "credit_accounting",
    },
)

## TODO: Most of those settings should later go to InvoiceCategory
##       or GNUCASCH_PAYMENT_ACCOUNTS above.
GNUCASH_ACC_POST = getattr(settings, "GENO_GNUCASH_ACC_POST", "1010")  # Postkonto
GNUCASH_ACC_KASSA = getattr(settings, "GENO_GNUCASH_ACC_KASSA", "1000")  # Kasse
GNUCASH_ACC_BANK = getattr(
    settings, "GENO_GNUCASH_ACC_BANK_RENT", "1020.1"
)  # Bankkonto (Mietzinskonto)
GNUCASH_ACC_BANK = getattr(settings, "GENO_GNUCASH_ACC_BANK", "1020.2")  # Bankkonto (Baukredit)
GNUCASH_ACC_HELPER_SHARES = getattr(
    settings, "GENO_GNUCASH_ACC_HELPER_SHARES", "9250"
)  # Hilfskonto Mitgliedschaft/Anteilscheine
GNUCASH_ACC_INVOICE_RECEIVABLE = getattr(
    settings, "GENO_GNUCASH_ACC_INVOICE_RECEIVABLE", "1102"
)  # Debitoren Miete
GNUCASH_ACC_INVOICE_INCOME = getattr(
    settings, "GENO_GNUCASH_ACC_INVOICE_INCOME", "3000"
)  # Mietertrag Wohnungen
GNUCASH_ACC_INVOICE_INCOME_BUSINESS = getattr(
    settings, "GENO_GNUCASH_ACC_INVOICE_INCOME_BUSINESS", "3001"
)  # Mietertrag Gewerbe
GNUCASH_ACC_INVOICE_INCOME_PARKING = getattr(
    settings, "GENO_GNUCASH_ACC_INVOICE_INCOME_PARKING", "3002"
)  # Mietertrag Parkplätze
GNUCASH_ACC_INVOICE_INCOME_OTHER = getattr(
    settings, "GENO_GNUCASH_ACC_INVOICE_INCOME_OTHER", "3003"
)  # Mietertrag andere (Gemeinschaft/Diverses)
GNUCASH_ACC_KIOSK = getattr(
    settings, "GENO_GNUCASH_ACC_KIOSK", "3500"
)  # Diverse Einnahmen, Twint GS etc.
GNUCASH_ACC_SPENDE = getattr(settings, "GENO_GNUCASH_ACC_SPENDE", "3620")  # Ertrag Spenden
GNUCASH_ACC_OTHER = getattr(settings, "GENO_GNUCASH_ACC_OTHER", "3690")  # Übriger Ertrag
GNUCASH_ACC_MIETDEPOT = getattr(settings, "GENO_GNUCASH_ACC_MIETDEPOT", "241.0")  # Mietdepots
GNUCASH_ACC_SCHLUESSELDEPOT = getattr(
    settings, "GENO_GNUCASH_ACC_SCHLUESSELDEPOT", "241.1"
)  # Schlüsseldepots
GNUCASH_ACC_STROM = getattr(
    settings, "GENO_GNUCASH_ACC_STROM", "2302"
)  # Strompauschalen -> NK-Pauschalzahlungen
GNUCASH_ACC_NK = getattr(settings, "GENO_GNUCASH_ACC_NK", "2301")  # NK-Akonto
GNUCASH_ACC_NK_FLAT = getattr(settings, "GENO_GNUCASH_ACC_NK_FLAT", "2301")  # NK-Pauschal
GNUCASH_ACC_NK_RECEIVABLE = getattr(
    settings, "GENO_GNUCASH_ACC_NK_RECEIVABLE", "1104"
)  # Forderungen>Nebenkosten
GNUCASH_ACC_RENTREDUCTION = getattr(
    settings, "GENO_GNUCASH_ACC_RENTREDUCTION", "3015"
)  # Mietzinsausfälle
GNUCASH_ACC_LEERSTAND = getattr(
    settings, "GENO_GNUCASH_ACC_LEERSTAND", "3010"
)  # Leerstandsverluste
GNUCASH_ACC_SHARES_MEMBERS = getattr(
    settings, "GENO_GNUCASH_ACC_SHARES_MEMBERS", "2800"
)  # Genossenschaftsanteile Mitglieder
GNUCASH_ACC_SHARES_DEPOSIT = getattr(
    settings, "GENO_GNUCASH_ACC_SHARES_DEPOSIT", "2110"
)  # Depositenkasse
GNUCASH_ACC_SHARES_LOAN_INT = getattr(
    settings, "GENO_GNUCASH_ACC_SHARES_LOAN_INT", "2402"
)  # Darlehen verzinst
GNUCASH_ACC_SHARES_LOAN_NOINT = getattr(
    settings, "GENO_GNUCASH_ACC_SHARES_LOAN_NOINT", "2401"
)  # Darlehen zinslos
GNUCASH_ACC_SHARES_INTEREST = getattr(
    settings, "GENO_GNUCASH_ACC_SHARES_INTEREST", "2070"
)  # Verbindlichkeiten aus Finanzierung
GNUCASH_ACC_SHARES_INTEREST_TAX = getattr(
    settings, "GENO_GNUCASH_ACC_SHARES_INTEREST_TAX", "2010"
)  # Verbindlichkeiten aus Verrechnungssteuer
GNUCASH_ACC_INTEREST_LOAN = getattr(
    settings, "GENO_GNUCASH_ACC_INTEREST_LOAN", "6920"
)  # Zinsaufwand Darlehen
GNUCASH_ACC_INTEREST_DEPOSIT = getattr(
    settings, "GENO_GNUCASH_ACC_INTEREST_DEPOSIT", "6940"
)  # Zinsaufwand Depositenkasse
GNUCASH_ACC_MEMBER_FEE_ENTRY = getattr(
    settings, "GENO_GNUCASH_ACC_MEMBER_FEE_ENTRY", "3600"
)  # Beitrittsgebühren
GNUCASH_ACC_MEMBER_FEE = getattr(
    settings, "GENO_GNUCASH_ACC_MEMBER_FEE", "3610"
)  # Mitgliederbeiträge

QRBILL_CREDITOR = settings.GENO_QRBILL_CREDITOR

ADMIN_SESSION_COOKIE_AGE = getattr(
    settings, "GENO_ADMIN_SESSION_COOKIE_AGE", 4 * 60 * 60
)  ## Default: 4 hours in seconds

MEMBER_FLAGS = getattr(
    settings,
    "GENO_MEMBER_FLAGS",
    {
        1: "Flag 1",  # Wohnen
        2: "Flag 2",  # Gewerbe/Arbeiten
        3: "Flag 3",  # Mitarbeit/Ideen umsetzen
        4: "Flag 4",  # Projekt unterstützen
        5: "Flag 5",  # Dranbleiben
    },
)
