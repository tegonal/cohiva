from django.apps import AppConfig
from django.conf import settings

from finance.accounting import AccountingManager, CashctrlBook, DummyBook, GnucashBook


class FinanceConfig(AppConfig):
    name = "finance"

    def ready(self):
        if getattr(settings, "GNUCASH", False):
            AccountingManager.register(GnucashBook)
        if getattr(settings, "CASHCTRL", False):
            AccountingManager.register(CashctrlBook)
        AccountingManager.register(DummyBook)
