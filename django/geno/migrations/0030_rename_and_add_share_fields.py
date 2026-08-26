from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geno", "0028_remove_documenttype_template_file"),
    ]

    operations = [
        migrations.RenameField(
            model_name="share",
            old_name="date",
            new_name="payment_date",
        ),
        migrations.RenameField(
            model_name="share",
            old_name="date_end",
            new_name="repayment_date",
        ),
        migrations.AddField(
            model_name="share",
            name="effective_from",
            field=models.DateField(blank=True, default=None, null=True, verbose_name="Wirksam ab"),
        ),
        migrations.AddField(
            model_name="share",
            name="effective_until",
            field=models.DateField(
                blank=True, default=None, null=True, verbose_name="Wirksam bis"
            ),
        ),
        migrations.RemoveField(model_name="share", name="state"),
        migrations.AlterField(
            model_name="share",
            name="payment_date",
            field=models.DateField(
                blank=True, default=None, null=True, verbose_name="Zahlungsdatum"
            ),
        ),
        migrations.AlterField(
            model_name="share",
            name="repayment_date",
            field=models.DateField(
                blank=True, default=None, null=True, verbose_name="Rückzahlungsdatum"
            ),
        ),
    ]
