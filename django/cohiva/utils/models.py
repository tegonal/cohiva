from django.apps import apps
from django.db.models import Max
from django.db.utils import OperationalError


def get_next_number(app_name: str, model_name: str, field_name: str, increment=1):
    # Find the highest existing number in the database
    model = apps.get_model(app_name, model_name)
    try:
        max_value = model.objects.aggregate(Max(field_name))[field_name + "__max"]
    except OperationalError:
        max_value = None

    if not isinstance(max_value, int):
        max_value = None

    # Add increment to the highest number (or to zero if it does not exist).
    if max_value is None:
        return increment
    return max_value + increment
