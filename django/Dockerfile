# we use the default debian package
FROM python:3.14 AS cohiva-platform-os

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libmariadb-dev libfreetype-dev libjpeg-dev libffi-dev poppler-utils xmlsec1 libreoffice-writer
RUN apt-get install -y locales && sed -i '/^#.*de_CH.UTF-8/s/^# *//' /etc/locale.gen && locale-gen de_CH.UTF-8 && update-locale LANG=de_CH.UTF-8

# set the container-wide default
ENV LANG=de_CH.UTF-8 \
    LC_ALL=de_CH.UTF-8

FROM cohiva-platform-os AS cohiva-platform-django

WORKDIR /cohiva
COPY . .
RUN chmod +x ./install_dependencies.sh
RUN ./install_dependencies.sh -e docker

FROM cohiva-platform-django AS cohiva-platform-app

# run configuration

# run the application

CMD ["./runserver.sh"]
