# from django.conf import settings

from .book import CashctrlBook as CashctrlBook
from .book import DummyBook
from .book import GnucashBook as GnucashBook
from .manager import AccountingManager

# TODO: Register books based on settings
AccountingManager.register(DummyBook)
