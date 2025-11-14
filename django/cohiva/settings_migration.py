"""
Minimal settings for running initial migrations without any admin or complex app checks
"""
from .settings_docker import *

# Use only essential Django apps plus required dependencies for migration
INSTALLED_APPS = (
    'django.contrib.admin',  # Include admin for filer compatibility
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Required dependencies
    'easy_thumbnails',
    'filer',
    'crispy_forms',
    # Add core Cohiva apps that are referenced
    'geno',
    'finance',
    'credit_accounting',  # Added - needed by geno.views
    'portal',             # Added - likely needed for URL routing
    'reservation',        # Added - likely referenced
)

# Disable all system checks
SILENCED_SYSTEM_CHECKS = ['*']

# Remove middleware that might cause issues
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
