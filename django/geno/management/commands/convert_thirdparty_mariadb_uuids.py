# Conversion script taken and adapted from Wagtail CMS
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, models


class Command(BaseCommand):
    help = "Converts UUID columns of third-party apps from char type to the native UUID type used in MariaDB 10.7+ and Django 5.0+."

    def convert_field(self, model, field_name, null=False):
        if model._meta.get_field(field_name).model != model:
            # Field is inherited from a parent model
            return

        if not model._meta.managed:
            # The migration framework skips unmanaged models, so we should too
            return

        old_field = models.CharField(null=null, max_length=36)
        old_field.set_attributes_from_name(field_name)

        new_field = models.UUIDField(null=null)
        new_field.set_attributes_from_name(field_name)

        with connection.schema_editor() as schema_editor:
            schema_editor.alter_field(model, old_field, new_field)

    def convert_oauth2_provider(self):
        try:
            from oauth2_provider.models import AbstractIDToken, AbstractRefreshToken
        except ImportError:
            self.stdout.write(
                self.style.WARNING("Skipping oauth2_provider. Could not import all models.")
            )
            return

        for model in apps.get_models():
            if issubclass(model, AbstractRefreshToken):
                self.convert_field(model, "token_family", null=True)
            elif issubclass(model, AbstractIDToken):
                self.convert_field(model, "jti")

        self.stdout.write(self.style.SUCCESS("Processed oauth2_provider."))

    def convert_djangosaml2idp(self):
        try:
            from djangosaml2idp.models import PersistentId
        except ImportError:
            self.stdout.write(
                self.style.WARNING("Skipping djangosaml2idp. Could not import all models.")
            )
            return

        for model in apps.get_models():
            if issubclass(model, PersistentId):
                self.convert_field(model, "persistent_id")

        self.stdout.write(self.style.SUCCESS("Processed djangosaml2idp."))

    def handle(self, **options):
        self.convert_oauth2_provider()
        self.convert_djangosaml2idp()
        self.stdout.write(
            self.style.WARNING(
                "Wagtail has its own conversion script. Please run that as well:\n"
                "   ./manage.py convert_mariadb_uuids"
            )
        )
