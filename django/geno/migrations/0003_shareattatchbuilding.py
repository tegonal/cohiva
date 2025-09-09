import django.db.models.deletion
import select2.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geno", "0002_contenttemplateoptiontype"),
    ]

    operations = [
        migrations.AddField(
            model_name="share",
            name="attached_to_building",
            field=select2.fields.ForeignKey(
                blank=True,
                help_text="Nur ausfüllbar wenn keine Vertrag gewählt ist.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="building_attached_shares",
                to="geno.building",
                verbose_name="Fixe Zuteilung zu Liegenschaft",
            ),
        ),
        migrations.AddConstraint(
            model_name="share",
            constraint=models.CheckConstraint(
                check=models.Q(attached_to_building=None) | models.Q(attached_to_contract=None),
                name="geno_share_attached_to_building_or_contract",
            ),
        ),
    ]
