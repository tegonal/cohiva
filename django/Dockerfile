# we use the default debian package
FROM python:3.12 AS cohiva-platform-os

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libmariadb-dev libfreetype-dev libjpeg-dev libffi-dev poppler-utils xmlsec1 libreoffice-writer mariadb-client mariadb-client-compat
RUN apt-get install -y locales && sed -i '/^#.*de_CH.UTF-8/s/^# *//' /etc/locale.gen && locale-gen de_CH.UTF-8 && update-locale LANG=de_CH.UTF-8

# set the container-wide default
ENV LANG=de_CH.UTF-8 \
    LC_ALL=de_CH.UTF-8

FROM cohiva-platform-os AS cohiva-platform-django

WORKDIR /cohiva
COPY . .
RUN chmod +x ./install_dependencies.sh
RUN ./install_dependencies.sh -e docker
# install gunicorn and whitenoise (if not already installed via dependencies script)
RUN pip install --no-cache-dir gunicorn whitenoise
# optional gunicorn tuning vars
ENV GUNICORN_WORKERS=2
ENV GUNICORN_BIND=0.0.0.0:8000
ENV GUNICORN_LOG_LEVEL=info
#ENV GUNICORN_TIMEOUT=120
#ENV DJANGO_DEBUG=1
EXPOSE 8000

FROM cohiva-platform-django AS cohiva-platform-app

# Create directory for static files
RUN mkdir -p /tmp/static
RUN mkdir -p /instance_files/override_files

# Create directories for instance-specific files and logs
RUN mkdir -p /var/www/cohiva/django-test/log
RUN mkdir -p /var/www/cohiva/django-production/log

# Set environment variable for instance path to match docker-compose
ENV COHIVA_INSTANCE_PATH=/instance_files/override_files

# Create entrypoint script for initialization
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
#ENV GUNICORN_CMD_ARGS="--workers ${GUNICORN_WORKERS} --bind ${GUNICORN_BIND} --timeout ${GUNICORN_TIMEOUT}"
ENV GUNICORN_CMD_ARGS="--workers ${GUNICORN_WORKERS} --bind ${GUNICORN_BIND} --log-level ${GUNICORN_LOG_LEVEL}}"
CMD ["gunicorn", "cohiva.wsgi:application"]
