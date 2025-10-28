from django.conf import settings

from .book import DummyBook
from .cashctrl import CashctrlBook as CashctrlBook
from .gnucash import GnucashBook as GnucashBook
from .manager import AccountingManager

if getattr(settings, "GNUCASH", False):
    AccountingManager.register(GnucashBook)
if getattr(settings, "CASHCTRL", False):
    AccountingManager.register(CashctrlBook)
AccountingManager.register(DummyBook)
