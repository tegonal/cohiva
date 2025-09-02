import django.db.models.deletion
import select2.fields
from django.db import migrations, models

from geno import settings as geno_settings

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
        )
        ]
