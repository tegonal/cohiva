from django.db import migrations, models

from cohiva.utils.countries import (
    get_country_choices,
    get_default_country_code,
    normalize_country_code,
)

from geno.utils import send_info_mail

COUNTRY_CHOICES = get_country_choices()


def migrate_country_to_iso(apps, schema_editor):
    Address = apps.get_model("geno", "Address")
    for address in Address.objects.all():
        code = normalize_country_code(address.country)
        if code is None:
            send_info_mail(f"Problem migrating Address.country to code", f"Could not normalize country code '{address.country}' for Address {address.pk} (setting to empty)")
            code = ""
        address.country = code
        address.save(update_fields=["country"])
    Building = apps.get_model("geno", "Building")
    for building in Building.objects.all():
        code = normalize_country_code(building.country)
        if code is None:
            send_info_mail(f"Problem migrating Building.country to code", f"Could not normalize country code '{building.country}' for Building {building.pk} (setting to empty)")
            code = ""
        building.country = code
        building.save(update_fields=["country"])

class Migration(migrations.Migration):

    dependencies = [
        ("geno", "0020_alter_registrationevent_enable_telephone"),
    ]

    operations = [
        migrations.RunPython(migrate_country_to_iso, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="address",
            name="country",
            field=models.CharField(
                "Land",
                max_length=2,
                blank=True,
                default=get_default_country_code,
                choices=COUNTRY_CHOICES,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="country",
            field=models.CharField(
                "Land",
                max_length=2,
                blank=True,
                default=get_default_country_code,
                choices=COUNTRY_CHOICES,
            ),
        ),
    ]

