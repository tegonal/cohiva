## Modify settings to run automated tests

import os
import warnings

from django.utils.deprecation import RemovedInDjango51Warning

import cohiva.base_config_example as cbc_test

## Load settings
from .settings import *  # noqa: F403
from .settings import DATABASES, GENO_FINANCE_ACCOUNTS, MEDIA_ROOT, SMEDIA_ROOT

## Redirect (S)MEDIA_ROOT for running tests (files will be deleted by run-tests.sh):
(head, tail) = os.path.split(MEDIA_ROOT)
MEDIA_ROOT = head + "/tests/" + tail
(head, tail) = os.path.split(SMEDIA_ROOT)
SMEDIA_ROOT = head + "/tests/" + tail
print(f"Redirected (S)MEDIA_ROOT to: {MEDIA_ROOT} and {SMEDIA_ROOT}")

## Show SA warnings?
# GNUCASH_IGNORE_SQLALCHEMY_WARNINGS = False

COHIVA_REPORT_API_TOKEN = "TEST_DUMMY_TOKEN"

## Required for legacy instances that have the old default 'utf8mb4_unicode_ci' in settings.py
DATABASES["default"]["OPTIONS"]["collation"] = "utf8mb4_general_ci"

## Display deprecation warnings only once
warnings.filterwarnings("once", category=RemovedInDjango51Warning)

## Make code aware that this is a test run
IS_RUNNING_TESTS = True

## Default settings for tests, which are overwritten temporarily by specific tests, if needed.
GENO_FORMAL = True
RESERVATION_BLOCKER_RULES = []
GENO_FINANCE_ACCOUNTS["default_debtor"]["iban"] = "CH7730000001250094239"
DEMO = False

GENO_QRBILL_CREDITOR = {
    "name": cbc_test.ORG_NAME,
    "street": cbc_test.ORG_ADDRESS_STREET_NAME,
    "house_num": cbc_test.ORG_ADDRESS_HOUSE_NUMBER,
    "pcode": cbc_test.ORG_ADDRESS_CITY_ZIPCODE,
    "city": cbc_test.ORG_ADDRESS_CITY_NAME,
    "country": cbc_test.ORG_ADDRESS_COUNTRY,
}
