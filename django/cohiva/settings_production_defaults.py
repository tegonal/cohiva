"""
Django default production settings for Cohiva.

To change settings, overwrite them in settings_production.py
"""

from urllib.parse import quote

import cohiva.base_config as cbc

from .settings import *  # noqa: F403
from .settings import DATABASES, FINANCIAL_ACCOUNTING_BACKENDS, LOGGING

# Disable debugging
DEBUG = False

# Production base URL
BASE_URL = "https://" + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN
PORTAL_SECONDARY_HOST = "portal2." + cbc.DOMAIN

# Media file storage
MEDIA_ROOT = cbc.INSTALL_DIR + "/django-production/media"
SMEDIA_ROOT = cbc.INSTALL_DIR + "/django-production/smedia"

# Use production databases
DATABASES["default"]["NAME"] = cbc.DB_PREFIX + "_django"
FINANCIAL_ACCOUNTING_BACKENDS["gnucash"]["OPTIONS"]["DB_SECRET"] = (
    f"mysql://{cbc.DB_PREFIX}:{quote(cbc.DB_PASSWORD)}@{cbc.DB_HOSTNAME}/"
    f"{cbc.DB_PREFIX}_gnucash?charset=utf8"
)

# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [cbc.PROD_HOSTNAME + "." + cbc.DOMAIN]

## Auth
# LOGIN_URL='/login'
CORS_ALLOWED_ORIGINS = [
    "https://chat." + cbc.DOMAIN,
    "https://app." + cbc.DOMAIN,
    "https://chat." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
    "https://app." + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
]

CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    "https://" + cbc.PROD_HOSTNAME + "." + cbc.DOMAIN,
]

if "portal" in cbc.FEATURES:
    # Adjust SAML2 URLs
    import saml2

    from .settings import SAML_IDP_CONFIG

    SAML_IDP_CONFIG["entityid"] = "%s/idp/metadata/" % BASE_URL
    SAML_IDP_CONFIG["service"]["idp"]["endpoints"] = {
        "single_sign_on_service": [
            ("%s/idp/sso/post/" % BASE_URL, saml2.BINDING_HTTP_POST),
            ("%s/idp/sso/redirect/" % BASE_URL, saml2.BINDING_HTTP_REDIRECT),
        ],
        "single_logout_service": [
            ("%s/idp/slo/post/" % BASE_URL, saml2.BINDING_HTTP_POST),
            ("%s/idp/slo/redirect/" % BASE_URL, saml2.BINDING_HTTP_REDIRECT),
        ],
    }

# Protect importing (overwrite default value true)
ALLOW_IMPORT = False

## Production logging
LOGGING["handlers"]["access_intern"]["filename"] = (
    cbc.INSTALL_DIR + "/django-production/log/access_intern.log"
)
LOGGING["handlers"]["access_portal"]["filename"] = (
    cbc.INSTALL_DIR + "/django-production/log/access_portal.log"
)
LOGGING["handlers"]["geno"]["filename"] = cbc.INSTALL_DIR + "/django-production/log/geno.log"
LOGGING["handlers"]["reservation"]["filename"] = (
    cbc.INSTALL_DIR + "/django-production/log/reservation.log"
)
LOGGING["handlers"]["reservation"]["level"] = "INFO"
LOGGING["handlers"]["credit_accounting"]["filename"] = (
    cbc.INSTALL_DIR + "/django-production/log/credit_accounting.log"
)
LOGGING["handlers"]["finance_accounting"]["filename"] = (
    cbc.INSTALL_DIR + "/django-production/log/finance_accounting.log"
)

## Use a different database number for production
CELERY_BROKER_URL = "redis://localhost:6379/1"

# Add WhiteNoise for static file serving
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + list(MIDDLEWARE)

# Static files configuration
STATIC_ROOT = "/tmp/static"  # Temporary location for collected static files
STATIC_URL = "/static/"

# Use simpler WhiteNoise backend without compression
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}