#!/usr/bin/bash

# exit on error
set -e

# if called from CI (GitHub Actions), copy the base_config_for_tests.py to base_config.py
if [ -n "$GITHUB_ACTIONS" ] ; then
    touch cohiva/settings.py
    cp cohiva/base_config_for_tests.py cohiva/base_config.py
fi

## Show warnings?
export PYTHONWARNINGS=always

INSTALL_DIR=`grep "^INSTALL_DIR = " cohiva/base_config.py | cut -d \" -f 2`

## Run coverage? No / full / append
COVERAGE_OPT=""
#COVERAGE_OPT="--source $INSTALL_DIR/django"
COVERAGE=""
#COVERAGE="coverage run $COVERAGE_OPT"
#COVERAGE="coverage run --append $COVERAGE_OPT"

## Base test command
TESTCMD="./manage.py test --settings=cohiva.settings_for_tests"

## Full test suite incl. migrations
# Run tests and capture the exit code of the test runner even though output is piped to tee.
# Temporarily disable 'set -e' so the script doesn't abort before we capture the exit code.
set +e
$COVERAGE $TESTCMD 2>&1 | tee test.log
TEST_EXIT_CODE=${PIPESTATUS[0]}
# restore 'set -e' behavior
set -e

## Keep DB (don't run migrations)
#$COVERAGE $TESTCMD --keepdb 2>&1 | tee test.log

## Run a subset of tests, e.g.
#$COVERAGE $TESTCMD --keepdb geno.tests
#$COVERAGE $TESTCMD --keepdb geno.tests.test_registration.TestRegistrationForm
#$COVERAGE $TESTCMD --keepdb portal.tests
#$COVERAGE $TESTCMD --keepdb report.tests
#$COVERAGE $TESTCMD --keepdb report.tests.test_tasks
#$COVERAGE $TESTCMD --keepdb credit_accounting.tests.test_models

if [ -n "$COVERAGE" ] ; then
    #coverage report
    coverage html 2>&1 | tee coverage.log
fi

## Cleanup
## TODO: Move this cleanup step to a custom test runner, so it is integrated in
##       the ./manage.py test command, and tests also work when run from the
##       IDE, for example.
rm -rf $INSTALL_DIR/django-test/tests

# exit with the test runner's exit code so callers (CI, scripts) see the test result
exit ${TEST_EXIT_CODE:-0}

#EOF
