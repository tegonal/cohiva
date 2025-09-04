"""
WSGI config for Cohiva.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

project = "cohiva"

os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings_production" % project

application = get_wsgi_application()
