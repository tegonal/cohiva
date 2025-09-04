import subprocess
import time

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Copy production data to test instance."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Not running in the TEST environment. Not doing anything!")

        ## Source is the PRODUCTION DB and PRODUCTION MEDIA_ROOT
        prod_db = settings.TEST_DATA["db"]
        test_db = settings.DATABASES["default"]["NAME"]
        db_host = settings.DATABASES["default"]["HOST"]
        db_user = settings.DATABASES["default"]["USER"]
        db_pass = settings.DATABASES["default"]["PASSWORD"]
        media_test_dir = settings.MEDIA_ROOT
        media_prod_dir = settings.TEST_DATA["media"]
        smedia_test_dir = settings.MEDIA_ROOT + "/../smedia"
        smedia_prod_dir = settings.TEST_DATA["media"] + "/../smedia"

        start = time.time()
        ## Drop and recreate table to delete tables that don't exist in production DB yet.
        self.stdout.write("Deleting and creating new TEST database '%s'" % (test_db))
        command = (
            'echo "set autocommit=0; set unique_checks=0; set foreign_key_checks=0; '
            "drop database if exists \\`%s\\`; create database \\`%s\\`; COMMIT; SET unique_checks=1; "
            'SET foreign_key_checks=1;" | mysql -h %s -u %s -p%s'
            % (test_db, test_db, db_host, db_user, db_pass)
        )
        self.run_cmd(command, shell=True)
        end = time.time()
        self.stdout.write(" -> %.2f seconds" % (end - start))
        inter = end

        ## Maybe this could be optimized by copying tables from one DB to the other using SQL (instead of deleting, dumping and importing)?
        self.stdout.write(
            "Filling TEST database '%s' from PRODUCTION database '%s'." % (test_db, prod_db)
        )
        command = (
            '(echo "set autocommit=0; set unique_checks=0; set foreign_key_checks=0;" ; '
            "mysqldump -h %s -u %s -p%s %s ; "
            'echo "COMMIT; SET unique_checks=1; SET foreign_key_checks=1;")'
            " | mysql -h %s -u %s -p%s %s"
            % (db_host, db_user, db_pass, prod_db, db_host, db_user, db_pass, test_db)
        )
        self.run_cmd(command, shell=True)
        end = time.time()
        self.stdout.write(" -> %.2f seconds" % (end - inter))
        inter = end

        self.stdout.write(
            "NOTE: You might need to migrate the imported data to the current model "
            "of the TEST environment to prevent errors. (./manage.py migrate)"
        )

        self.stdout.write(
            "Syncing media files from '%s' to '%s'..." % (media_prod_dir, media_test_dir)
        )
        command = "rsync -a --info=NAME --delete '%s/' '%s'" % (media_prod_dir, media_test_dir)
        try:
            self.run_cmd(command, shell=True)
        except CommandError:
            self.stdout.write("=======================")
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: The rsync command failed, the smedia files might be out of sync."
                )
            )
            self.stdout.write(
                self.style.WARNING(" Most likely this is a permissions issue. Try 'chmod a+r'")
            )

        self.stdout.write(
            "Syncing smedia files from '%s' to '%s'..." % (smedia_prod_dir, smedia_test_dir)
        )
        command = "rsync -a --info=NAME --delete '%s/' '%s'" % (smedia_prod_dir, smedia_test_dir)
        try:
            self.run_cmd(command, shell=True)
        except CommandError:
            self.stdout.write("=======================")
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: The rsync command failed, the smedia files might be out of sync."
                )
            )
            self.stdout.write(
                self.style.WARNING(" Most likely this is a permissions issue. Try 'chmod a+r'")
            )
        end = time.time()
        self.stdout.write(" -> %.2f seconds" % (end - inter))
        inter = end

        if getattr(settings, "TEST_USER_PASSWORD", False):
            self.stdout.write("Changing all user passwords.")
            from django.contrib.auth.models import User

            User.objects.all().update(password=make_password(settings.TEST_USER_PASSWORD))
            end = time.time()
            self.stdout.write(" -> %.2f seconds" % (end - inter))
            inter = end

        self.stdout.write(self.style.SUCCESS("Successfully cloned production data to test"))
        end = time.time()
        self.stdout.write("TOTAL TIME: %.2f seconds" % (end - start))

    def run_cmd(self, command, **kwargs):
        # self.stdout.write("Command: %s" % command)
        show_output = False
        try:
            output = subprocess.check_output(command, **kwargs)
        except (subprocess.CalledProcessError, OSError) as e:
            if e.output and show_output:
                self.stdout.write("Output: %s" % e.output)
            raise CommandError("ERROR: Command exited with error code %s." % e.returncode)
        if output and show_output:
            self.stdout.write("Output: %s" % output)
