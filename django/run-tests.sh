#!/usr/bin/bash
#
## Show warnings?
export PYTHONWARNINGS=always

INSTALL_DIR=`grep "^INSTALL_DIR = " cohiva/base_config.py | cut -d \" -f 2`

## Run coverage? No / full / append
COVERAGE=""
#COVERAGE="coverage run --source $INSTALL_DIR/django"
#COVERAGE="coverage run --append --source $INSTALL_DIR/django"

## Base test command
TESTCMD="./manage.py test --settings=cohiva.settings_for_tests"

## Full test suite incl. migrations
$COVERAGE $TESTCMD 2>&1 | tee test.log

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
rm -rf $INSTALL_DIR/django-test/tests

#EOF
