## Settings for test/development environment
## For production settings use settings_production.py

## Load default test settings
from .settings_defaults import *  # noqa: F403
# from .settings_defaults import LOGGING

## Put your custom test settings here:
######################################

## Example: Configure outbound SMTP
# EMAIL_HOST = "mail.example.com"
# EMAIL_HOST_USER = "smtpuser"
# EMAIL_HOST_PASSWORD = "secret"

## Example: Enable debug logging in a third-party package (here oauthlib)
# LOGGING["loggers"]["oauthlib"] = {
#    "level": "DEBUG",
#    "handlers": ["access_portal"],
#    "propagate": True,
# }
