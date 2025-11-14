import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cohiva.settings_docker')

# Get the Django WSGI application
application = get_wsgi_application()

# Note: This debug wrapper solved the 400 error issue with Gunicorn
# Keep using this instead of the regular cohiva.wsgi