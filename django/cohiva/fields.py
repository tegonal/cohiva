from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from stdnum.ch import ssn


class AHVNumberField(models.CharField):
    description = "Swiss social security number (AHV-Nummer)"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 16
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def db_type(self, connection):
        return "char(13)"

    @staticmethod
    def format_value(value):
        if not ssn.is_valid(value):
            raise ValidationError(_("Invalid AHV number"))
        return ssn.format(value)

    def get_prep_value(self, value):
        if not value:
            return ""
        if not ssn.is_valid(value):
            raise ValidationError(_("Invalid AHV number"))
        return ssn.compact(value)

    def from_db_value(self, value, expression, connection):
        if not value:
            return None
        return self.format_value(value)

    def to_python(self, value):
        if not value:
            return None
        return self.format_value(value)
