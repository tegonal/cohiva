import datetime

import django_tables2 as dt2
from django.utils.safestring import mark_safe

from .models import Account, Transaction


class TransactionTable(dt2.Table):
    date = dt2.Column(footer="SUMME")
    amount = dt2.Column(footer=lambda table: sum(x.amount for x in table.data))
    saldo = dt2.Column(accessor="pk", verbose_name="Saldo", orderable=False)
    note = dt2.Column(accessor="description", footer=lambda table: f"{len(table.data)} Buchungen")

    def render_saldo(self, record):
        if not self.balance:
            return "-"
        return self.balance[record.pk]

    def __init__(self, *args, **kwargs):
        self.balance = kwargs.pop("balance", {})
        super().__init__(*args, **kwargs)

    class Meta:
        model = Transaction
        fields = ("date", "name", "account", "amount", "saldo", "note")


class AccountTable(dt2.Table):
    download = dt2.Column(accessor="pk", verbose_name="Download", orderable=False)

    def render_name(self, record):
        return mark_safe('<a href="edit/%d/">%s</a>' % (record.pk, record.name))

    def render_account_owners(self, record):
        owners = []
        for owner in record.account_owners.all():
            owners.append("%s" % owner.owner_object)
        return " / ".join(owners)

    def render_download(self, record):
        return mark_safe(f'<a href="qrbill/{record.pk}/">QR-Rechnung</a>')

    class Meta:
        model = Account
        fields = ("name", "pin", "balance", "account_owners", "active", "download")


class RevenueReportTable(dt2.Table):
    date = dt2.Column(verbose_name="Periode", footer="Total")
    amount_in = dt2.Column(
        verbose_name="Gutschriften", footer=lambda table: sum(x["amount_in"] for x in table.data)
    )
    amount_out = dt2.Column(
        verbose_name="Einkäufe", footer=lambda table: sum(x["amount_out"] for x in table.data)
    )
    amount_net = dt2.Column(
        verbose_name="Differenz", footer=lambda table: sum(x["amount_net"] for x in table.data)
    )
    balance = dt2.Column(verbose_name="Saldo am Ende der Periode")


class SalesByAccountReportTable(dt2.Table):
    year = datetime.datetime.now().year
    account = dt2.Column(verbose_name="Konto", footer="Total")
    amount_cur = dt2.Column(
        verbose_name=f"{year}", footer=lambda table: sum(x["amount_cur"] for x in table.data)
    )
    amount_prev = dt2.Column(
        verbose_name=f"{year - 1}", footer=lambda table: sum(x["amount_prev"] for x in table.data)
    )
    amount_prev2 = dt2.Column(
        verbose_name=f"{year - 2}", footer=lambda table: sum(x["amount_prev2"] for x in table.data)
    )
