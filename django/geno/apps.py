from django.apps import AppConfig


class GenoConfig(AppConfig):
    name = "geno"

    def ready(self):
        """Import checks when app is ready."""
        # Delegate directly to Django's native setter for .choices, to avoid
        # an infinite recursion caused by the select2 library interacting with
        # Django 5.2's super() function in an unexpected way.
        import select2.fields
        from django.forms.fields import ChoiceField as DjangoChoiceField

        from geno import checks  # noqa: F401

        def _select2_choices_setter(self, value):
            DjangoChoiceField.choices.fset(self, value)

        select2.fields.Select2FieldMixin.choices = property(
            select2.fields.Select2FieldMixin.choices.fget,
            _select2_choices_setter,
        )
