#!/bin/sh

set -e

# Check if correct Python version is available
echo "Checking Python version..."
REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR_MIN=11
REQUIRED_PYTHON_MINOR_MAX=13
REQUIRED_PYTHON_VERSION="${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR_MIN} - ${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR_MAX}"

# Try to find python3 or python command
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "ERROR: Neither python3 nor python command found."
    echo "Please install Python ${REQUIRED_PYTHON_VERSION}."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info[0])")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info[1])")

echo "Found Python $PYTHON_VERSION"

# Check if version is supported
if [ "$PYTHON_MAJOR" -ne "$REQUIRED_PYTHON_MAJOR" ] || { [ "$PYTHON_MAJOR" -eq "$REQUIRED_PYTHON_MAJOR" ] && [ "$PYTHON_MINOR" -lt "$REQUIRED_PYTHON_MINOR_MIN" ]; } || { [ "$PYTHON_MAJOR" -eq "$REQUIRED_PYTHON_MAJOR" ] && [ "$PYTHON_MINOR" -gt "$REQUIRED_PYTHON_MINOR_MAX" ]; }; then
    echo "ERROR: Python ${REQUIRED_PYTHON_VERSION} is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "Python version check passed (${REQUIRED_PYTHON_VERSION})"
echo "Running install.py..."
echo ""

# Parse arguments to handle --yes flag
# POSIX-compatible argument parsing (no arrays)
quote_arg() {
    # Escape single quotes in the argument and wrap in single quotes
    printf "'%s'" "$(printf "%s" "$1" | sed "s/'/'\\\\''/g")"
}

NEW_ARGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -y|--yes)
            NEW_ARGS="${NEW_ARGS:+$NEW_ARGS }$(quote_arg --yes)"
            shift
            ;;
        -e|--environment)
            shift
            if [ "$#" -eq 0 ]; then
                echo "ERROR: --environment requires a value." >&2
                exit 1
            fi
            NEW_ARGS="${NEW_ARGS:+$NEW_ARGS }$(quote_arg --environment) $(quote_arg "$1")"
            shift
            ;;
        *)
            NEW_ARGS="${NEW_ARGS:+$NEW_ARGS }$(quote_arg "$1")"
            shift
            ;;
    esac
done

# Rebuild positional parameters from the quoted list
if [ -n "$NEW_ARGS" ]; then
    eval "set -- $NEW_ARGS"
else
    set --
fi

exec "$PYTHON_CMD" install.py "$@"
