from django.apps import AppConfig


class GenoConfig(AppConfig):
    name = "geno"

    def ready(self):
        """Import checks when app is ready."""
        from geno import checks  # noqa: F401
