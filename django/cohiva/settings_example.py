## Settings for test/development environment
## For production settings use settings_production.py

## Load default test settings
from .settings_defaults import *  # noqa: F403

# from .settings_defaults import LOGGING

## Put your custom test settings here:
######################################

## Disable secure cookies for local development over HTTP
## WARNING: Only enable this for local development! Never use in production!
## The bootstrap script will automatically uncomment these for you.
# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False

## Configure outbound SMTP (here using Mailpit for local testing)
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = "mailpituser"
EMAIL_HOST_PASSWORD = "secret"

## Example: Enable debug logging in a third-party package (here oauthlib)
# LOGGING["loggers"]["oauthlib"] = {
#    "level": "DEBUG",
#    "handlers": ["access_portal"],
#    "propagate": True,
# }
