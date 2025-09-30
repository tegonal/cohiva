from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geno", "0003_shareattatchbuilding"),
    ]

    def populate_rent_netto(apps, schema_editor):
        RentalUnitModel = apps.get_model("geno", "RentalUnit")
        for obj in RentalUnitModel.objects.all():
            calculated_value = (
                (obj.rent_total if obj.rent_total is not None else 0)
                - (obj.nk if obj.nk else 0)
                - (obj.nk_electricity if obj.nk_electricity else 0)
            )
            obj.rent_netto = calculated_value
            obj.save(update_fields=["rent_netto"])
        RentalUnitModel.objects.all().update(rent_total=None)

    def reverse_populate_rent_netto(apps, schema_editor):
        RentalUnitModel = apps.get_model("geno", "RentalUnit")
        for obj in RentalUnitModel.objects.all():
            calculated_value = (
                (obj.rent_netto if obj.rent_netto is not None else 0)
                + (obj.nk if obj.nk else 0)
                + (obj.nk_electricity if obj.nk_electricity else 0)
            )
            obj.rent_netto = calculated_value
            obj.save(update_fields=["rent_total"])
        RentalUnitModel.objects.all().update(rent_netto=None)

    operations = [
        migrations.AddField(
            model_name="RentalUnit",
            name="rent_netto",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Die Netto-Miete, ohne NK und Strom.",
                max_digits=10,
                null=True,
                verbose_name="Netto-Miete exkl. NK+Strom (Fr./Monat)",
            ),
        ),
        migrations.RunPython(populate_rent_netto, reverse_populate_rent_netto),
        migrations.RemoveField(
            model_name="RentalUnit",
            name="rent_total",
        ),
    ]
