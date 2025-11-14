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
ENV GUNICORN_WORKERS=2 \
    GUNICORN_BIND=0.0.0.0:8000 \
    GUNICORN_TIMEOUT=120 \
    DJANGO_SETTINGS_MODULE=cohiva.settings_docker \
    DJANGO_DEBUG=1
EXPOSE 8000

FROM cohiva-platform-django AS cohiva-platform-app

# Create directory for static files
RUN mkdir -p /tmp/static

# Use debug WSGI wrapper without unsupported static-map
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--log-level", "debug", "cohiva.wsgi_debug:application"]
