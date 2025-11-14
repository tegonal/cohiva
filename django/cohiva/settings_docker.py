"""
Docker-specific settings when running Django container separately from docker-compose.
This assumes the database is accessible via localhost (port forwarded from docker-compose).
"""

from .settings_defaults import *

# Override database settings to use localhost instead of internal docker hostname
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": cbc.DB_PREFIX + "_django_test",
        "USER": cbc.DB_PREFIX,
        "PASSWORD": cbc.DB_PASSWORD,
        "HOST": "127.0.0.1",  # Use 127.0.0.1 to force TCP instead of Unix socket
        "PORT": "3306",
        "OPTIONS": {
            "sql_mode": "traditional,ALLOW_INVALID_DATES",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
        },
    }
}

# Override Celery broker to use 127.0.0.1
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

# Add localhost to allowed hosts for development - be more explicit
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "*",  # Allow all hosts for debugging
] + ALLOWED_HOSTS

# Force DEBUG mode for better error reporting
DEBUG = True

# Simplify logging - just use console
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(asctime)s %(module)s %(message)s',
    handlers=[logging.StreamHandler()]
)

# Force Django to show full error pages
ALLOWED_HOSTS = ["*"]  # Allow all hosts to eliminate ALLOWED_HOSTS issues

# Add debug toolbar if available for detailed request info
try:
    import debug_toolbar
    INSTALLED_APPS = list(INSTALLED_APPS) + ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + list(MIDDLEWARE)
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
except ImportError:
    pass

# Override the default logging completely to ensure Django logs appear
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  # Changed to True to ensure our config is used
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Changed to ERROR to catch 400 responses
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Add WhiteNoise for static file serving
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + list(MIDDLEWARE)

# Static files configuration for development
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
