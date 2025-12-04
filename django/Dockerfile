# Build stage
FROM python:3.13-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libmariadb-dev libfreetype-dev libjpeg-dev libffi-dev

# Install python dependencies in /usr/local/
WORKDIR /cohiva
# Copy only the necessary files to improve build caching
COPY requirements-docker.txt requirements.txt
COPY install_dependencies.sh install.py ./
COPY geno/python-sepa geno/python-sepa
COPY cohiva/saml2/*.patch cohiva/saml2/
RUN chmod +x ./install_dependencies.sh
RUN ./install_dependencies.sh -e docker

# Remove unnecessary stuff from /usr/local/
RUN find /usr/local/lib -type d -name '__pycache__' -exec rm -rf {} + && \
    find /usr/local/lib -type f -name '*.dist-info' -exec rm -rf {} +

# Runtime stage
FROM python:3.13-slim-bookworm AS cohiva-platform-os

# Set environment variables to ensure LibreOffice runs in headless mode
ENV DEBIAN_FRONTEND=noninteractive
ENV LIBREOFFICE_HEADLESS=1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies
    # mariadb-client-compat
RUN apt-get update && \
    apt-get install -y --no-install-recommends xmlsec1 libreoffice-writer-nogui mariadb-client locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set locale to de_CH.UTF-8
RUN sed -i '/^#.*de_CH.UTF-8/s/^# *//' /etc/locale.gen && locale-gen de_CH.UTF-8 && update-locale LANG=de_CH.UTF-8
ENV LANG=de_CH.UTF-8 \
    LC_ALL=de_CH.UTF-8

FROM cohiva-platform-os AS cohiva-platform-django

WORKDIR /cohiva
COPY --from=builder /usr/local /usr/local
COPY . .
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
