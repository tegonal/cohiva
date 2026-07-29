from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("geno", "0028_remove_documenttype_template_file"),
    ]

    operations = [
        migrations.RenameField(
            model_name="share", old_name="date", new_name="payment_date"
        ),
        migrations.RenameField(
            model_name="share", old_name="date_end", new_name="repayment_date"
        ),
        migrations.RenameField(
            model_name="share", old_name="state", new_name="payment_state"
        ),
    ]

