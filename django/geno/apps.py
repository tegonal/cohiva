from django.apps import AppConfig


class GenoConfig(AppConfig):
    name = "geno"

    def ready(self):
        """Import checks when app is ready."""
        from geno import checks  # noqa: F401

        # Django 5.2 enables native UUID on MariaDB 10.7+, but mysqlclient
        # does not know how to serialize uuid.UUID objects. We patch Django's
        # conversions dict to ensure that valid SQL-literal strings containing
        # hex values are returned for every connection.
        import uuid
        import django.db.backends.mysql.base as mysql_base

        mysql_base.django_conversions[uuid.UUID] = lambda v, d: "'%s'" % v.hex
