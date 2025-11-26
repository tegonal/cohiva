"""
Docker-specific settings when running Django container separately from docker-compose.
This assumes the database is accessible via localhost (port forwarded from docker-compose).
"""

from .settings_defaults import *

# Add WhiteNoise for static file serving
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
