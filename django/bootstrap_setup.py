#!/usr/bin/env python3
"""
Cohiva Bootstrap Setup Script (Python)
This script handles the main setup logic after Python has been selected.
"""

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


class ValidationError(Exception):
    """Custom exception for validation errors."""


def validate_path(path_str, path_type="path"):
    """
    Validate and sanitize a file system path.

    Args:
        path_str: Path string to validate
        path_type: Type of path for error messages (e.g., "venv", "install directory")

    Returns:
        Validated and resolved Path object

    Raises:
        ValidationError: If path is invalid or unsafe
    """
    if not path_str:
        raise ValidationError(f"{path_type} cannot be empty")

    # Check for null bytes (security)
    if "\0" in path_str:
        raise ValidationError(f"{path_type} contains invalid null byte")

    # Expand user home directory
    path = Path(path_str).expanduser()

    # Resolve to absolute path
    try:
        path = path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValidationError(f"Cannot resolve {path_type}: {e}")

    # Check for suspicious patterns
    path_str_normalized = str(path)
    suspicious_patterns = [
        r"/\.\./",  # Path traversal in middle
        r"^\.\.$",  # Just ".."
        r"/\.\.$",  # Ends with ".."
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, path_str_normalized):
            raise ValidationError(f"{path_type} contains suspicious pattern: {pattern}")

    # For venv and install directories, ensure they're in reasonable locations
    if path_type in ("venv", "install directory"):
        # Check it's not system directories
        system_dirs = ["/bin", "/sbin", "/usr", "/etc", "/var", "/sys", "/proc", "/dev"]
        for sys_dir in system_dirs:
            if path_str_normalized.startswith(sys_dir + "/") or path_str_normalized == sys_dir:
                raise ValidationError(f"{path_type} cannot be in system directory: {sys_dir}")

    return path


def validate_yes_no_input(response, default="n"):
    """
    Validate yes/no user input.

    Args:
        response: User input string
        default: Default value if empty ('y' or 'n')

    Returns:
        bool: True for yes, False for no
    """
    if not response:
        response = default

    response = response.strip().lower()

    # Accept various affirmative responses
    if response in ("y", "yes", "true", "1"):
        return True

    # Accept various negative responses
    if response in ("n", "no", "false", "0"):
        return False

    # Invalid input
    raise ValidationError(f"Invalid input: '{response}'. Please enter 'y' or 'n'")


def validate_python_path(python_path):
    """
    Validate Python executable path.

    Args:
        python_path: Path to Python executable

    Returns:
        Validated Path object

    Raises:
        ValidationError: If Python path is invalid
    """
    if not python_path:
        raise ValidationError("Python path cannot be empty")

    path = Path(python_path)

    # Check if file exists
    if not path.exists():
        raise ValidationError(f"Python executable not found: {python_path}")

    # Check if it's a file
    if not path.is_file():
        raise ValidationError(f"Python path is not a file: {python_path}")

    # Check if it's executable
    if not os.access(path, os.X_OK):
        raise ValidationError(f"Python path is not executable: {python_path}")

    # Try to run it to verify it's actually Python
    try:
        result = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise ValidationError(f"Cannot execute Python: {python_path}")

        # Check output contains "Python"
        output = result.stdout + result.stderr
        if "Python" not in output:
            raise ValidationError(f"Not a valid Python executable: {python_path}")

    except subprocess.TimeoutExpired:
        raise ValidationError(f"Python executable timed out: {python_path}")
    except Exception as e:
        raise ValidationError(f"Error validating Python executable: {e}")

    return path


def print_header(message):
    """Print a header message."""
    print()
    print(f"{Colors.BLUE}{'=' * 40}{Colors.NC}")
    print(f"{Colors.BLUE}{message}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 40}{Colors.NC}")
    print()


def print_info(message):
    """Print an info message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def print_warn(message):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def print_error(message):
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.NC} {message}")


def print_step(message):
    """Print a step message."""
    print(f"{Colors.BLUE}➜{Colors.NC} {message}")


def run_command(cmd, cwd=None, check=True, capture_output=False, env=None):
    """Run a shell command."""
    return subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True,
        env=env,
    )


def check_command_exists(cmd):
    """Check if a command exists in PATH."""
    result = run_command(
        ["which", cmd],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def check_brew_package(package):
    """Check if a Homebrew package is installed (macOS)."""
    result = run_command(
        ["brew", "list", package],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def check_apt_package(package):
    """Check if an apt package is installed (Linux)."""
    result = run_command(
        ["dpkg", "-l", package],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0 and "ii" in result.stdout


def check_system_dependencies():
    """Check for required system dependencies."""
    print_step("Checking system dependencies...")

    os_type = platform.system()
    missing_packages = []
    optional_missing = []

    if os_type == "Darwin":  # macOS
        print_info("Detected macOS - checking Homebrew packages...")

        # Check if Homebrew is installed
        if not check_command_exists("brew"):
            print_warn("Homebrew is not installed")
            print()
            print("Homebrew is recommended for managing dependencies on macOS.")
            print("Install from: https://brew.sh")
            print()
            print("Or run:")
            print(
                '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            )
            print()
            response = input("Continue without Homebrew? (y/N) ")
            try:
                if not validate_yes_no_input(response, default="n"):
                    sys.exit(1)
            except ValidationError as e:
                print_error(str(e))
                sys.exit(1)
            return

        # Required packages on macOS
        required = {
            "pkg-config": "pkg-config",
            "mariadb-connector-c": "mariadb-connector-c",
            "freetype": "freetype",
            "jpeg": "jpeg",
            "libffi": "libffi",
            "xmlsec1": "xmlsec1",
        }

        # Optional packages
        optional = {
            "poppler": "poppler (for PDF tests)",
            "libreoffice": "libreoffice (for document generation)",
        }

        for pkg, _name in required.items():
            if not check_brew_package(pkg):
                missing_packages.append(pkg)

        for pkg, description in optional.items():
            if not check_brew_package(pkg):
                optional_missing.append(f"{pkg} - {description}")

        if missing_packages or optional_missing:
            if missing_packages:
                print_warn(f"Missing required packages: {', '.join(missing_packages)}")
                print()
                print("Install with:")
                print(f"  brew install {' '.join(missing_packages)}")
                print()

            if optional_missing:
                print_warn("Missing optional packages:")
                for pkg in optional_missing:
                    print(f"  - {pkg}")
                print()
                print("Install optional packages with:")
                optional_names = [p.split(" - ")[0] for p in optional_missing]
                print(f"  brew install {' '.join(optional_names)}")
                print()

            if missing_packages:
                response = input("Install missing required packages now? (Y/n) ")
                try:
                    if validate_yes_no_input(response, default="y"):
                        print_step("Installing packages via Homebrew...")
                        try:
                            run_command(["brew", "install"] + missing_packages)
                            print_info("Packages installed successfully")
                        except subprocess.CalledProcessError:
                            print_error("Failed to install packages")
                            sys.exit(1)
                    else:
                        response = input("Continue without required packages? (y/N) ")
                        if not validate_yes_no_input(response, default="n"):
                            sys.exit(1)
                except ValidationError as e:
                    print_error(str(e))
                    sys.exit(1)
        else:
            print_info("All required system dependencies are installed")

    elif os_type == "Linux":  # Linux
        print_info("Detected Linux - checking system packages...")

        # Detect package manager
        has_apt = check_command_exists("apt")
        has_dnf = check_command_exists("dnf")
        has_pacman = check_command_exists("pacman")

        if not (has_apt or has_dnf or has_pacman):
            print_warn("Could not detect package manager (apt, dnf, or pacman)")
            print("Please install system dependencies manually.")
            return

        # Required packages (Debian/Ubuntu naming)
        required_apt = [
            "build-essential",
            "python3-dev",
            "python3-venv",
            "libmariadb-dev",  # or libmysqlclient-dev
            "libfreetype-dev",
            "libjpeg-dev",
            "libffi-dev",
            "xmlsec1",
        ]

        # Optional packages
        optional_apt = [
            "poppler-utils",  # for tests
            "libreoffice-writer",  # for PDF generation
        ]

        # Check locale
        locale_result = run_command(
            ["locale", "-a"],
            check=False,
            capture_output=True,
        )
        has_locale = "de_CH.utf8" in locale_result.stdout or "de_CH.UTF-8" in locale_result.stdout

        if has_apt:
            # Check which packages are missing
            for pkg in required_apt:
                if not check_apt_package(pkg):
                    # Try alternative for MySQL
                    if pkg == "libmariadb-dev" and check_apt_package("default-libmysqlclient-dev"):
                        continue
                    missing_packages.append(pkg)

            for pkg in optional_apt:
                if not check_apt_package(pkg):
                    optional_missing.append(pkg)

            if missing_packages or optional_missing or not has_locale:
                if missing_packages:
                    print_warn(f"Missing required packages: {', '.join(missing_packages)}")
                    print()
                    print("Install with:")
                    print("  sudo apt update")
                    print(f"  sudo apt install {' '.join(missing_packages)}")
                    print()

                if optional_missing:
                    print_warn(f"Missing optional packages: {', '.join(optional_missing)}")
                    print()
                    print("Install optional packages with:")
                    print(f"  sudo apt install {' '.join(optional_missing)}")
                    print()

                if not has_locale:
                    print_warn("Missing de_CH.UTF-8 locale")
                    print()
                    print("Install with:")
                    print("  sudo locale-gen de_CH.UTF-8")
                    print("  sudo update-locale")
                    print()

                if missing_packages:
                    print()
                    print("Note: You'll need sudo privileges to install system packages.")
                    print(
                        "The script cannot automatically install them on Linux for security reasons."
                    )
                    print()
                    response = input("Continue without required packages? (y/N) ")
                    try:
                        if not validate_yes_no_input(response, default="n"):
                            sys.exit(1)
                    except ValidationError as e:
                        print_error(str(e))
                        sys.exit(1)
            else:
                print_info("All required system dependencies are installed")

        elif has_dnf:
            print_warn("Detected Fedora/RHEL system")
            print()
            print("Install required packages with:")
            print("  sudo dnf install gcc gcc-c++ python3-devel")
            print("  sudo dnf install mariadb-connector-c-devel freetype-devel")
            print("  sudo dnf install libjpeg-devel libffi-devel xmlsec1")
            print()

        elif has_pacman:
            print_warn("Detected Arch Linux system")
            print()
            print("Install required packages with:")
            print("  sudo pacman -S base-devel python")
            print("  sudo pacman -S mariadb-libs freetype2 libjpeg libffi xmlsec")
            print()

    else:
        print_warn(f"Unsupported operating system: {os_type}")
        print("Please install system dependencies manually.")


def setup_venv(python_path, venv_path):
    """Create and setup virtual environment."""
    print_step("Setting up Python virtual environment...")

    # Validate paths
    try:
        python_path = validate_python_path(python_path)
        venv_path = validate_path(venv_path, "venv")
    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)

    if venv_path.exists():
        print_info(f"Virtual environment already exists at: {venv_path}")
    else:
        print_step(f"Creating virtual environment at: {venv_path}")
        run_command([str(python_path), "-m", "venv", str(venv_path)])
        print_info("Virtual environment created")

    return venv_path


def install_dependencies(venv_path):
    """Install Python dependencies."""
    print_step("Installing Python dependencies...")

    if not Path("install_dependencies.sh").exists():
        print_error("install_dependencies.sh not found. Are you in the django directory?")
        sys.exit(1)

    # Run install_dependencies.sh with the venv's Python
    # Pass --yes flag to auto-confirm pip-sync during automated setup
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    env["PATH"] = f"{venv_path / 'bin'}:{env['PATH']}"

    run_command(["./install_dependencies.sh", "--yes"], env=env)
    print_info("Dependencies installed")


def setup_config(install_dir, venv_path):
    """Setup configuration files."""
    print_step("Setting up configuration files...")

    # Validate install directory
    try:
        install_dir = validate_path(install_dir, "install directory")
    except ValidationError as e:
        print_error(str(e))
        sys.exit(1)

    python_path = venv_path / "bin" / "python"

    # Set up environment for venv
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    env["PATH"] = f"{venv_path / 'bin'}:{env['PATH']}"

    base_config = Path("cohiva/base_config.py")
    base_config_example = Path("cohiva/base_config_example.py")

    # Create install directory
    install_dir.mkdir(parents=True, exist_ok=True)

    # If base_config.py doesn't exist, create it from example
    if not base_config.exists() and base_config_example.exists():
        print_step("Creating base_config.py with custom INSTALL_DIR...")

        # Read example and replace INSTALL_DIR and generate SECRET
        content = base_config_example.read_text()
        content = content.replace(
            'INSTALL_DIR = "/var/www/cohiva"',
            f'INSTALL_DIR = "{install_dir}"',
        )

        # Generate random secret key
        # Import here to avoid Django dependency at module level
        result = run_command(
            [
                str(python_path),
                "-c",
                "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())",
            ],
            env=env,
            capture_output=True,
        )
        secret_key = result.stdout.strip()

        content = content.replace(
            'SITE_SECRET = "<SECRET>"',
            f'SITE_SECRET = "{secret_key}"',
        )

        # Write the updated config
        # NOTE: base_config.py is git-ignored (see .gitignore line 11), so this secret
        # is never committed to source control. This is the standard Django pattern for
        # local development. For production, use environment variables or secret managers.
        base_config.write_text(content)
        print_info(f"INSTALL_DIR set to: {install_dir}")
        print_info("Generated random SITE_SECRET (stored in git-ignored base_config.py)")

    # If base_config.py exists but has wrong INSTALL_DIR, update it
    elif base_config.exists():
        content = base_config.read_text()
        if 'INSTALL_DIR = "/var/www/cohiva"' in content:
            print_step("Updating INSTALL_DIR in existing base_config.py...")
            content = content.replace(
                'INSTALL_DIR = "/var/www/cohiva"',
                f'INSTALL_DIR = "{install_dir}"',
            )
            base_config.write_text(content)
            print_info(f"INSTALL_DIR updated to: {install_dir}")

    # Run setup.py to create directories and keys
    run_command([str(python_path), "setup.py"], env=env)

    # Uncomment CSRF/Session cookie settings for local development
    settings_file = Path("cohiva/settings.py")
    if settings_file.exists():
        content = settings_file.read_text()
        # Uncomment the CSRF and session cookie settings for local HTTP development
        content = content.replace(
            "# SESSION_COOKIE_SECURE = False", "SESSION_COOKIE_SECURE = False"
        )
        content = content.replace("# CSRF_COOKIE_SECURE = False", "CSRF_COOKIE_SECURE = False")
        settings_file.write_text(content)
        print_info("Enabled local development cookie settings (insecure cookies for HTTP)")

    # Uncomment CSRF/Session cookie settings for local development
    settings_file = Path('cohiva/settings.py')
    if settings_file.exists():
        content = settings_file.read_text()
        # Uncomment the CSRF and session cookie settings for local HTTP development
        content = content.replace(
            '# SESSION_COOKIE_SECURE = False',
            'SESSION_COOKIE_SECURE = False'
        )
        content = content.replace(
            '# CSRF_COOKIE_SECURE = False',
            'CSRF_COOKIE_SECURE = False'
        )
        settings_file.write_text(content)
        print_info("Enabled local development cookie settings (insecure cookies for HTTP)")

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env_example")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print_info("Created .env from .env_example")
        else:
            env_file.write_text("COHIVA_DEV_PORT=8000\n")
            print_info("Created .env file")

    print_info("Configuration complete")


def setup_auto_venv(venv_path):
    """Setup automatic venv activation files (optional)."""
    print_step("Setting up direnv for automatic venv activation...")
    print()
    print(
        "direnv can automatically activate your virtual environment when you enter the project directory."
    )
    print()

    response = input("Do you want to set up direnv auto-activation? (y/N) ")
    try:
        setup_direnv = validate_yes_no_input(response, default="n")
    except ValidationError as e:
        print_error(str(e))
        print_info("Skipping direnv setup")
        return

    if not setup_direnv:
        print_info("Skipping direnv setup")
        print_info("You can manually set up direnv later if needed")
        return

    venv_path = Path(venv_path).expanduser()

    # Create .venv-path file
    venv_path_file = Path(".venv-path")
    venv_path_file.write_text(
        f"# Virtual environment path for shell auto-activation\n{venv_path}\n"
    )
    print_info("Created .venv-path file")

    # Check if .envrc already exists
    envrc_file = Path(".envrc")
    if not envrc_file.exists():
        envrc_content = f'''# direnv configuration for Cohiva

# Activate virtual environment
if [ -d "{venv_path}" ]; then
    source "{venv_path}/bin/activate"
elif [ -d "$HOME/.venv/cohiva-dev" ]; then
    source "$HOME/.venv/cohiva-dev/bin/activate"
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Load .env file if it exists
dotenv_if_exists
'''
        envrc_file.write_text(envrc_content)
        print_info("Created .envrc file")
    else:
        print_info(".envrc file already exists")

    print_info(f"Auto-activation configured for: {venv_path}")
    print()
    print("Next steps:")
    print("  1. Install direnv: https://direnv.net/docs/installation.html")
    print("  2. Hook direnv into your shell: https://direnv.net/docs/hook.html")
    print("  3. Run: direnv allow")
    print()


def start_docker():
    """Start Docker services."""
    print_step("Starting Docker services (MariaDB, Redis)...")

    result = run_command(
        ["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d"],
        check=False,
    )

    if result.returncode != 0:
        print_error("Failed to start Docker services")
        print_warn("This might be due to:")
        print_warn("  - Docker Registry temporarily unavailable (503 error)")
        print_warn("  - Docker Desktop not running")
        print_warn("  - Network connectivity issues")
        print()
        print_info("You can start Docker services manually later with:")
        print_info("  docker compose -f docker-compose.dev.yml up -d")
        print()
        return False

    # Wait for database to be ready
    print_step("Waiting for database to be ready...")
    import time

    # First wait a bit for containers to start
    time.sleep(3)

    timeout = 60
    elapsed = 0
    db_ready = False

    while elapsed < timeout:
        # Test actual database connection
        result = run_command(
            [
                "docker",
                "exec",
                "cohiva-dev-mariadb",
                "mariadb",
                "-ucohiva",
                "-pc0H1v4",
                "-e",
                "SELECT 1;",
            ],
            capture_output=True,
            check=False,
        )

        if result.returncode == 0:
            db_ready = True
            break

        time.sleep(2)
        elapsed += 2
        print(".", end="", flush=True)

    print()

    if not db_ready:
        print_warn("Database may not be fully ready yet")
        print_info("You can check status with: docker compose -f docker-compose.dev.yml ps")
        print_info(
            "Or test connection: docker exec cohiva-dev-mariadb mariadb -ucohiva -pc0H1v4 -e 'SELECT 1;'"
        )
    else:
        print_info("Database is ready")

    return db_ready


def run_migrations(venv_path):
    """Run database migrations."""
    print_step("Running database migrations...")

    # Set up environment for venv
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    env["PATH"] = f"{venv_path / 'bin'}:{env['PATH']}"

    # Skip checks to avoid issues with admin checks before tables exist
    run_command(["./manage.py", "migrate", "--skip-checks"], env=env)
    print_info("Migrations complete")


def create_superuser(venv_path):
    """Create superuser account."""
    print_step("Creating superuser account...")
    print()

    # Ask if user wants demo credentials or custom ones
    print("Choose superuser creation method:")
    print("  1. Quick setup with demo credentials (username: demo, password: demo)")
    print("  2. Create custom superuser (interactive)")
    print()

    while True:
        choice = input("Select option [1-2, default: 1]: ").strip()

        # Default to option 1
        if not choice:
            choice = "1"

        if choice in ["1", "2"]:
            break
        print_error("Invalid choice. Please enter 1 or 2.")

    # Set up environment for venv
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    env["PATH"] = f"{venv_path / 'bin'}:{env['PATH']}"

    if choice == "1":
        # Create demo superuser non-interactively
        print()
        print_info("Creating superuser with demo credentials...")
        print_warn("IMPORTANT: Change these credentials in production!")
        print()

        env["DJANGO_SUPERUSER_USERNAME"] = "demo"
        env["DJANGO_SUPERUSER_EMAIL"] = "demo@example.com"
        env["DJANGO_SUPERUSER_PASSWORD"] = "demo"

        try:
            run_command(
                ["./manage.py", "createsuperuser", "--noinput"],
                env=env,
                capture_output=False
            )
            print()
            print_info("Demo superuser created successfully")
            print_info("  Username: demo")
            print_info("  Password: demo")
            print_warn("  Remember to change these credentials!")
        except subprocess.CalledProcessError:
            print_warn("Superuser creation failed (may already exist)")
    else:
        # Interactive superuser creation
        print()
        print("Please create an admin user for accessing the Cohiva admin interface:")
        run_command(["./manage.py", "createsuperuser"], env=env)


def load_demo_data(venv_path):
    """Load demo data into the database."""
    print_step("Loading demo data...")
    print()

    # Check if demo data exists
    demo_data_sql = Path("demo-data/demo-data.sql")
    if not demo_data_sql.exists():
        print_warn("Demo data file not found: demo-data/demo-data.sql")
        print_info("Skipping demo data loading")
        return False

    print("This will load sample data including:")
    print("  - Member accounts and contracts")
    print("  - Invoices and transactions")
    print("  - Reservation resources")
    print("  - Document templates")
    print()
    print_warn("This will overwrite existing data in the TEST database!")
    print()

    # Set up environment for venv
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    env["PATH"] = f"{venv_path / 'bin'}:{env['PATH']}"

    try:
        # Run demo_data_manager.py with --load and --force flags
        result = run_command(
            ["python", "scripts/demo_data_manager.py", "--load", "--force"],
            env=env,
            check=False,
        )

        if result.returncode != 0:
            print_error("Failed to load demo data")
            return False

        print_info("Demo data loaded successfully")
        print()

        # Run migrations to update schema to latest version
        # The demo data might have old table structures, so we need to apply any new migrations
        print_step("Applying latest migrations to demo data...")
        try:
            run_command(["./manage.py", "migrate", "--skip-checks"], env=env)
            print_info("Migrations applied successfully")
        except subprocess.CalledProcessError:
            print_warn("Some migrations failed - this can happen with data migrations")
            print_info("The database should still be usable. If you encounter issues, try:")
            print_info("  ./manage.py showmigrations  # Check migration status")
            print_info("  ./manage.py migrate --fake-initial  # Skip initial table creation")
            print_info("  ./manage.py migrate  # Try completing migrations")

        print()
        print_warn("Note: You'll need to create a superuser to access the admin interface")
        print_info("Run: ./manage.py createsuperuser")
        print()
        return True

    except Exception as e:
        print_error(f"Error loading demo data: {e}")
        return False


def print_success(venv_path, demo_data_loaded=False):
    """Print success message."""
    print_header("Setup Complete!")

    print("Your Cohiva development environment is ready!")
    print()
    print(f"{Colors.GREEN}Next steps:{Colors.NC}")
    print()
    print("  1. Activate the virtual environment (if not already active):")
    print(f"     {Colors.BLUE}source {venv_path}/bin/activate{Colors.NC}")
    print()
    print("  2. Start the development server:")
    print(f"     {Colors.BLUE}./develop.sh{Colors.NC}")
    print()
    print("  3. Access the admin interface at:")
    print(f"     {Colors.BLUE}http://localhost:8000/admin/{Colors.NC}")
    print()

    if demo_data_loaded:
        print(f"{Colors.GREEN}Demo data loaded!{Colors.NC}")
        print("  You can now explore the system with sample members, contracts, and invoices.")
        print()
        print(f"{Colors.YELLOW}⚠ Troubleshooting login issues:{Colors.NC}")
        print("  - Make sure you're using http://localhost:8000/admin/ (not /portal/)")
        print("  - Clear browser cookies if you still see CSRF errors")
        print("  - The dev server must be running for login to work")
        print()

    print(f"{Colors.YELLOW}Optional:{Colors.NC}")
    if not demo_data_loaded:
        print("  - Load demo data: ./scripts/demo_data_manager.py --load")
    print("  - Run tests: ./run-tests.sh")
    print()
    print(f"{Colors.GREEN}Quick commands:{Colors.NC}")
    print("  - Start dev server:  ./develop.sh")
    print("  - With Celery:       ./develop.sh --celery")
    print("  - Run tests:         ./run-tests.sh")
    print("  - Stop Docker:       docker compose -f docker-compose.dev.yml down")
    print()


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Cohiva development environment setup (Python)")
    parser.add_argument(
        "--python",
        required=True,
        help="Path to Python binary to use",
    )
    parser.add_argument(
        "--venv",
        default=os.path.expanduser("~/.venv/cohiva-dev"),
        help="Path for virtual environment",
    )
    parser.add_argument(
        "--install-dir",
        default=os.path.abspath("."),
        help="Path for Cohiva data directory (defaults to current directory)",
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip starting Docker services",
    )
    parser.add_argument(
        "--skip-superuser",
        action="store_true",
        help="Skip creating superuser",
    )
    parser.add_argument(
        "--load-demo-data",
        action="store_true",
        help="Load demo data after setup",
    )

    args = parser.parse_args()

    print_header("Cohiva Development Environment Setup")

    # Check system dependencies
    check_system_dependencies()

    # Setup virtual environment
    venv_path = setup_venv(args.python, args.venv)

    # Install dependencies
    install_dependencies(venv_path)

    # Setup configuration
    setup_config(args.install_dir, venv_path)

    # Setup auto-activation
    setup_auto_venv(venv_path)

    # Start Docker (but defer migrations until we know if demo data will be loaded)
    docker_started = False
    if not args.skip_docker:
        docker_started = start_docker()
        if not docker_started:
            print_warn("Docker services not started - skipping database setup")
            print_info("Start Docker manually and run migrations:")
            print_info("  docker compose -f docker-compose.dev.yml up -d")
            print_info("  ./manage.py migrate")

    # Load demo data or run migrations + create superuser (only if Docker started successfully)
    demo_data_loaded = False
    if args.skip_docker or docker_started:
        # Check if demo data should be loaded
        load_demo = args.load_demo_data

        # If not specified via flag, ask interactively (only if demo data exists)
        if not load_demo and not args.skip_superuser:
            demo_data_sql = Path("demo-data/demo-data.sql")
            if demo_data_sql.exists():
                print()
                response = input("Do you want to load demo data now? (y/N) ")
                try:
                    load_demo = validate_yes_no_input(response, default="n")
                except ValidationError as e:
                    print_error(str(e))
                    load_demo = False

        # Load demo data if requested (migrations are run inside load_demo_data)
        if load_demo:
            demo_data_loaded = load_demo_data(venv_path)

            # If demo data was loaded, we still need to create superuser
            if demo_data_loaded and not args.skip_superuser:
                print()
                response = input("Do you want to create a superuser now? (Y/n) ")
                try:
                    if validate_yes_no_input(response, default="y"):
                        create_superuser(venv_path)
                except ValidationError as e:
                    print_error(str(e))
                    print_warn("Skipping superuser creation")

        # If demo data NOT loaded, run regular migrations first, then offer superuser
        else:
            # Run migrations on empty database
            if docker_started:
                run_migrations(venv_path)

            if not args.skip_superuser:
                print()
                response = input("Do you want to create a superuser now? (Y/n) ")
                try:
                    if validate_yes_no_input(response, default="y"):
                        create_superuser(venv_path)
                except ValidationError as e:
                    print_error(str(e))
                    print_warn("Skipping superuser creation")
    elif not args.skip_superuser and not docker_started:
        print_warn("Skipping superuser creation (database not available)")
        print_info("Create superuser manually after starting Docker:")
        print_info("  ./manage.py createsuperuser")

    # Print success message
    print_success(venv_path, demo_data_loaded)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBootstrap cancelled by user.")
        sys.exit(130)  # Standard exit code for SIGINT
