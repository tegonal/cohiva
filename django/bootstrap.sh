#!/bin/bash
#
# Cohiva Development Environment Bootstrap Script
# This script automates the setup of a local development environment
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_VENV_PATH="$HOME/.venv/cohiva-dev"
DEFAULT_INSTALL_DIR="$HOME/cohiva-dev-data"

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_step() {
    echo -e "${BLUE}➜${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_info "Detected OS: $OS"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker
check_docker() {
    print_step "Checking Docker..."
    if ! command_exists docker; then
        print_error "Docker is not installed"
        echo "Please install Docker:"
        if [ "$OS" = "macos" ]; then
            echo "  brew install --cask docker"
            echo "  Or download from: https://www.docker.com/products/docker-desktop"
        else
            echo "  Visit: https://docs.docker.com/engine/install/"
        fi
        exit 1
    fi

    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is installed but not running"
        echo "Please start Docker and run this script again"
        exit 1
    fi

    print_info "Docker is installed and running"
}

# Find all available Python binaries
find_python_binaries() {
    print_step "Searching for Python installations..."

    PYTHON_BINARIES=()
    PYTHON_VERSIONS=()
    PYTHON_PATHS=()

    local candidates=()

    # Search for python binaries in PATH
    while IFS= read -r line; do
        candidates+=("$line")
    done < <(compgen -c | grep -E '^python[0-9.]*$' | sort -u)

    # Additional search paths for Homebrew on macOS
    if [ "$OS" = "macos" ]; then
        # Apple Silicon - search for all python@ directories
        if [ -d "/opt/homebrew/opt" ]; then
            while IFS= read -r dir; do
                local bin_path="${dir}/bin"
                if [ -d "$bin_path" ]; then
                    for py_bin in "$bin_path"/python*; do
                        if [ -f "$py_bin" ] && [ -x "$py_bin" ]; then
                            candidates+=("$py_bin")
                        fi
                    done
                fi
            done < <(find /opt/homebrew/opt -maxdepth 1 -type d -name 'python@*' 2>/dev/null)
        fi

        # Intel - search for all python@ directories
        if [ -d "/usr/local/opt" ]; then
            while IFS= read -r dir; do
                local bin_path="${dir}/bin"
                if [ -d "$bin_path" ]; then
                    for py_bin in "$bin_path"/python*; do
                        if [ -f "$py_bin" ] && [ -x "$py_bin" ]; then
                            candidates+=("$py_bin")
                        fi
                    done
                fi
            done < <(find /usr/local/opt -maxdepth 1 -type d -name 'python@*' 2>/dev/null)
        fi
    fi

    # Additional common locations on Linux
    if [ "$OS" = "linux" ]; then
        for dir in /usr/bin /usr/local/bin; do
            if [ -d "$dir" ]; then
                for py_bin in "$dir"/python*; do
                    if [ -f "$py_bin" ] && [ -x "$py_bin" ]; then
                        candidates+=("$(basename "$py_bin")")
                    fi
                done
            fi
        done
    fi

    # Process each candidate
    local seen_paths=()
    for cmd in "${candidates[@]}"; do
        # Skip non-executable or non-existent commands
        if ! command_exists "$cmd" && [ ! -f "$cmd" ]; then
            continue
        fi

        # Get full path
        if [ -f "$cmd" ] && [[ "$cmd" == /* ]]; then
            local full_path="$cmd"
        else
            local full_path=$(command -v "$cmd" 2>/dev/null)
            if [ -z "$full_path" ]; then
                continue
            fi
        fi

        # Resolve symlinks to get actual binary (cross-platform)
        if [ -L "$full_path" ]; then
            # Use Python to resolve symlinks (works on both macOS and Linux)
            local resolved_path=$(python3 -c "import os; print(os.path.realpath('$full_path'))" 2>/dev/null || \
                                  python -c "import os; print(os.path.realpath('$full_path'))" 2>/dev/null)
            if [ -n "$resolved_path" ] && [ -f "$resolved_path" ]; then
                full_path="$resolved_path"
            fi
        fi

        # Skip if already added (deduplicate by resolved path)
        local already_added=false
        for seen in "${seen_paths[@]}"; do
            if [ "$full_path" = "$seen" ]; then
                already_added=true
                break
            fi
        done

        if [ "$already_added" = true ]; then
            continue
        fi

        # Get version
        local version=$("$full_path" -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')" 2>/dev/null)
        if [ -z "$version" ]; then
            continue
        fi

        # Parse version
        local major=$(echo "$version" | cut -d. -f1)
        local minor=$(echo "$version" | cut -d. -f2)

        # Only include Python 3.x
        if [ "$major" -eq 3 ]; then
            PYTHON_BINARIES+=("$cmd")
            PYTHON_VERSIONS+=("$version")
            PYTHON_PATHS+=("$full_path")
            seen_paths+=("$full_path")
        fi
    done

    if [ ${#PYTHON_BINARIES[@]} -eq 0 ]; then
        print_error "No Python 3.x installation found"
        if [ "$OS" = "macos" ]; then
            echo "Install with: brew install python@3.11"
        else
            echo "Install with: sudo apt install python3.11 python3.11-venv python3.11-dev"
        fi
        exit 1
    fi

    print_info "Found ${#PYTHON_BINARIES[@]} Python installation(s)"
}

# Let user select Python version
select_python() {
    print_step "Available Python installations:"
    echo ""

    local valid_options=()
    local recommended_idx=-1

    for i in "${!PYTHON_BINARIES[@]}"; do
        local version="${PYTHON_VERSIONS[$i]}"
        local binary="${PYTHON_BINARIES[$i]}"
        local path="${PYTHON_PATHS[$i]}"

        local major=$(echo "$version" | cut -d. -f1)
        local minor=$(echo "$version" | cut -d. -f2)

        local status=""
        local is_valid=false

        if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; then
            status="${GREEN}✓ Supported${NC}"
            is_valid=true
            valid_options+=("$i")
            if [ $recommended_idx -eq -1 ]; then
                recommended_idx=$i
                status="${GREEN}✓ Recommended${NC}"
            fi
        else
            status="${YELLOW}⚠ Too old (Python 3.11+ required)${NC}"
        fi

        local num=$((i + 1))
        echo -e "  ${BLUE}[$num]${NC} Python $version - $binary"
        echo -e "      Path: $path"
        echo -e "      Status: $status"
        echo ""
    done

    if [ ${#valid_options[@]} -eq 0 ]; then
        print_error "No Python 3.11+ installation found"
        if [ "$OS" = "macos" ]; then
            echo "Install with: brew install python@3.11"
        else
            echo "Install with: sudo apt install python3.11 python3.11-venv python3.11-dev"
        fi
        exit 1
    fi

    # Auto-select if only one valid option
    if [ ${#valid_options[@]} -eq 1 ]; then
        local idx="${valid_options[0]}"
        SELECTED_PYTHON="${PYTHON_PATHS[$idx]}"
        PYTHON_VERSION="${PYTHON_VERSIONS[$idx]}"
        print_info "Auto-selected Python ${PYTHON_VERSION}: $SELECTED_PYTHON"
        return
    fi

    # Ask user to select
    local recommended_num=$((recommended_idx + 1))
    echo -e "Select Python version to use ${BLUE}[default: $recommended_num]${NC}:"
    read -p "> " selection

    # Use default if empty
    if [ -z "$selection" ]; then
        selection=$recommended_num
    fi

    # Validate selection
    local idx=$((selection - 1))
    if [ "$idx" -lt 0 ] || [ "$idx" -ge ${#PYTHON_BINARIES[@]} ]; then
        print_error "Invalid selection"
        exit 1
    fi

    # Check if selected version is valid
    local selected_version="${PYTHON_VERSIONS[$idx]}"
    local major=$(echo "$selected_version" | cut -d. -f1)
    local minor=$(echo "$selected_version" | cut -d. -f2)

    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 11 ]; }; then
        print_error "Python 3.11+ is required, but you selected $selected_version"
        exit 1
    fi

    SELECTED_PYTHON="${PYTHON_PATHS[$idx]}"
    PYTHON_VERSION="${PYTHON_VERSIONS[$idx]}"
    print_info "Selected Python ${PYTHON_VERSION}: $SELECTED_PYTHON"
}


# Main execution
main() {
    print_header "Cohiva Development Environment Bootstrap"

    echo "This script will set up your local Cohiva development environment."
    echo ""

    # Parse arguments
    VENV_PATH=""
    INSTALL_DIR=""
    SKIP_DOCKER=false
    SKIP_SUPERUSER=false
    LOAD_DEMO_DATA=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --venv)
                VENV_PATH="$2"
                shift 2
                ;;
            --install-dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-superuser)
                SKIP_SUPERUSER=true
                shift
                ;;
            --load-demo-data)
                LOAD_DEMO_DATA=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --venv PATH          Path for virtual environment (default: $DEFAULT_VENV_PATH)"
                echo "  --install-dir PATH   Path for Cohiva data directory (default: $DEFAULT_INSTALL_DIR)"
                echo "  --skip-docker        Skip starting Docker services"
                echo "  --skip-superuser     Skip creating superuser"
                echo "  --load-demo-data     Load demo data after setup"
                echo "  --help               Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Set defaults if not provided
    if [ -z "$VENV_PATH" ]; then
        VENV_PATH="$DEFAULT_VENV_PATH"
    fi

    if [ -z "$INSTALL_DIR" ]; then
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
    fi

    # Run initial checks
    detect_os

    if [ "$SKIP_DOCKER" = false ]; then
        check_docker
    fi

    # Find and select Python
    find_python_binaries
    select_python

    echo ""
    print_info "Delegating to Python setup script..."
    echo ""

    # Build arguments for Python script
    PYTHON_ARGS=(
        "--python" "$SELECTED_PYTHON"
        "--venv" "$VENV_PATH"
        "--install-dir" "$INSTALL_DIR"
    )

    if [ "$SKIP_DOCKER" = true ]; then
        PYTHON_ARGS+=("--skip-docker")
    fi

    if [ "$SKIP_SUPERUSER" = true ]; then
        PYTHON_ARGS+=("--skip-superuser")
    fi

    if [ "$LOAD_DEMO_DATA" = true ]; then
        PYTHON_ARGS+=("--load-demo-data")
    fi

    # Execute Python setup script
    exec "$SELECTED_PYTHON" bootstrap_setup.py "${PYTHON_ARGS[@]}"
}

# Run main
main "$@"
