from importlib import import_module

from django.db import DEFAULT_DB_ALIAS, connections
from django.test.runner import DiscoverRunner


class SelectiveMigrationRunner(DiscoverRunner):
    """A test runner that applies the migrations specified in migrations without checks"""

    migrations = {
        ("geno", "0006_tenantsview"),
    }

    def setup_databases(self, **kwargs):
        old_config = super().setup_databases(**kwargs)

        for app_label, migration in self.migrations:
            print(f"Applying required migration for tests: {app_label}.{migration}")
            module = import_module(f"{app_label}.migrations.{migration}")
            migration_class = module.Migration
            schema_editor = connections[DEFAULT_DB_ALIAS].schema_editor()
            for op in migration_class.operations:
                op.database_forwards(app_label, schema_editor, from_state=None, to_state=None)

        return old_config
