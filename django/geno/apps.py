from django.apps import AppConfig


class GenoConfig(AppConfig):
    name = "geno"

    def ready(self):
        """Import checks when app is ready."""
        # Django 5.2 enables native UUID on MariaDB 10.7+, but mysqlclient
        # does not know how to serialize uuid.UUID objects. We patch Django's
        # conversions dict to ensure that valid SQL-literal strings containing
        # hex values are returned for every connection.
        import uuid

        import django.db.backends.mysql.base as mysql_base

        from geno import checks  # noqa: F401

        mysql_base.django_conversions[uuid.UUID] = lambda v, d: "'%s'" % v.hex

        # Delegate directly to Django's native setter for .choices, to avoid
        # an infinite recursion caused by the select2 library interacting with
        # Django 5.2's super() function in an unexpected way.
        import select2.fields
        from django.forms.fields import ChoiceField as DjangoChoiceField

        def _select2_choices_setter(self, value):
            DjangoChoiceField.choices.fset(self, value)

        select2.fields.Select2FieldMixin.choices = property(
            select2.fields.Select2FieldMixin.choices.fget,
            _select2_choices_setter,
        )
