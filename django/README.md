# Installation

## Install required system packages

Example using `aptitude` on Debian 11:

    aptitude install build-essential
    aptitude install python3-dev
    aptitude install python3-venv
    aptitude install libmariadb-dev   ## or default-libmysqlclient-dev
    aptitude install libfreetype-dev
    aptitude install libjpeg-dev
    aptitude install libffi-dev
    aptitude install redis-server     ## for celery broker/result backend
    aptitude install poppler-utils    ## (optional, for tests)
    aptitude install xmlsec1	          ## for SAML 2.0 IDP (see SAML_IDP_CONFIG settings)
    aptitude install libreoffice-writer   ## for PDF generation from .odt templates

NOTE: This list may not be complete. If you get errors when installing python packages in the next step, you might need to install additional packages, such as `libxml2-dev`.

## Setup Python environment

Example for project `cohiva-demo`:

    ## Checkout Cohiva code
    mkdir -p /var/www/cohiva-demo
    cd /var/www/cohiva-demo
    git clone https://github.com/tegonal/cohiva.git .

    ## Change to django directory
    cd django
    
    ## Create and activate virtual environment
    python3 -m venv ~/.venv/cohiva-demo-prod
    source ~/.venv/cohiva-demo-prod/bin/activate
    
    ## Install dependencies
    ./install_dependencies.sh

## Setup Development/Staging Database

- Create a MariaDB/MySQL user (e.g. 'cohiva') and pick a database prefix (e.g. 'cohiva')
- Create the database `<DBPREFIX>_django_test` for development/staging.
- Grant permissions for that database and also for `test_<DBPREFIX>_django_test`, which will be automatically created when running tests. For example:
```
    CREATE USER 'cohiva'@'localhost' IDENTIFIED BY '<SECRET>';
    CREATE DATABASE `cohiva_django_test`;  -- dev/staging database
    GRANT ALL PRIVILEGES ON `cohiva_django_test`.* TO 'cohiva'@'localhost';
    GRANT ALL PRIVILEGES ON `test_cohiva_django_test`.* TO 'cohiva'@'localhost';   -- for automated testsCode bla
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
       ./runserver.sh       # Run the test-server. The port can be configred in `.env`
       ./runcelery.sh       # Run the celery-worker for testing (if required)
       
       ./run-tests.sh       # Run tests (optional, requires permission to create a temporary database `test_<stagingdbname>`)
       
       ./deploy.py          # Deploy to production environment
       
    Test data and logs are at `<INSTALL_DIR>/django-test`, the production environment lives in `<INSTALL_DIR>/django-production`.
    The production data can be copied to the test environment with `./manage.py copy_production_to_test`.

    The Cohiva login screen is at `https://hostname/admin/`. For the first login, you need to create a superuser:

       ./manage.py createsuperuser
       ./manage.py createsuperuser --settings=cohiva.settings_production

## Advanced configuration

### Oauth2 and SAML2

`setup.py` will automatically create keys in:

    cohiva/saml2/private.key
    cohiva/saml2/public.pem

### Custom website

Add `website` to `FEATURES` in `cohiva/base_config.py` and copy `website_example` to `website` (or create a new app `website`).

# Development

## Manage dependencies

Generate/update `requirements.txt` from `requirements.in`:

    pip-compile --strip-extras requirements.in   # NOTE: --strip-extras will be dafault from v8.0.0

Upgrade packages:

    pip-compile --upgrade-package zipp --strip-extras requirements.in   # Upgrade a single package
    pip-compile --upgrade --strip-extras requirements.in                # Upgrade ALL packages

Sync virtual environment with new requirements.txt:

    ./install_dependencies.sh   (which will call `pip-sync -a`)

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
   
