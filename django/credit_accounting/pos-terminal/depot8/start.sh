#!/bin/sh

# Required system site packages:
# aptitude install python3-tk python3-requests python3-tz

INSTALL_REQUIREMENTS=0
if [ ! -e "venv" ] ; then
    echo "Creating virtual environment in venv..."
    python3 -m venv venv --system-site-packages
    INSTALL_REQUIREMENTS=1
fi

. venv/bin/activate

if [ $INSTALL_REQUIREMENTS -eq 1 ] ; then
    echo "Installing additional packages from venv-requirements.txt..."
    pip install -r venv-requirements.txt
fi

./depotpos.py

deactivate

#EOF
