import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from .models import Contract, Member, RentalUnit


class MemberTable(tables.Table):
    address = tables.Column(accessor="name__street")
    city = tables.Column(accessor="name__city")
    title = tables.Column(accessor="name__title")
    email = tables.EmailColumn(accessor="name__email")
    telephone = tables.Column(accessor="name__telephone")
    mobile = tables.Column(accessor="name__mobile")
    occupation = tables.Column(accessor="name__occupation")
    date_join = tables.Column()

    class Meta:
        model = Member
        fields = (
            "name",
            "address",
            "city",
            "title",
            "email",
            "telephone",
            "mobile",
            "occupation",
            "date_join",
            "flag_01",
            "flag_02",
            "flag_03",
            "flag_04",
            "flag_05",
        )
        attrs = {"class": "paleblue"}


class MemberTableAdmin(tables.Table):
    name = tables.RelatedLinkColumn()
    address = tables.Column(accessor="name__street")
    city = tables.Column(accessor="name__city")
    title = tables.Column(accessor="name__title")
    email = tables.EmailColumn(accessor="name__email")
    telephone = tables.Column(accessor="name__telephone")
    mobile = tables.Column(accessor="name__mobile")
    occupation = tables.Column(accessor="name__occupation")
    date_join = tables.Column()
    bankaccount = tables.Column(accessor="name__bankaccount")

    class Meta:
        model = Member
        fields = (
            "name",
            "address",
            "city",
            "title",
            "email",
            "telephone",
            "mobile",
            "occupation",
            "date_join",
            "bankaccount",
        )
        attrs = {"class": "paleblue"}


UNFOLD_LINK_CLASS = "text-primary-600 dark:text-primary-400 hover:underline"


def _get_balance_color_class(value):
    """Return Tailwind CSS classes for balance value coloring."""
    if value > 0:
        return "text-red-600 dark:text-red-400 font-semibold"
    elif value < 0:
        return "text-green-600 dark:text-green-400 font-semibold"
    return "text-gray-500 dark:text-gray-400"


def _render_currency(value, css_class="text-right"):
    """Render a currency value with right alignment."""
    return mark_safe(f'<div class="{css_class}">{value:.2f}</div>')


def _render_currency_colored(value):
    """Render a currency value with color based on positive/negative."""
    color_class = _get_balance_color_class(value)
    return mark_safe(f'<div class="text-right {color_class}">{value:.2f}</div>')


class InvoiceOverviewTotalColumn(tables.Column):
    def render_footer(self, bound_column, table):
        total_receivable = sum(max(x["total"], 0) for x in table.data)
        total_payable = sum(min(x["total"], 0) for x in table.data)
        return mark_safe(
            f'<div class="text-right">'
            f'<div class="text-red-600 dark:text-red-400">{total_receivable:.2f}</div>'
            f'<div class="text-green-600 dark:text-green-400">{total_payable:.2f}</div>'
            f'<div class="border-t border-base-300 dark:border-base-700 mt-1 pt-1 whitespace-nowrap">'
            f"= {total_receivable + total_payable:.2f}</div>"
            f"</div>"
        )


def _entries_footer(table):
    """Footer function for entry count with proper pluralization."""
    count = len(table.data)
    return ngettext_lazy("%(count)d Eintrag", "%(count)d Einträge", count) % {"count": count}


class InvoiceOverviewTable(tables.Table):
    obj = tables.Column(verbose_name=_("Link"), footer=_("Summe"), orderable=False)
    name = tables.Column(footer=_entries_footer, verbose_name=_("Vertrag/Person/Org."))
    total_billed = tables.Column(
        footer=lambda table: _render_currency(sum(x["total_billed"] for x in table.data)),
        verbose_name=_("Gefordert"),
        attrs={"td": {"class": "text-right"}},
    )
    total_paid = tables.Column(
        footer=lambda table: _render_currency(sum(x["total_paid"] for x in table.data)),
        verbose_name=_("Bezahlt"),
        attrs={"td": {"class": "text-right"}},
    )
    total = InvoiceOverviewTotalColumn(
        verbose_name=_("Saldo"),
        attrs={"td": {"class": "text-right"}},
    )
    open_bill_date = tables.DateColumn(
        verbose_name=_("Offene Forderung seit"),
        format="d.m.Y",
        attrs={"td": {"class": "text-center"}},
    )
    last_payment_date = tables.DateColumn(
        verbose_name=_("Letzte Zahlung"),
        format="d.m.Y",
        attrs={"td": {"class": "text-center"}},
    )

    def render_obj(self, value):
        obj_type = "c" if isinstance(value, Contract) else "p"
        url = reverse("geno:debtor-detail", kwargs={"key_type": obj_type, "key": value.pk})
        return mark_safe(f'<a href="{url}" class="{UNFOLD_LINK_CLASS}">{_("Details")}</a>')

    def render_total_billed(self, value):
        return _render_currency(value)

    def render_total_paid(self, value):
        return _render_currency(value)

    def render_total(self, value):
        return _render_currency_colored(value)

    class Meta:
        template_name = "geno/components/django_tables2_unfold.html"
        attrs = {"class": "unfold-table"}
        empty_text = _("Keine Debitoren gefunden.")
        order_by = "-total"


class InvoiceDetailTable(tables.Table):
    obj = tables.Column(verbose_name=_("Link"), orderable=False)
    date = tables.DateColumn(
        verbose_name=_("Datum"),
        format="d.m.Y",
        attrs={"td": {"class": "text-center"}},
    )
    number = tables.Column(verbose_name=_("Nummer"), attrs={"td": {"class": "text-center"}})
    note = tables.Column(verbose_name=_("Beschreibung"))
    billed = tables.Column(verbose_name=_("Rechnung"), attrs={"td": {"class": "text-right"}})
    paid = tables.Column(verbose_name=_("Zahlung"), attrs={"td": {"class": "text-right"}})
    balance = tables.Column(verbose_name=_("Saldo"), attrs={"td": {"class": "text-right"}})
    consolidated = tables.Column(verbose_name=_("K"), attrs={"td": {"class": "text-center"}})
    extra_info = tables.Column(verbose_name=_("Zusatzinfo"))

    def render_obj(self, value):
        link_text = _("Zahlung") if value.invoice_type == "Payment" else _("Rechnung")
        url = reverse("admin:geno_invoice_change", args=[value.pk])
        return mark_safe(f'<a href="{url}" class="{UNFOLD_LINK_CLASS}">{link_text}</a>')

    def render_billed(self, value):
        return _render_currency(value) if value else ""

    def render_paid(self, value):
        return _render_currency(value) if value else ""

    def render_balance(self, value):
        return _render_currency_colored(value)

    class Meta:
        template_name = "geno/components/django_tables2_unfold.html"
        attrs = {"class": "unfold-table"}
        empty_text = _("Keine Rechnungen gefunden.")
        order_by = "-date"


class RentalUnitTable(tables.Table):
    name = tables.RelatedLinkColumn()

    class Meta:
        model = RentalUnit
        fields = ("name",)
        attrs = {"class": "paleblue"}
