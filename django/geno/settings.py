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
