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
INSTALL_PY_ARGS=()
for arg in "$@"; do
    case $arg in
        -y|--yes)
            INSTALL_PY_ARGS+=("--yes")
            ;;
        -e|--environment)
            shift
            INSTALL_PY_ARGS+=("--environment" "$1")
            ;;
        *)
            INSTALL_PY_ARGS+=("$arg")
            ;;
    esac
    shift || true
done

# Execute the Python installation script with all arguments passed through
exec $PYTHON_CMD install.py "${INSTALL_PY_ARGS[@]}"
