#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

import cohiva.base_config as cbc

## Project name
PROJECT = "cohiva"

## Destination path for production installation.
DEPLOY_DEST_PRODUCTION = cbc.INSTALL_DIR + "/django-production"

## Project and apps to deploy
MODULES = (PROJECT, "geno", "finance")
if "website" in cbc.FEATURES:
    MODULES += ("website",)
if "portal" in cbc.FEATURES:
    MODULES += ("portal",)
if "reservation" in cbc.FEATURES:
    MODULES += ("reservation",)
if "credit_accounting" in cbc.FEATURES:
    MODULES += ("credit_accounting",)
if "report" in cbc.FEATURES:
    MODULES += ("report",)

## Ignore static files that match those patterns.
## Set 'CLEAR_STATIC = True' for one run after changes and to REMOVE FILES!.
IGNORE_STATIC = ("*.bak", "*.sh", "*.pl", "*.py")
CLEAR_STATIC = False

## Ignore code files that match those patterns
## Set 'CLEAR_CODE = True' for one run after changes.
IGNORE_CODE = (
    "*.pyc",
    ".git*",
    ".svn",
    "*.swp",
    "*.bak*",
    "*.old",
    "*.orig",
    "/*/tests",
    ".ruff_cache",
    ".mypy_cache",
    "deployment_custom",
    "static_example",
    "/geno/python-sepa",
    "__pycache__",
)
CLEAR_CODE = False

RELOAD_WEBSERVER = False
RELOAD_CELERY = False


def update_deployed_version_file():
    file_path = Path(DEPLOY_DEST_PRODUCTION) / "cohiva" / "version.py"
    git_tag = subprocess.check_output(["git", "describe", "--tags", "--always"], text=True).strip()
    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

    lines = file_path.read_text().splitlines()
    updated_lines = []
    for line in lines:
        if line.startswith("git_tag = "):
            updated_lines.append(f'git_tag = "{git_tag}"')
        elif line.startswith("git_commit = "):
            updated_lines.append(f'git_commit = "{git_commit}"')
        else:
            updated_lines.append(line)
    file_path.write_text("\n".join(updated_lines) + "\n")


def deploy_production():
    global RELOAD_WEBSERVER
    print("------------------------------------------------------------")
    print("Deploying production installation to: %s" % DEPLOY_DEST_PRODUCTION)
    print("------------------------------------------------------------")
    ## Create directory and readme file if not present
    if not os.path.isdir(DEPLOY_DEST_PRODUCTION):
        os.makedirs(DEPLOY_DEST_PRODUCTION)
        RELOAD_WEBSERVER = True
    if not os.path.exists(DEPLOY_DEST_PRODUCTION + "/README"):
        f = open(DEPLOY_DEST_PRODUCTION + "/README", "w")
        f.write(
            "DEPLOYED PRODUCTION FILES!\n\n"
            "Don't edit the files in this directory.\n"
            "Edit the code in the development directory and use deploy.py\n"
        )
        f.close()
    for subdir in ("log", "media", "smedia"):
        if not os.path.isdir(DEPLOY_DEST_PRODUCTION + "/" + subdir):
            os.makedirs(DEPLOY_DEST_PRODUCTION + "/" + subdir)

    print("")
    print("1. Updating code")
    print("****************")
    ## Rsync code
    rsync_opts = "--copy-links --exclude '" + "' --exclude '".join(IGNORE_CODE) + "'"
    if CLEAR_CODE:
        rsync_opts = rsync_opts + " --delete-excluded"
    for module in MODULES:
        print(f"- Syncing {module}...")
        os.system(
            "rsync -a --info=NAME %s %s --exclude static/ --exclude OLD/ --delete %s/"
            % (module, rsync_opts, DEPLOY_DEST_PRODUCTION)
        )

    ## Other deployment files (currently only celery config)
    print("- Syncing deployment...")
    celery_files = "deployment/celery.conf deployment/cohiva-celery.service"
    os.system(
        f"rsync -a --info=NAME {celery_files} {rsync_opts} --delete --delete-missing-args {DEPLOY_DEST_PRODUCTION}/celery/"
    )

    print("- Updating version.py")
    update_deployed_version_file()

    print("")
    print("2. Updating static files")
    print("************************")
    ## Collect and copy static files
    static_opt = "-i '" + "' -i '".join(IGNORE_STATIC) + "'"
    if CLEAR_STATIC:
        static_opt = static_opt + " --clear"
    os.system("./manage.py collectstatic --noinput %s" % static_opt)

    print("")
    print("3. Updating database")
    print("********************")
    ## Apply migrations
    os.system("./manage.py migrate --settings=%s.settings_production" % PROJECT)


## Apply changes to production installation.
deploy_production()

print("")
if RELOAD_WEBSERVER:
    print("Reloading webserver")
    os.system("sudo service apache2 reload")
else:
    print("Touching wsgi.py to force server reload")
    os.system("touch -c %s/%s/wsgi.py" % (DEPLOY_DEST_PRODUCTION, PROJECT))

if RELOAD_CELERY:
    print("Reloading Celery service (requires root password)")
    os.system('su -c "systemctl restart cohiva-celery.service"')

print("")
