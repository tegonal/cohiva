"""
Settings for Docker Compose development environment.
Inherits from settings_defaults and overrides necessary configurations.
"""

from .settings_defaults import *
import os

# Instance-specific configuration
COHIVA_INSTANCE_PATH = os.environ.get('COHIVA_INSTANCE_PATH', '/instance_files/override_files')

# Override Celery broker for Docker Compose networking
CELERY_BROKER_URL = "redis://redis:6379/0"

# Add Docker Compose hosts to allowed hosts
ALLOWED_HOSTS = ALLOWED_HOSTS + [
    "cohiva",
    "cohiva-dev-django",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
]

# Add Docker IPs if configured
if hasattr(cbc, "DOCKER_IP"):
    if isinstance(cbc.DOCKER_IP, list):
        ALLOWED_HOSTS.extend(cbc.DOCKER_IP)
    else:
        ALLOWED_HOSTS.append(cbc.DOCKER_IP)

# Add instance static files
if os.path.exists(os.path.join(COHIVA_INSTANCE_PATH, 'static')):
    STATICFILES_DIRS = [
        os.path.join(COHIVA_INSTANCE_PATH, 'static'),
    ] + list(getattr(globals(), 'STATICFILES_DIRS', []))

# Static files configuration for Docker Compose
STATIC_ROOT = "/tmp/static"
STATIC_URL = "/static/"

# WhiteNoise for static file serving
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + list(MIDDLEWARE)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

# Email configuration for Docker Compose (using Mailpit)
EMAIL_HOST = "mailpit"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False

# Override media configuration for instance files
MEDIA_ROOT = os.path.join(COHIVA_INSTANCE_PATH, 'media')

# Force DEBUG mode for development
DEBUG = True

# Disable secure cookies for local development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Override CORS for Docker Compose networking
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    "http://cohiva:8000",
    "http://cohiva-dev-django:8000",
]
