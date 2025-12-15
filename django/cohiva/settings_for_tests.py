## Modify settings to run automated tests

import os
import warnings
from urllib.parse import quote

from django.utils.deprecation import RemovedInDjango51Warning

import cohiva.base_config_example as cbc_test
import cohiva.base_config_for_tests as cbc
from finance.accounting import AccountKey

## Load settings
from .settings import *  # noqa: F403
from .settings import DATABASES, FINANCIAL_ACCOUNTS, INSTALLED_APPS, MEDIA_ROOT, SMEDIA_ROOT
from .settings_defaults import *  # noqa: F403

## Redirect (S)MEDIA_ROOT for running tests (files will be deleted by run-tests.sh):
(head, tail) = os.path.split(MEDIA_ROOT)
MEDIA_ROOT = head + "/tests/" + tail
(head, tail) = os.path.split(SMEDIA_ROOT)
SMEDIA_ROOT = head + "/tests/" + tail
print(f"Redirected (S)MEDIA_ROOT to: {MEDIA_ROOT} and {SMEDIA_ROOT}")

COHIVA_REPORT_API_TOKEN = "TEST_DUMMY_TOKEN"

## Display deprecation warnings only once
warnings.filterwarnings("once", category=RemovedInDjango51Warning)

## Make code aware that this is a test run
IS_RUNNING_TESTS = True

if os.getenv("SKIP_SLOW", "false") == "true":
    ## Speed up tests in quick mode
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
    if os.getenv("KEEP_DB", "false") == "false":
        ## Skip migrations and use a test runner that applies selected migrations needed for tests
        DATABASES["default"]["TEST"] = {"MIGRATE": False}
        TEST_RUNNER = "cohiva.utils.migrations_for_tests.SelectiveMigrationRunner"

## Default settings for tests, which are overwritten temporarily by specific tests, if needed.
GENO_FORMAL = True
DEMO = False
RESERVATION_BLOCKER_RULES = []
FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["iban"] = "CH7730000001250094239"
FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["account_code"] = "1020.1"

FINANCIAL_ACCOUNTING_CASHCTRL_LIVE_TESTS = False

FINANCIAL_ACCOUNTING_DEFAULT_BACKEND = "dummy_test"
FINANCIAL_ACCOUNTING_BACKENDS = {
    "gnucash_test": {
        "BACKEND": "finance.accounting.GnucashBook",
        "OPTIONS": {
            "DB_SECRET": (
                f"mysql://{cbc.DB_PREFIX}:{quote(cbc.DB_PASSWORD)}@{cbc.DB_HOSTNAME}/"
                f"{cbc.DB_PREFIX}_gnucash_test?charset=utf8"
            ),
            "READONLY": False,
            "IGNORE_SQLALCHEMY_WARNINGS": True,
        },
    },
    "cashctrl_test": {
        "BACKEND": "finance.accounting.CashctrlBook",
        "OPTIONS": {
            "API_HOST": "cashctrl123.com",
            "API_TOKEN": "123test",
            "TENANT": "cohiva-test",
        },
    },
    "cashctrl_test_live": {
        "BACKEND": "finance.accounting.CashctrlBook",
        "DB_ID": 1,
        "OPTIONS": {
            "API_HOST": "cashctrl.com",
            "API_TOKEN": f"{cbc.CASHCTRL_API_TOKEN}",
            "TENANT": f"{cbc.CASHCTRL_TENANT}",
        },
    },
    "dummy_test": {
        "BACKEND": "finance.accounting.DummyBook",
        "OPTIONS": {
            "SAVE_TRANSACTIONS": True,
        },
    },
    "dummy_test2": {
        "BACKEND": "finance.accounting.DummyBook",
        "DB_ID": 1,
        "OPTIONS": {
            "SAVE_TRANSACTIONS": False,
        },
    },
}
GENO_QRBILL_CREDITOR = {
    "name": cbc_test.ORG_NAME,
    "street": cbc_test.ORG_ADDRESS_STREET_NAME,
    "house_num": cbc_test.ORG_ADDRESS_HOUSE_NUMBER,
    "pcode": cbc_test.ORG_ADDRESS_CITY_ZIPCODE,
    "city": cbc_test.ORG_ADDRESS_CITY_NAME,
    "country": cbc_test.ORG_ADDRESS_COUNTRY,
}

if "importer" not in INSTALLED_APPS:
    INSTALLED_APPS += ("importer",)
