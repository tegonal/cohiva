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

## Make sure we have pip-sync
command -v pip-sync >/dev/null 2>&1 || pip install pip-tools

## Install patched version of python-sepa and make sure it is in requirements.txt to prevent uninstallation when running pip-sync
if [ ! -e ./geno/python-sepa/.git ] ; then
    echo "Initializing git submodule python-sepa"
    git submodule update --init geno/python-sepa
fi
( cd geno/python-sepa && python3 setup.py build install )
grep "^sepa==" requirements.txt >/dev/null || echo "sepa==0.5.3+mst1" >> requirements.txt

## Sync virtual environment with requirements.txt
pip-sync -a

## Apply patches to site packages in virtual environment
INSTALLPATH=`pip show djangosaml2idp | grep ^Location: | cut -c 11-`
patch --backup --forward --reject-file - $INSTALLPATH/djangosaml2idp/models.py cohiva/saml2/djangosaml2idp_models.py.patch
patch --backup --forward --reject-file - $INSTALLPATH/djangosaml2idp/views.py cohiva/saml2/djangosaml2idp_views.py.patch
