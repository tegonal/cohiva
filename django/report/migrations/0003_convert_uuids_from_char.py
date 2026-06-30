# Django 5.x makes use of MariaDB's UUID data type (introducted in 10.7),
# instead of the char(32) fields that we previously used to store UUIDs. We
# convert the existing UUID field to use the new native type, as described here:
# https://code.djangoproject.com/ticket/33507, rather than the "official"
# recommendation to define a custom class that leaves the char(32) columns in
# place (https://docs.djangoproject.com/en/5.2/releases/5.0/#migrating-existing-uuidfield-on-mariadb-10-7).
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('geno', '0002_alter_report_comment_alter_report_report_type_and_more.py'),
    ]

    operations = [
        # Update UUIDFields from CHAR(32) to UUID
        migrations.RunSQL(
            sql="""
            ALTER TABLE report_report MODIFY task_id UUID NOT NULL;
            """,
        )
    ]
