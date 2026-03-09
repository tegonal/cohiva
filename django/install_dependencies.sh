#!/bin/sh

set -e

# Check if Python 3.11 or higher is available
echo "Checking Python version..."

# Try to find python3 or python command
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "ERROR: Neither python3 nor python command found."
    echo "Please install Python 3.11 or higher."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info[0])")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info[1])")

echo "Found Python $PYTHON_VERSION"

# Check if version is >= 3.11
if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo "ERROR: Python 3.11 or higher is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "Python version check passed (>= 3.11)"
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
