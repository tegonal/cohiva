#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

try:
    from django.core.management.utils import get_random_secret_key
except ImportError:
    print(
        "Django does not seem to be installed. Please check that you are in the correct virtual environment."
    )


def setup():
    link_missing_templates()
    copy_missing_settings()
    generate_missing_base_config()
    create_missing_dirs()
    generate_saml2_keys()


def generate_missing_base_config():
    if not os.path.exists("./cohiva/base_config.py"):
        with open("./cohiva/base_config_example.py") as fin:
            with open("./cohiva/base_config.py", "w") as fout:
                for line in fin:
                    if line.startswith('SITE_SECRET = "<SECRET>"'):
                        fout.write(line.replace("<SECRET>", get_random_secret_key()))
                    else:
                        fout.write(line)
        print("Generated example ./cohiva/base_config.py")
        print(" ==> Please edit it to configure your instance and run setup.py again!")
        sys.exit(0)


def copy_missing_settings():
    """Copy example settings files where they are missing"""
    config_files = [
        ("./cohiva/settings.py", "./cohiva/settings_example.py"),
        ("./cohiva/settings_production.py", "./cohiva/settings_production_example.py"),
    ]
    for template in config_files:
        if not os.path.exists(template[0]):
            print(f"Copying missing config file from example {template[0]} → {template[1]}.")
            shutil.copyfile(template[1], template[0])


def link_missing_templates():
    """Link to examples where no custom template is in place"""
    custom_templates = [
        ("./portal/templates/portal/base.html", "./examples/base.html"),
        ("./portal/templates/portal/base_secondary.html", "./examples/base_secondary.html"),
        ("./portal/templates/portal/secondary.html", "./examples/secondary.html"),
        ("./portal/templates/portal/portal_page.html", "./examples/portal_page.html"),
        ("./portal/static", "./static_example"),
        ("./geno/templates/geno/contract_email.html", "./examples/contract_email.html"),
        ("./geno/templates/geno/email_invoice.html", "./examples/email_invoice.html"),
        (
            "./geno/templates/geno/email_rent_bill_first.html",
            "./examples/email_rent_bill_first.html",
        ),
        ("./website", "./website_example"),
    ]
    for template in custom_templates:
        if not os.path.exists(template[0]):
            print(f"Linking missing template to example {template[0]} → {template[1]}.")
            os.symlink(template[1], template[0])


def create_missing_dirs():
    import cohiva.base_config as cbc

    dirs = [
        cbc.INSTALL_DIR,
        cbc.INSTALL_DIR + "/django-test",
        cbc.INSTALL_DIR + "/django-test/log",
        cbc.INSTALL_DIR + "/django-production",
        cbc.INSTALL_DIR + "/django-production/log",
    ]

    for d in dirs:
        if not os.path.exists(d):
            print(f"Creating missing directory {d}")
            os.mkdir(d)


def generate_saml2_keys():
    if os.path.exists("./cohiva/saml2/private.key") or os.path.exists("./cohiva/saml2/public.pem"):
        return
    print("Generating SAML2 keys in ./cohiva/saml2/.")
    subprocess.run(
        [
            "openssl",
            "req",
            "-nodes",
            "-new",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-days",
            "3650",
            "-keyout",
            "./cohiva/saml2/private.key",
            "-out",
            "./cohiva/saml2/public.pem",
        ]
    )


if __name__ == "__main__":
    setup()
