## Modify settings to run automated tests

import os
import warnings
from urllib.parse import quote

from django.utils.deprecation import RemovedInDjango51Warning

import cohiva.base_config as cbc
from finance.accounting import AccountKey

## Load settings
from .settings import *  # noqa: F403
from .settings import FINANCIAL_ACCOUNTS, MEDIA_ROOT, SMEDIA_ROOT

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

## Default settings for tests, which are overwritten temporarily by specific tests, if needed.
GENO_FORMAL = True
RESERVATION_BLOCKER_RULES = []
FINANCIAL_ACCOUNTS[AccountKey.DEFAULT_DEBTOR]["iban"] = "CH7730000001250094239"

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
