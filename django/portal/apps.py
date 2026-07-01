from django.apps import AppConfig


class PortalConfig(AppConfig):
    name = "portal"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals

        assert signals
