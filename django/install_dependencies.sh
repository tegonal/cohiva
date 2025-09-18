#!/bin/sh

set -e

ENVIRONMENT="local"
PIP_ROOT_USER_MODE=""
PIP_SYNC_ASK="--ask"

# parse arguments for environment (-e or --environment) and service name (-s or --service)
while [ "$#" -gt 0 ]; do
    case $1 in
        -e|--environment) ENVIRONMENT="$2"; shift ;;
        *) ;;
    esac
    shift
done

echo '$ENVIRONMENT' is set to $ENVIRONMENT

## Make sure we are in a virtual env
if [ $VIRTUAL_ENV ] ; then
    echo "Checking/installing dependencies in virtual environment '$VIRTUAL_ENV'..."
else
  if [ "$ENVIRONMENT" = "docker" ]; then
    echo "Checking/installing dependencies on native environment since we are in docker mode..."
    PIP_ROOT_USER_MODE="ignore"
    PIP_SYNC_ASK=""
  else
    echo "Is seems that no Python virtual environment is active."
    echo "Please create and activate a virtual environment first. (see README.md)"
    exit
  fi
fi

## Temporary workaround because of issue in celery (invalid metadata) => not needed anymore(?)
#pip install "pip<24.1"

## Handle legacy Python versions
REQUIREMENTS="requirements.txt"
PYTHON_VERSION=`python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"`
if [ -e ./requirements_legacy_python${PYTHON_VERSION}.txt ] ; then
    echo "Using legacy requirements file for Python ${PYTHON_VERSION}"
    REQUIREMENTS="requirements_legacy_python${PYTHON_VERSION}.txt"
fi

## Make sure we have pip-sync
export PIP_ROOT_USER_ACTION=$PIP_ROOT_USER_MODE
set -x
command -v pip-sync >/dev/null 2>&1 || pip install pip-tools

## Install patched version of python-sepa and make sure it is in requirements.txt to prevent uninstallation when running pip-sync
if [ "$ENVIRONMENT" != "docker" && ! -e ./geno/python-sepa/.git ] ; then
    echo "Initializing git submodule python-sepa"
    git submodule update --init geno/python-sepa
fi
( cd geno/python-sepa && python3 setup.py build install )
grep "^sepa==" $REQUIREMENTS >/dev/null || echo "sepa==0.5.3+mst1" >> $REQUIREMENTS

## Sync virtual environment with requirements.txt

pip-sync $PIP_SYNC_ASK $REQUIREMENTS

## Apply patches to site packages in virtual environment
INSTALLPATH=`pip show djangosaml2idp | grep ^Location: | cut -c 11-`
patch --backup --forward --reject-file - $INSTALLPATH/djangosaml2idp/models.py cohiva/saml2/djangosaml2idp_models.py.patch
patch --backup --forward --reject-file - $INSTALLPATH/djangosaml2idp/views.py cohiva/saml2/djangosaml2idp_views.py.patch
