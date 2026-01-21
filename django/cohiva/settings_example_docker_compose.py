"""
Settings for Docker Compose development environment.
Inherits from settings_defaults and overrides necessary configurations.
"""

import os

from .settings_defaults import *  # noqa: F403
from .settings_defaults import CORS_ALLOWED_ORIGINS

# Instance-specific configuration
COHIVA_INSTANCE_PATH = os.environ.get("COHIVA_INSTANCE_PATH", "/instance_files/override_files")

# Override Celery broker for Docker Compose networking
CELERY_BROKER_URL = "redis://redis:6379/0"

# Static files configuration for Docker Compose
STATIC_ROOT = "/tmp/static"
if os.path.exists(os.path.join(COHIVA_INSTANCE_PATH, "static")):
    STATICFILES_DIRS = [
        os.path.join(COHIVA_INSTANCE_PATH, "static"),
    ] + list(getattr(globals(), "STATICFILES_DIRS", []))


# Email configuration for Docker Compose (using Mailpit)
EMAIL_HOST = "mailpit"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False

# Override media configuration for instance files
MEDIA_ROOT = os.path.join(COHIVA_INSTANCE_PATH, "media")

# Force DEBUG mode for development (NOT FOR PRODUCTION!)
DEBUG = True

# Disable secure cookies for local development (NOT FOR PRODUCTION!)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Override CORS for Docker Compose networking
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    "http://cohiva:8000",
    "http://cohiva-dev-django:8000",
]
