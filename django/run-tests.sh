#!/usr/bin/bash

# exit on error
set -e

# if called from CI (GitHub Actions), copy the base_config_for_tests.py to base_config.py
#if [ -n "$GITHUB_ACTIONS" ] ; then
# This is done with setup.py in the workflow already...
#    touch cohiva/settings.py
#    cp cohiva/base_config_for_tests.py cohiva/base_config.py
#fi

## Show warnings?
export PYTHONWARNINGS=always

INSTALL_DIR=$(grep "^INSTALL_DIR = " cohiva/base_config.py | cut -d \" -f 2)

## Coverage options
#COVERAGE="true"  # Uncomment to enable coverage
COVERAGE_OPTS=()
#COVERAGE_OPTS=(--source "$INSTALL_DIR/django")
#COVERAGE_OPTS=(--append)
if [ -n "$GITHUB_ACTIONS" ] ; then
    #COVERAGE_OPTS=(--source "/cohiva/")
    cat <<EOT >.coveragerc
[run]
source = /cohiva/
relative_files = True
EOT

fi

if [ -n "$COVERAGE" ] ; then
    COVERAGE_CMD="coverage run ${COVERAGE_OPTS[*]}"
else
    COVERAGE_CMD=""
fi

## Base test command
TESTCMD="./manage.py test --settings=cohiva.settings_for_tests"

## Test options
TEST_OPTS=""
#TEST_OPTS="--keepdb" # Keep DB (don't run migrations)

## Select test to run (leave emtpy to run all tests)
SELECTED_TESTS=""
# Examples:
SELECTED_TESTS="finance.tests geno.tests.test_documents.DocumentSendTest.test_send_member_bill"

## Full test suite incl. migrations
# Run tests and capture the exit code of the test runner even though output is piped to tee.
# Temporarily disable 'set -e' so the script doesn't abort before we capture the exit code.
set +e
$COVERAGE_CMD $TESTCMD $TEST_OPTS $SELECTED_TESTS 2>&1 | tee test.log
TEST_EXIT_CODE=${PIPESTATUS[0]}
set -e

if [ -n "$COVERAGE_CMD" ] ; then
  if [ -n "$GITHUB_ACTIONS" ] ; then
    #coverage html 2>&1 | tee coverage.log
    # Copy the output to the mounted docker host file
    cp .coverage .coverage_output_for_github_action
  else
    coverage html 2>&1 | tee coverage.log
    #coverage report
  fi
fi

## Cleanup
## TODO: Move this cleanup step to a custom test runner, so it is integrated in
##       the ./manage.py test command, and tests also work when run from the
##       IDE, for example.
rm -rf "$INSTALL_DIR"/django-test/tests

# exit with the test runner's exit code so callers (CI, scripts) see the test result
exit "${TEST_EXIT_CODE:-0}"

#EOF
