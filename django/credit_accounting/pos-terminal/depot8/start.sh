#!/bin/sh

# Required system site packages:
# aptitude install python3-tk python3-requests python3-tz

VENV_DIR="venv"

if [ ! -e "$VENV_DIR" ] ; then
    echo "Creating virtual environment in ${VENV_DIR}..."
    python3 -m venv "$VENV_DIR"
fi

. ${VENV_DIR}/bin/activate

MARKER_FILE=${VENV_DIR}/update_ts_marker
if [ ! -e $MARKER_FILE -o venv-requirements.txt -nt $MARKER_FILE ] ; then
    echo "Installing additional packages from venv-requirements.txt..."
    pip install -r venv-requirements.txt
    touch $MARKER_FILE
fi

./depotpos.py

deactivate

#EOF
