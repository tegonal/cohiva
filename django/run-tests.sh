#!/usr/bin/bash

# exit on error
set -e

## Uncomment to enable coverage
#COVERAGE="true"

## Show warnings?
export PYTHONWARNINGS=always

INSTALL_DIR=$(grep "^INSTALL_DIR = " cohiva/base_config.py | cut -d \" -f 2)

## Normalize flags
case "${COVERAGE,,}" in
  true|1|yes|on)
    COVERAGE="true"
    ;;
  *)
    COVERAGE="false"
    ;;
esac
case "${GITHUB_ACTIONS,,}" in
  true|1|yes|on)
    GITHUB_ACTIONS="true"
    ;;
  *)
    GITHUB_ACTIONS="false"
    ;;
esac
case "${SKIP_SLOW,,}" in
  true|1|yes|on)
    SKIP_SLOW="true"
    ;;
  *)
    SKIP_SLOW="false"
    ;;
esac

## Coverage options
COVERAGE_OPTS=()
#COVERAGE_OPTS=(--source "$INSTALL_DIR/django")
#COVERAGE_OPTS=(--append)

if [ "$COVERAGE" = "true" ] ; then
    COVERAGE_CMD="coverage run ${COVERAGE_OPTS[*]}"
else
    COVERAGE_CMD=""
fi

## Base test command
TESTCMD="./manage.py test --settings=cohiva.settings_for_tests"
if [ "$SKIP_SLOW" = "true" ] ; then
    TESTCMD="${TESTCMD} --exclude-tag=slow-test"
    export PYTHONDONTWRITEBYTECODE=1
    export SKIP_SLOW="true"
fi

## Test options
TEST_OPTS=""
#TEST_OPTS="--keepdb" # Keep DB (don't run migrations)

## Select test to run (leave emtpy to run all tests)
SELECTED_TESTS=""
# Examples:
#SELECTED_TESTS="cohiva.tests credit_accounting.tests finance.tests geno.tests importer.tests portal.tests report.tests reservation.tests"
#SELECTED_TESTS="geno.tests.test_models.AddressTest finance.tests.test_accounting.TransactionTestCase.test_strings"

## Full test suite incl. migrations
# Run tests and capture the exit code of the test runner even though output is piped to tee.
# Temporarily disable 'set -e' so the script doesn't abort before we capture the exit code.
set +e
$COVERAGE_CMD $TESTCMD $TEST_OPTS $SELECTED_TESTS 2>&1 | tee test.log
TEST_EXIT_CODE=${PIPESTATUS[0]}
set -e

if [ -n "$COVERAGE_CMD" ] ; then
  if [ "$GITHUB_ACTIONS" = "true" ] ; then
    # Copy the output to the mounted docker host file because
    # coverage can't use the mounted file directly in the container.
    cp .coverage .coverage_output_for_github_action
    #coverage html 2>&1 | tee coverage.log
  else
    #coverage report
    coverage html 2>&1 | tee coverage.log
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
