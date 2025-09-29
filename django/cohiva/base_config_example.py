# Basic configuration of your Cohiva instance.
#
# More advanced configuration can be done in settings.py and
# settings_production.py (see settings_defaults.py and
# settings_production_defaults.py for available options
# and default values).

INSTALL_DIR = "/var/www/cohiva"
DB_PREFIX = "cohiva"
DB_PASSWORD = "c0H1v4"
DB_HOSTNAME = "127.0.0.1"
PROD_HOSTNAME = "demo"
DOMAIN = "cohiva.ch"

# Container IP address, if you run Cohiva in Docker (optional, comment out to disable).
DOCKER_IP = "172.20.42.100"

SITE_NAME = "Genossenschaft Musterweg"
SITE_NICKNAME = "Musterweg"
SITE_SECRET = "<SECRET>"
## The SITE_SECRET can be generated with:
##      python3 -c 'from django.core.management.utils import get_random_secret_key;
##                  print(get_random_secret_key())'

ORG_NAME = "Genossenschaft Musterweg"
ORG_ADDRESS_STREET = "Musterweg 1"
ORG_ADDRESS_CITY = "3000 Bern"

ADMINS = (("Hans Muster", "info@example.com"),)

FEATURES = [
    "api",
    "portal",
    "reservation",
    "report",
    "credit_accounting",
    "website",
    "cms",
]
