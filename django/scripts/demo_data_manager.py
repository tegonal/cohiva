#!/bin/env python3

import argparse
import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cohiva.settings as settings


class Settings:
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
    demodata_dir = "./demo-data"
    demodata_prefix = "demo-data"


def main():
    parser = argparse.ArgumentParser(description="Demo data manager.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="Saves PROD database and media files to ./demo-data/",
    )
    action.add_argument(
        "--load",
        "-l",
        action="store_true",
        help="Loads data and media files from ./demo-data/ to TEST",
    )
    action.add_argument(
        "--deploy-to-prod",
        action="store_true",
        help="Loads data from media files from ./demo-data/ to PROD (OVERWRITES all the data!)",
    )
    parser.add_argument("--force", action="store_true", help="Don't ask before overwriting data.")
    args = parser.parse_args()
    if args.save:
        save(args.force)
    if args.load:
        load(args.force)
    if args.deploy_to_prod:
        deploy_to_prod(args.force)


def save(force=False):
    s = Settings()
    if not os.path.isdir(s.demodata_dir):
        os.makedirs(s.demodata_dir)
    print(
        f"This will dump the PROD database to {s.demodata_dir}/{s.demodata_prefix}.sql "
        f"and saving PROD [S]MEDIA files to {s.demodata_dir}/[s]media."
    )
    if (
        os.path.exists(f"{s.demodata_dir}/{s.demodata_prefix}.sql")
        or os.path.exists(f"{s.demodata_dir}/media")
        or os.path.exists(f"{s.demodata_dir}/smedia")
    ):
        if not force and not confirm_action(
            "Are you sure you want to overwrite existing files? (y/n): "
        ):
            print("Abort")
            return
    cmd = (
        f"mysqldump --events --create-options --quote-names --skip-extended-insert "
        f'-p{s.db_pass} -u{s.db_user} {s.prod_db} | grep -vE "^INSERT INTO '
        "\\`(oauth2_provider_accesstoken|oauth2_provider_application|"
        "oauth2_provider_refreshtoken|django_session|authtoken_token|auth_user|django_admin_log"
        ')\\` VALUES \\("'
        f" > {s.demodata_dir}/{s.demodata_prefix}.sql"
    )
    run_cmd(cmd, shell=True)
    cmd = (
        f"rsync -a --info=NAME --delete --delete-missing-args {s.media_prod_dir}/* "
        f"{s.demodata_dir}/media"
    )
    run_cmd(cmd, shell=True)
    cmd = (
        f"rsync -a --info=NAME --delete --delete-missing-args {s.smedia_prod_dir}/* "
        f"{s.demodata_dir}/smedia"
    )
    run_cmd(cmd, shell=True)


def load(force=False):
    s = Settings()
    print(
        f"This will *overwrite* the TEST database with data from {s.demodata_dir}/"
        f"{s.demodata_prefix}.sql and TEST [S]MEDIA files from {s.demodata_dir}/[s]media"
    )
    if not force and not confirm_action():
        return
    cmd = (
        f"mysql -p{s.db_pass} -u{s.db_user} {s.test_db} < {s.demodata_dir}/{s.demodata_prefix}.sql"
    )
    run_cmd(cmd, shell=True)
    cmd = (
        f"rsync -a --info=NAME --delete --delete-missing-args {s.demodata_dir}/media/* "
        f"{s.media_test_dir}"
    )
    run_cmd(cmd, shell=True)
    cmd = (
        f"rsync -a --info=NAME --delete --delete-missing-args {s.demodata_dir}/smedia/* "
        f"{s.smedia_test_dir}"
    )
    run_cmd(cmd, shell=True)
    print(
        "NOTE: You might have to adjust the permissions of the [S]MEDIA files, run migrations"
        " and create users."
    )


def deploy_to_prod(force=False):
    s = Settings()
    print(
        f"This will *overwrite* the PROD database with data from {s.demodata_dir}/"
        f"{s.demodata_prefix}.sql and PROD [S]MEDIA files from {s.demodata_dir}/[s]media"
    )
    if not force and not confirm_action():
        return
    cmd = (
        f"mysql -p{s.db_pass} -u{s.db_user} {s.prod_db} < {s.demodata_dir}/{s.demodata_prefix}.sql"
    )
    run_cmd(cmd, shell=True)
    cmd = (
        f"rsync -a --info=NAME --delete --delete-missing-args {s.demodata_dir}/media/* "
        f"{s.media_prod_dir}"
    )
    run_cmd(cmd, shell=True)
    cmd = (
        f"rsync -a --info=NAME --delete --delete-missing-args {s.demodata_dir}/smedia/* "
        f"{s.smedia_prod_dir}"
    )
    run_cmd(cmd, shell=True)
    print(
        "NOTE: You might have to adjust the permissions of the [S]MEDIA files, run migrations"
        " and create users."
    )


def confirm_action(message="Are you sure you want to proceed? (y/n): "):
    while True:
        response = input(message).strip().lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'.")


def run_cmd(command, **kwargs):
    # self.stdout.write("Command: %s" % command)
    show_output = True
    try:
        output = subprocess.check_output(command, **kwargs)
    except (subprocess.CalledProcessError, OSError) as e:
        if e.output and show_output:
            print(e.output.decode())
        raise RuntimeError("ERROR: Command exited with error code %s." % e.returncode)
    if output and show_output:
        print(output.decode())


if __name__ == "__main__":
    main()
