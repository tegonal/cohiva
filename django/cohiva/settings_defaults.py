"""
Django default settings for Cohiva.

To change settings, overwrite them in settings.py or settings_production.py
"""

import locale
from pathlib import Path
from urllib.parse import quote

import cohiva.base_config as cbc
from cohiva.version import __version__ as COHIVA_VERSION  # noqa: F401

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "https://test." + cbc.DOMAIN
PORTAL_SECONDARY_HOST = "test-secondary-portal." + cbc.DOMAIN
PORTAL_SECONDARY_NAME = "Siedlung"
PORTAL_SECONDARY_SIGNATURE = "Siedlung Musterweg"
PORTAL_SECONDARY_EMAIL_SENDER = f'"{PORTAL_SECONDARY_NAME}-Portal" <noreply@{cbc.DOMAIN}>'
SECRET_KEY = cbc.SITE_SECRET

PORTAL_BACKGROUND = None
PORTAL_BANNED_USERS = []

DEBUG = True
DEMO = False

ADMINS = cbc.ADMINS
MANAGERS = cbc.ADMINS
TEST_MAIL_RECIPIENT = ADMINS[0][1]

SERVER_EMAIL = "info@" + cbc.DOMAIN
EMAIL_SUBJECT_PREFIX = f"[Cohiva {cbc.SITE_NICKNAME}] "

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    cbc.DOCKER_IP,
    "[::1]",
    "test." + cbc.DOMAIN,
    "test." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    PORTAL_SECONDARY_HOST,
]
# Developer hosts for debugging
INTERNAL_IPS = ("localhost", "127.0.0.1")

## For use behind a proxy
## https://stackoverflow.com/questions/32631903/
## django-rest-framework-reverse-relationship-breaks-when-behind-proxy
USE_X_FORWARDED_HOST = True

## CORS for OAuth and API (https://pypi.org/project/django-cors-headers/)
CORS_ALLOWED_ORIGINS = [
    "https://chat." + cbc.DOMAIN,
    "https://app." + cbc.DOMAIN,
    "https://app-test." + cbc.DOMAIN,
    "https://chat." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    "https://app." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    "https://app-test." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://localhost:9001",
    "http://127.0.0.1:9001",
]
CORS_ALLOW_CREDENTIALS = True

## OAuth
OAUTH2_PROVIDER = {
    #   # parses OAuth2 data from application/json requests
    #  #'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
    #  'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.OAuthLibCore',
    "SCOPES": {
        "read": "Leserecht",
        "write": "Schreibrecht",
        "chat": "Anmeldedaten für " + cbc.SITE_NICKNAME + "-Chat",
        "username": "Benutzername",
        "email": "Email Adresse",
        "realname": "Vorname und Nachname",
    },
    "REQUEST_APPROVAL_PROMPT": "auto",  ## auto / force
    "PKCE_REQUIRED": False,  ## Rocket.Chat does not support PKCE
}

## Enable OIDC
OAUTH2_PROVIDER["OIDC_ENABLED"] = True
with open(str(BASE_DIR / "cohiva/oauth2/oidc.key")) as keyfile:
    OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = keyfile.read()
OAUTH2_PROVIDER["SCOPES"].update(
    {
        "profile": "Profildaten wie Name, Vorname, etc.",
        "openid": "OpenID Connect scope",
    }
)
OAUTH2_PROVIDER["OAUTH2_VALIDATOR_CLASS"] = "cohiva.oauth_validators.CohivaOAuth2Validator"

if "portal" in cbc.FEATURES:
    ## SAML 2.0
    import saml2
    import saml2.saml

    SAML_IDP_DJANGO_USERNAME_FIELD = "email"
    SAML_AUTHN_SIGN_ALG = saml2.xmldsig.SIG_RSA_SHA256
    SAML_AUTHN_DIGEST_ALG = saml2.xmldsig.DIGEST_SHA256
    SAML_ENCRYPT_AUTHN_RESPONSE = True
    SAML_IDP_CONFIG = {
        "xmlsec_binary": "/usr/bin/xmlsec1",
        "entityid": "%s/idp/metadata/" % BASE_URL,
        "description": cbc.SITE_NICKNAME + " Portal",
        # this block states what services we provide
        "service": {
            "idp": {
                "name": cbc.SITE_NICKNAME + " Portal",
                "endpoints": {
                    "single_sign_on_service": [
                        ("%s/idp/sso/post/" % BASE_URL, saml2.BINDING_HTTP_POST),
                        ("%s/idp/sso/redirect/" % BASE_URL, saml2.BINDING_HTTP_REDIRECT),
                    ],
                    "single_logout_service": [
                        ("%s/idp/slo/post/" % BASE_URL, saml2.BINDING_HTTP_POST),
                        ("%s/idp/slo/redirect/" % BASE_URL, saml2.BINDING_HTTP_REDIRECT),
                    ],
                },
                "name_id_format": [
                    saml2.saml.NAMEID_FORMAT_EMAILADDRESS,
                    saml2.saml.NAMEID_FORMAT_UNSPECIFIED,
                ],
                "sign_response": True,
                "sign_assertion": True,
                "want_authn_requests_signed": False,
            },
        },
        # set to 1 to output debugging information
        "debug": 1,
        # Signing
        "key_file": str(BASE_DIR / "cohiva/saml2/private.key"),  # private part (expects str)
        "cert_file": str(BASE_DIR / "cohiva/saml2/public.pem"),  # public part (expects str)
        # Encryption
        "encryption_keypairs": [
            {
                "key_file": str(
                    BASE_DIR / "cohiva/saml2/private.key"
                ),  # private part (expects str)
                "cert_file": str(
                    BASE_DIR / "cohiva/saml2/public.pem"
                ),  # public part (expects str)
            }
        ],
        "valid_for": 365 * 24,
        # own metadata settings
        "contact_person": [
            {
                "given_name": "Admin",
                "sur_name": "Team",
                "company": cbc.SITE_NAME,
                "email_address": "support@" + cbc.DOMAIN,
                "contact_type": "technical",
            },
            #'contact_type': 'administrative'},
        ],
        # you can set multilanguage information here
        "organization": {
            "name": [(cbc.SITE_NAME, "de"), (cbc.SITE_NAME, "en")],
            "display_name": [(cbc.SITE_NICKNAME, "de"), (cbc.SITE_NICKNAME, "en")],
            "url": [("https://www." + cbc.DOMAIN, "de"), ("https://www." + cbc.DOMAIN, "en")],
        },
    }

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  ## Django default
)
if "portal" in cbc.FEATURES:
    AUTHENTICATION_BACKENDS += (
        "oauth2_provider.backends.OAuth2Backend",
    )  ## For Oauth2 token authentification

## Application definition

INSTALLED_APPS = (
    ## Geno must be before admin so we can extend templates
    "geno",
    ## Django and third party apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "email_obfuscator",
    "django_tables2",
    "select2",
    "datetimewidget",
    "easy_thumbnails",
    "cohiva.apps.CohivaFilerConfig",
)
if "api" in cbc.FEATURES:
    INSTALLED_APPS += (
        # For API
        "rest_framework",
        "rest_framework.authtoken",
        "dj_rest_auth",
        #'rest_framework_jwt',
    )

if "cms" in cbc.FEATURES:
    INSTALLED_APPS += (
        ## For wagtail
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail",
        "modelcluster",
        "taggit",
    )

if "website" in cbc.FEATURES:
    INSTALLED_APPS += ("website",)

if "portal" in cbc.FEATURES:
    INSTALLED_APPS += (
        "portal",
        # For oauth
        "oauth2_provider",
        "corsheaders",
        # For SAML 2.0
        "djangosaml2idp",
    )

if "reservation" in cbc.FEATURES:
    INSTALLED_APPS += ("reservation",)

if "credit_accounting" in cbc.FEATURES:
    INSTALLED_APPS += ("credit_accounting",)

if "report" in cbc.FEATURES:
    INSTALLED_APPS += ("report",)

MIDDLEWARE = ()
if "portal" in cbc.FEATURES:
    MIDDLEWARE += (
        "corsheaders.middleware.CorsMiddleware",  ## CORS for Oauth and API
        ## Restrict access or redirect for secondary portal
        "portal.middleware.SecondaryPortalMiddleware",
        "oauth2_provider.middleware.OAuth2TokenMiddleware",  ## For Oauth2 token authentication
    )
MIDDLEWARE += (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #'portal.views.debug_middleware',
    "geno.middleware.SessionExpiryMiddleware",  ## Restrict cookie timeout for geno module
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ## For django-datetime-widget
    "django.middleware.locale.LocaleMiddleware",
    #'wagtail.contrib.redirects.middleware.RedirectMiddleware',
)

# TEST_RUNNER = 'django.test.runner.DiscoverRunner'

ROOT_URLCONF = "cohiva.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "cohiva/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cohiva.context_processors.baseconfig",
                "geno.context_processors.featurelist",
            ],
        },
    },
]

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "cohiva.wsgi.application"

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": cbc.DB_PREFIX + "_django_test",
        "USER": cbc.DB_PREFIX,
        "PASSWORD": cbc.DB_PASSWORD,
        "HOST": cbc.DB_HOSTNAME,  # Set to empty string for localhost.
        "PORT": "",  # Set to empty string for default.
        "OPTIONS": {
            ## ALLOW_INVALID_DATES --> workaround datetime format problem with piecash
            "sql_mode": "traditional,ALLOW_INVALID_DATES",
            "charset": "utf8mb4",
        },
    }
}
# https://docs.djangoproject.com/en/5.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "de-ch"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/Zurich"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

locale.setlocale(locale.LC_ALL, ("de_CH", "UTF-8"))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = cbc.INSTALL_DIR + "/django-production/static"

STATIC_URL = "/static/"

## Cache Buster --> Need to test this first! (duplicate files! / error...)
##STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Additional locations of static files
# STATICFILES_DIRS = (
#    BASE_DIR / 'static',
# )

## List of finder classes that know how to find static files in
## various locations.
# STATICFILES_FINDERS = (
#    # Default
#    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
##    'django.contrib.staticfiles.finders.DefaultStorageFinder',
#    # For django-scheduler / bower
#    'djangobower.finders.BowerFinder',
# )

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = cbc.INSTALL_DIR + "/django-test/media"
SMEDIA_ROOT = cbc.INSTALL_DIR + "/django-test/smedia"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(asctime)s %(levelname)-8s [%(module)s/%(funcName)s:%(lineno)d] %(message)s"
            )
        },
        "simple": {"format": "%(asctime)s %(levelname)-8s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "mail_admins_debug": {
            "level": "WARNING",
            #'filters': ['require_debug_false'],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "access_intern": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": cbc.INSTALL_DIR + "/django-test/log/access_intern.log",
            "formatter": "verbose",
        },
        "access_portal": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": cbc.INSTALL_DIR + "/django-test/log/access_portal.log",
            "formatter": "verbose",
        },
        "geno": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": cbc.INSTALL_DIR + "/django-test/log/geno.log",
            "formatter": "verbose",
        },
        "reservation": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": cbc.INSTALL_DIR + "/django-test/log/reservation.log",
            "formatter": "verbose",
        },
        "credit_accounting": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": cbc.INSTALL_DIR + "/django-test/log/credit_accounting.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "access_intern": {
            "level": "DEBUG",
            "handlers": ["access_intern"],
            "propagate": True,
        },
        "access_portal": {
            "level": "DEBUG",
            "handlers": ["access_portal"],
            "propagate": True,
        },
        "geno": {
            "level": "DEBUG",
            "handlers": ["geno"],
            "propagate": True,
        },
        "reservation": {
            "level": "DEBUG",
            "handlers": ["reservation"],
            "propagate": True,
        },
        "credit_accounting": {
            "level": "DEBUG",
            "handlers": ["credit_accounting", "mail_admins_debug"],
            "propagate": True,
        },
    },
}

## API
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 200,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.IsAdminUser",
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

## Sites
SITE_ID = 1

## django-filer - https://django-filer.readthedocs.io/en/latest/settings.html
FILER_ENABLE_PERMISSIONS = True
FILER_IS_PUBLIC_DEFAULT = False
FILER_SERVERS = {
    "private": {
        "main": {
            "ENGINE": "filer.server.backends.xsendfile.ApacheXSendfileServer",
        },
        "thumbnails": {
            "ENGINE": "filer.server.backends.xsendfile.ApacheXSendfileServer",
        },
    },
}

## Celery with redis
CELERY_BROKER_URL = "redis://localhost:6379/0"
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
#   'global_keyprefix': 'cohiva_'
# }

## Cohiva specific config
COHIVA_FEATURES = cbc.FEATURES
COHIVA_SITE_NICKNAME = cbc.SITE_NICKNAME
COHIVA_APP_EMAIL_SENDER = f'"{cbc.SITE_NICKNAME}-App" <noreply@{cbc.DOMAIN}>'

## Own config (GENO)
GENO_ID = cbc.SITE_NICKNAME
GENO_FILENAME_STR = GENO_ID
GENO_NAME = cbc.SITE_NAME
GENO_DEFAULT_EMAIL = "info@" + cbc.DOMAIN
GENO_WEBSITE = "www." + cbc.DOMAIN
GENO_FORMAL = False
GENO_CARDDAV_URI = None
GENO_CARDDAV_USER = None
GENO_CARDDAV_PASS = None

GENO_ORG_INFO = {
    "name": cbc.ORG_NAME,
    "street": cbc.ORG_ADDRESS_STREET,
    "city": cbc.ORG_ADDRESS_CITY,
    "email": "info@" + cbc.DOMAIN,
    "website": "www." + cbc.DOMAIN,
}

GENO_QRBILL_CREDITOR = {
    "name": cbc.ORG_NAME,
    "line1": cbc.ORG_ADDRESS_STREET,
    "line2": cbc.ORG_ADDRESS_CITY,
}

GENO_FINANCE_ACCOUNTS = {
    "default_debtor": {
        "name": "Bankkonto Einzahlungen",
        "iban": None,  ## QR-IBAN
        "account_iban": None,
        "account_code": "1020.1",  ## Account number in financial accounting (e.g. GnuCash)
    },
}

## Additional email senders for email sending forms (list of "Name <email>" strings).
GENO_EXTRA_EMAIL_SENDER_CHOICES = ()

GENO_CHECK_MAILINGLISTS = {
    ## List of email addresses that should be ignored in the mailinglists sync check
    "ignore_emails": [],
}

## List of Address.street strings that should have the apartment number added
GENO_ADDRESSES_WITH_APARTMENT_NUMBER = []

GENO_TRANSACTION_MEMBERFEE_STARTYEAR = 2022
GENO_GNUCASH_ACC_POST = "1010.1"

GENO_MEMBER_FLAGS = {
    1: "Wohnen",
    2: "Gewerbe/Arbeiten",
    3: "Mitarbeit/Ideen umsetzen",
    4: "Projekt unterstützen",
    5: "Dranbleiben",
}

RESERVATION_BLOCKER_RULES = [
    #    {'object': "Dachküche",
    #     'contact': {'organization': cbc.site_name, 'name': ""}
    #     'rule': {'type': 'weekly',        # weekly
    #              'weekdays': [1,4],       # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    #              'time_start': '17:00',   # HH:MM
    #              'time_end': '23:59',     # HH:MM
    #              'summary': 'Keine Reservation möglich',
    #             }
    #    },
]

if "portal" in cbc.FEATURES:
    LOGIN_URL = "/portal/login/"
else:
    LOGIN_URL = "/admin/login/"

## Alow import of data
ALLOW_IMPORT = True
## Where to load test data from
TEST_DATA = {
    "db": cbc.DB_PREFIX + "_django",
    "media": cbc.INSTALL_DIR + "/django-production/media",
}
## Session timeout etc. --> use stricter settings for more sensitive content
## using e.g. request.session.set_expiry(GENO_ADMIN_SESSION_AGE)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # True
SESSION_COOKIE_AGE = 14 * 24 * 60 * 60  ## 14 days in seconds
SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_SAMESITE = None
## CSRF cookies
CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = None
CSRF_TRUSTED_ORIGINS = [
    "https://" + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    "https://test." + cbc.DOMAIN,
    "https://test." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://localhost:9001",
    "http://127.0.0.1:9001",
]

## GnuCash interface
GNUCASH = False
GNUCASH_DB_SECRET = (
    f"mysql://{cbc.DB_PREFIX}:{quote(cbc.DB_PASSWORD)}@{cbc.DB_HOSTNAME}/"
    f"{cbc.DB_PREFIX}_gnucash_test?charset=utf8"
)
GNUCASH_READONLY = False
GNUCASH_IGNORE_SQLALCHEMY_WARNINGS = True

## CreateSend API
CREATESEND_API_KEY = None
CREATESEND_LIST_ID_NEWSLETTER = None

MAILMAN_API = {
    "url": "http://localhost:8001/3.1",
    "user": "restadmin",
    "password": None,
    "lists_domain": "lists." + cbc.DOMAIN,
}

ROCKETCHAT_API = {
    "default": {"user": "cohiva.app", "pass": None, "url": "https://chat." + cbc.DOMAIN},
}
ROCKETCHAT_WEBHOOK_TOKEN = None
ROCKETCHAT_WEBHOOK_AUTORESPONDER = {
    #'autorespond_example': {
    #   'text': (
    #       "Dies ist ein Admin-Konto. Nachrichten an dieses Konto werden in der Regel "
    #       "nicht gelesen. Bitte kontaktiere eine «richtige» Person.")
    # },
}

## API for reports
COHIVA_REPORT_API_TOKEN = None
COHIVA_REPORT_EMAIL = GENO_DEFAULT_EMAIL

## With the following option you can change the default configuration of the Django admin site
# for the Cohiva models (fields, readonly_fields, list_display, list_filter)
# COHIVA_ADMIN_FIELDS = {
#     "geno.admin": {
#         "RentalUnitAdmin.fields": [
#             "name",
#             ("label", "label_short"),
#             ("rental_type", "rooms", "min_occupancy"),
#             ("building", "floor"),
#             ("area", "area_balcony", "area_add"),
#             ("height", "volume"),
#             ("rent_netto", "nk", "nk_electricity", "rent_total"),
#             "rent_year", # activate rent per year filed
#             ("share", "depot"),
#             "note",
#             "svg_polygon",
#             "description",
#             "status",
#             "adit_serial",
#             "active",
#             "comment",
#             "ts_created",
#             "ts_modified",
#             "links",
#             "backlinks",
#         ],
#     },
# }

## Share settings
SHARE_PLOT = True

WAGTAIL_SITE_NAME = cbc.SITE_NICKNAME + " Portal"
WAGTAILADMIN_BASE_URL = BASE_URL
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL

## Silence warning about MySQL constraints
SILENCED_SYSTEM_CHECKS = [
    "models.W036",
]
