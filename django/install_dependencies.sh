#!/bin/sh

## Make sure we are in a virtual env
if [ $VIRTUAL_ENV ] ; then
    echo "Checking/installing dependencies in virtual environment '$VIRTUAL_ENV'..."
else
    echo "Is seems that no Python virtual environment is active."
    echo "Please create and activate a virtual environment first. (see README.md)"
    exit
fi

## Temporary workaround because of issue in celery (invalid metadata) => not needed anymore(?)
#pip install "pip<24.1"

## Handle legacy Python versions
REQUIREMENTS="requirements.txt"
PYTHON_VERSION=`python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"`
if [ -z "$PYTHON_VERSION" ] ; then
    echo "ERROR: Can't determine Python version."
    exit
fi
if [ -e ./requirements_legacy_python${PYTHON_VERSION}.txt ] ; then
    echo "Using legacy requirements file for Python ${PYTHON_VERSION}"
    REQUIREMENTS="requirements_legacy_python${PYTHON_VERSION}.txt"
fi

## Make sure we have pip-sync
command -v pip-sync >/dev/null 2>&1 || pip install pip-tools

## Uninstall old patched versions of python-sepa
SITE_PACKAGES=`python -c "import site; print(site.getsitepackages()[0])"`
if [ "$SITE_PACKAGES" ] ; then
    find $SITE_PACKAGES -name "sepa-0.5.[1-3]+mst[1-9]-*.egg" -printf "Removing %p\n"
    find $SITE_PACKAGES -name "sepa-0.5.[1-3]+mst[1-9]-*.egg" | xargs rm -rf
fi

## Install patched version of python-sepa and make sure it is in requirements.txt to prevent uninstallation when running pip-sync
if [ ! -e ./geno/python-sepa/.git ] ; then
    echo "Initializing git submodule python-sepa"
    git submodule update --init geno/python-sepa
else
    git submodule update geno/python-sepa
fi
echo "Installing python-sepa from submodule"
( cd geno/python-sepa && python3 setup.py build install )
grep "^sepa==" $REQUIREMENTS >/dev/null || printf "\n# Packages added/managed by install_dependencies.sh:\nsepa==0.5.4+mst1\n" >> $REQUIREMENTS

## Sync virtual environment with requirements.txt
pip-sync -a $REQUIREMENTS

## Apply patches to site packages in virtual environment
INSTALLPATH=`pip show djangosaml2idp | grep ^Location: | cut -c 11-`
patch --backup --forward --reject-file - $INSTALLPATH/djangosaml2idp/models.py cohiva/saml2/djangosaml2idp_models.py.patch
patch --backup --forward --reject-file - $INSTALLPATH/djangosaml2idp/views.py cohiva/saml2/djangosaml2idp_views.py.patch
