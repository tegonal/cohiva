from django.db import migrations, models

from geno.countries import (
    get_country_choices,
    get_default_country_code,
    normalize_country_code,
)

COUNTRY_CHOICES = get_country_choices()


def migrate_country_to_iso(apps, schema_editor):
    Address = apps.get_model("geno", "Address")
    for address in Address.objects.all():
        code = normalize_country_code(address.country) or ""
        address.country = code
        address.save(update_fields=["country"])


class Migration(migrations.Migration):

    dependencies = [
        ("geno", "0018_alter_address_bankaccount_alter_contract_bankaccount"),
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
    ]

