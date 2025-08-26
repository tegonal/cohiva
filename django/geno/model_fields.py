from django.db import models


class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """

    def to_python(self, value):
        """
        Convert email to lowercase.
        """
        value = super().to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value
