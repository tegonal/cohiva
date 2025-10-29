from django.apps import AppConfig

from finance.accounting import AccountingManager


class FinanceConfig(AppConfig):
    name = "finance"

    def ready(self):
        AccountingManager.register_backends_from_settings()
