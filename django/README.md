# Installation

## Quick Start (Recommended)

**Modern development setup using Docker for services (MariaDB, Redis).**

### Prerequisites

Install Docker and Python 3.11+:

**macOS:**
```bash
brew install python@3.11
brew install --cask docker  # Or download Docker Desktop from docker.com
```

**Linux (Ubuntu/Debian):**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER  # Add yourself to docker group
newgrp docker  # Activate group (or logout/login)

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### Setup

```bash
# Clone and navigate to the project
git clone https://github.com/tegonal/cohiva.git
cd cohiva/django

# Run the bootstrap script (automated setup)
./bootstrap.sh

# Start the development server
./develop.sh
```

The bootstrap script will:
- ✅ Check all prerequisites (Python 3.11+, Docker, system packages)
- ✅ **Detect and offer to install missing system packages** (Homebrew on macOS, apt on Linux)
- ✅ Check for required locale (de_CH.UTF-8)
- ✅ Create and activate a Python virtual environment
- ✅ Install all Python dependencies
- ✅ Generate configuration files with sensible defaults
- ✅ Start Docker services (MariaDB, Redis)
- ✅ Run database migrations
- ✅ Guide you through creating a superuser account

**Development data location:** All development data (logs, media files, etc.) is stored in `django-test/` within the project directory. This is automatically created and is git-ignored.

**Access the application:** http://localhost:8000/admin/

**Next steps:**
- **Tip:** Install [direnv](https://direnv.net/) to automatically activate your venv when entering the project directory
- See [Development Workflow](#development-workflow) below for daily commands

**Clean up:**
If you need to start fresh and remove all bootstrap-generated files:
```bash
./clean.sh              # Interactive cleanup with confirmation
./clean.sh --force      # Skip confirmation prompt
./clean.sh --keep-venv  # Keep the virtual environment
```

---

## Manual Installation

**Note:** The Quick Start above is the recommended approach for development. Manual installation is primarily for production deployments or environments where Docker is not available.

If you need to set up step-by-step or are preparing a production deployment, follow the sections below.

## Install required system packages

Example for Debian 11 (should work on most Debian/Ubuntu based systems):

    sudo apt install build-essential
    sudo apt install python3-dev
    sudo apt install python3-venv
    sudo apt install libmariadb-dev   ## or default-libmysqlclient-dev
    sudo apt install libfreetype-dev
    sudo apt install libjpeg-dev
    sudo apt install libffi-dev
    sudo apt install xmlsec1          ## for SAML 2.0 IDP
    sudo apt install poppler-utils    ## (optional, for tests)
    sudo apt install libreoffice-writer   ## (optional, for PDF generation)

**Note:** If using Docker for development (recommended), you don't need `redis-server` or `mariadb-server` system packages. The bootstrap script automatically detects and offers to install required packages on macOS.

If you get errors when installing Python packages, you might need additional packages such as `libxml2-dev`.

## Install locale

Cohiva currently expects the `de_CH.UTF-8` locale to be installed. On a Debian/Ubuntu based system you can install it with the following commands, if it's missing:

    sudo locale-gen de_CH.UTF-8
    sudo update-locale

## Setup Python environment

**Requirements:** Python 3.11 or higher is required.

### macOS with Homebrew

If you're using macOS with Homebrew, you can install Python 3.11:

    # Install Python 3.11
    brew install python@3.11

    # Create virtual environment using Python 3.11
    /opt/homebrew/opt/python@3.11/bin/python3.11 -m venv ~/.venv/cohiva-demo-prod
    # For Intel Macs, use: /usr/local/opt/python@3.11/bin/python3.11 -m venv ~/.venv/cohiva-demo-prod

    # Activate the virtual environment
    source ~/.venv/cohiva-demo-prod/bin/activate

    # Verify Python version
    python --version  # Should show Python 3.11.x

### Linux / Standard Setup

Example for project `cohiva-demo`:

    ## Checkout Cohiva code
    mkdir -p /var/www/cohiva-demo
    cd /var/www/cohiva-demo
    git clone https://github.com/tegonal/cohiva.git .

    ## Change to django directory
    cd django

    ## Create and activate virtual environment with Python 3.11+
    python3 -m venv ~/.venv/cohiva-demo-prod
    source ~/.venv/cohiva-demo-prod/bin/activate

    ## Verify Python version (must be >= 3.11)
    python --version

    ## Install dependencies
    ./install_dependencies.sh

The `install_dependencies.sh` script will:
- Automatically check for Python 3.11 or higher
- Execute the Python-based installation script (`install.py`)
- Install pip-tools if not already available
- Synchronize dependencies using pip-sync
- Install the patched python-sepa package from the git submodule
- Apply necessary patches to installed packages

For Docker environments, use:

    ./install_dependencies.sh --environment docker

## Database Setup

### For Development: Docker Compose (Standard)

**If you used the Quick Start, this is already done!** The `./bootstrap.sh` and `./develop.sh` scripts handle this automatically.

For manual control:

    # Start MariaDB and Redis with Docker Compose
    docker compose -f docker-compose.dev.yml up -d

    # Stop services
    docker compose -f docker-compose.dev.yml down

This automatically provides:
- MariaDB server with database `cohiva_django_test` (user: `cohiva`, password: `c0H1v4`)
- Test database `test_cohiva_django_test` for automated tests
- Redis server for Celery (on port 6379)

### For Production: Manual Database Setup

**This section is for production deployments only.**

- Install a MariaDB/MySQL server (e.g. `sudo apt install mariadb-server`)
- Create a MariaDB/MySQL user and database
- For production, create database `<DBPREFIX>_django` (see `base_config.py`)
- Grant appropriate permissions. Example:

```sql
CREATE USER 'cohiva'@'localhost' IDENTIFIED BY '<STRONG_PASSWORD>';
CREATE DATABASE `cohiva_django`;  -- production database
GRANT ALL PRIVILEGES ON `cohiva_django`.* TO 'cohiva'@'localhost';
FLUSH PRIVILEGES;
```

For development/staging with manual database:
```sql
CREATE DATABASE `cohiva_django_test`;  -- dev/staging database
GRANT ALL PRIVILEGES ON `cohiva_django_test`.* TO 'cohiva'@'localhost';
GRANT ALL PRIVILEGES ON `test_cohiva_django_test`.* TO 'cohiva'@'localhost';  -- for tests
```

## Production Database and Webserver

 - In the production settings, the default database name is `<DBPREFIX>_django`. So you need to create that and grand permissions for a production instance.
 - Configure a webserver with a WSGI for production and (optionally) a proxy for the test/dev-server. See example in `deployment/apache2-example.conf` for Apache.

## Basic setup and configuration of Cohiva

1. Create default config files and templates:
   
       ./setup.py

2. Edit `cohiva/base_config.py` and adjust at least `INSTALL_DIR` (e.g. `/var/www/cohiva-demo`).

3. Run `./setup.py` again to populate `INSTALL_DIR`. It will ask for information to create a certificate for the SAML2 authentication.
    
4. (If required) Add custom settings to `cohiva/settings.py` or `cohiva/settings_production.py` (production-only settings, wich overwrites the basic in `settings.py` for the production environment). For config options and default values see `cohiva/settings*_defaults.py`.

5. Start using Cohiva:

       # Load initial demo data (optional)
       ./scripts/demo_data_manager.py --load

       ./manage.py migrate  # Initial DB-creation/migration

    Test data and logs are at `<INSTALL_DIR>/django-test`, the production environment lives in `<INSTALL_DIR>/django-production`.
    The production data can be copied to the test environment with `./manage.py copy_production_to_test`.

    The Cohiva login screen is at `https://hostname/admin/`. For the first login, you need to create a superuser:

       ./manage.py createsuperuser
       ./manage.py createsuperuser --settings=cohiva.settings_production

## Development Workflow

### Daily Development Commands

**Start development environment:**
```bash
./develop.sh                    # Start everything (Docker + Django)
./develop.sh --celery           # Include Celery worker
./develop.sh --skip-migrations  # Skip migrations on startup
```

The `develop.sh` script:
- ✅ Starts Docker Compose services (MariaDB, Redis)
- ✅ Waits for services to be healthy
- ✅ Runs database migrations (unless `--skip-migrations`)
- ✅ Starts Django development server
- ✅ Optionally starts Celery worker (`--celery`)
- ✅ Graceful shutdown on Ctrl+C (stops all services)

**Access the application:**
- Admin interface: http://localhost:8000/admin/
- Change port with `COHIVA_DEV_PORT` in `.env`

**Common development tasks:**
```bash
# Create migrations
./manage.py makemigrations

# Run tests
./run-tests.sh
./manage.py test --keepdb  # Faster, keeps test database

# Load demo data
./scripts/demo_data_manager.py --load

# Create superuser
./manage.py createsuperuser

# Python shell
./manage.py shell

# Database shell
./manage.py dbshell
```

**Docker service management:**
```bash
# View logs
docker compose -f docker-compose.dev.yml logs -f

# Restart services
docker compose -f docker-compose.dev.yml restart

# Stop services (keeps data)
docker compose -f docker-compose.dev.yml down

# Stop and remove data
docker compose -f docker-compose.dev.yml down -v  # ⚠️ Deletes databases
```

### Alternative: Manual Service Start

If you prefer more control or don't use `develop.sh`:

```bash
# 1. Start Docker services manually
docker compose -f docker-compose.dev.yml up -d

# 2. Start Django dev server
./runserver.sh  # Port configured in .env

# 3. (Optional) Start Celery worker
./runcelery.sh
```

## Advanced configuration

### Oauth2 and SAML2

`setup.py` will automatically create keys in:

    cohiva/saml2/private.key
    cohiva/saml2/public.pem
    cohiva/oauth2/oidc.key

### Custom website

Add `website` to `FEATURES` in `cohiva/base_config.py` and copy `website_example` to `website` (or create a new app `website`).

# Development

## Manage dependencies

Currently pip-tools is used for dependency management.

Generate/update `requirements.txt` from `requirements.in`:

    pip-compile --strip-extras requirements.in   # NOTE: --strip-extras will be default from v8.0.0

Upgrade packages:

    pip-compile --upgrade-package zipp --strip-extras requirements.in   # Upgrade a single package
    pip-compile --upgrade --strip-extras requirements.in                # Upgrade ALL packages

Sync virtual environment with new requirements.txt:

    ./install_dependencies.sh   # Runs install.py which calls pip-sync with appropriate flags

The installation process uses two scripts:
- `install_dependencies.sh`: Checks for Python 3.11+ and calls the Python script
- `install.py`: Python-based installation script that handles all dependency management

**Note:** The Quick Start `./bootstrap.sh` automatically runs `install_dependencies.sh` during initial setup. You only need to run `install_dependencies.sh` manually when updating dependencies after initial setup.

## Docker Compose for Development

The project includes a `docker-compose.dev.yml` file for local development with containerized services:

**Services included:**
- MariaDB 11.4 with `utf8mb4_unicode_ci` collation (`cohiva_django_test` database)
- Redis 7 for Celery broker/backend

**Docker Compose commands:**

    # Start services
    docker compose -f docker-compose.dev.yml up -d

    # Stop services
    docker compose -f docker-compose.dev.yml down

    # View logs
    docker compose -f docker-compose.dev.yml logs -f

    # Remove volumes (WARNING: deletes all data)
    docker compose -f docker-compose.dev.yml down -v

**Database connection details:**
- Host: `localhost` (or `127.0.0.1`)
- Port: `3306`
- Database: `cohiva_django_test`
- User: `cohiva`
- Password: `c0H1v4`
- Test database: `test_cohiva_django_test` (auto-created for tests)

These settings match the defaults in `cohiva/base_config_example.py`.

## Formatting and linting

Currently, ruff is used for formatting and linting. It is included in GitHub workflows through:

    ../scripts/before-pr.sh
    ../scripts/cleanup-on-push-to-main.sh

It is recommended to run `before-pr.sh` before committing code, either manually or automatically with a git pre-commit hook.

There is a ruff plugin for the PyCharm IDE (see below)

## Development workflow

    # Create new apps
    ./manage.py startapp <appname>
    ## Add it to INSTALLED_APPS in settings.py

    # Migrations
    ./manage.py makemigrations [--dry-run] [app-names...]
    ./manage.py migrate [--plan]

    # Format and lint
    ../scripts/before-pr.sh

    # Run Test-Server
    ./runserver.sh

    # Run tests
    ./manage.py test [--keepdb]

    # Get coverage
    coverage run manage.py test [--keepdb]
    coverage report  # or: html

    # Deploy to production
    ./deploy.py

## Migrations

    ./manage.py showmigrations [--plan]

## Tools

### PyCharm IDE

JetBrains [PyCharm](https://www.jetbrains.com/help/pycharm/installation-guide.html) is the recommended IDE.

Recommendations:

 - Install Ruff plugin for code formatting and linting.
   - Enable "Run ruff when the python file is saved" and "Use ruff format for version 0.0.289 and later".
   - Enable Ruff LSP feature (with LSP4IJ plugin in CE version)
   - Set config file to `pyproject.toml`
 - Set the Python interpreter to the correct virtual environment (if managed with `install_dependencies.sh`):
   - Settings > Python > Interpreter
   - Add Interpreter > Add Local Interpreter
   - Select existing > Type Python > Select `<path to venv>/bin/python3`

### dumpdata / loaddata

Save/load data to files (see https://docs.djangoproject.com/en/5.1/ref/django-admin/#dumpdata). Can be used to create fixtures for testing, loading inital data, debugging etc.  

    ## Save all contracts from production DB to JSON file (with one space indentation).
    ./manage.py dumpdata geno.Contract --indent 1 --settings=cohiva.settings_production -o fixtures/contracts.json
    ./manage.py loaddata contracts

### Demo data

Demo data can be loaded or saved with `./scripts/demo_data_manager.py`.
   
