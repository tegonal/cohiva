from django.conf import settings

## Settings following the pattern in https://djangopatterns.readthedocs.io/en/latest/configuration/configure_app.html

DEFAULT_VENDOR = getattr(settings, "CREDIT_ACCOUNTING_DEFAULT_VENDOR", "Depot8")

# EOF
