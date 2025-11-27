# Basic configuration of your Cohiva instance.
#
# More advanced configuration can be done in settings.py and
# settings_production.py (see settings_defaults.py and
# settings_production_defaults.py for available options
# and default values).

INSTALL_DIR = "/tmp/"
DB_PREFIX = "cohiva"
DB_PASSWORD = "cohiva_password"
DB_HOSTNAME = "127.0.0.1"
PROD_HOSTNAME = "gh-action-ci"
DOMAIN = "cohiva.ch"

SITE_NAME = "Genossenschaft Musterweg"
SITE_NICKNAME = "Musterweg"
SITE_SECRET = "02th_bhn9-0l1!0w^-o!94tz=uiu)wpqvo84=gwz26j7knt07_"

ORG_NAME = "Genossenschaft Musterweg"
ORG_ADDRESS_STREET_NAME = "Musterweg"
ORG_ADDRESS_HOUSE_NUMBER = "1"
ORG_ADDRESS_CITY_ZIPCODE = "3000"
ORG_ADDRESS_CITY_NAME = "Bern"
ORG_ADDRESS_COUNTRY = "Schweiz"

ADMINS = (("Hans Muster", "info@example.com"),)

CASHCTRL_API_TOKEN = ""
CASHCTRL_TENANT = ""

FEATURES = [
FEATURES = [
    "api",
    "portal",
    "reservation",
    "report",
    "credit_accounting",
    "website",
    "cms",
    "importer",
]
