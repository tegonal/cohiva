import django_tables2 as tables
from django.utils.safestring import mark_safe

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


class InvoiceOverviewTotalColumn(tables.Column):
    def render_footer(self, bound_column, table):
        total_receivable = sum(
            max(x["total"], 0) for x in table.data
        )  ## positive values (Forderungen)
        total_payable = sum(
            min(x["total"], 0) for x in table.data
        )  ## negative values (Verbindlichkeiten / Vorauszahlungen)
        return mark_safe(
            "%s<br>%s<br>= %s"
            % (total_receivable, total_payable, total_receivable + total_payable)
        )


class InvoiceOverviewTable(tables.Table):
    obj = tables.Column(verbose_name="Link", footer="Summe")
    name = tables.Column(
        footer=lambda table: len(table.data), verbose_name="Vertrag/Person/Org."
    )  # , order_by=("obj__rental_units__name")) #empty_values=())
    total_billed = tables.Column(
        footer=lambda table: sum(x["total_billed"] for x in table.data),
        verbose_name="Gefordert",
        attrs={"td": {"style": "text-align: right;"}},
    )
    total_paid = tables.Column(
        footer=lambda table: sum(x["total_paid"] for x in table.data),
        verbose_name="Bezahlt",
        attrs={"td": {"style": "text-align: right;"}},
    )
    total = InvoiceOverviewTotalColumn(
        verbose_name="Saldo", attrs={"td": {"style": "text-align: right;"}}
    )
    open_bill_date = tables.Column(verbose_name="Offene Forderung seit")
    last_payment_date = tables.Column(verbose_name="Letzte Zahlung")

    def render_obj(self, value):
        if type(value) is Contract:
            obj_type = "c"
        else:
            obj_type = "p"
        return mark_safe(
            '<a href="/geno/invoice/detail/%s/%d/">Details</a>' % (obj_type, value.pk)
        )

    class Meta:
        attrs = {"class": "paleblue"}


class InvoiceDetailTable(tables.Table):
    obj = tables.Column(verbose_name="Link")
    date = tables.Column(verbose_name="Datum")
    number = tables.Column(verbose_name="Nummer")
    note = tables.Column(verbose_name="Beschreibung")
    billed = tables.Column(verbose_name="Rechnung", attrs={"td": {"style": "text-align: right;"}})
    paid = tables.Column(verbose_name="Zahlung", attrs={"td": {"style": "text-align: right;"}})
    balance = tables.Column(verbose_name="Saldo", attrs={"td": {"style": "text-align: right;"}})
    consolidated = tables.Column(verbose_name="K")
    extra_info = tables.Column(verbose_name="Zusatzinfo")

    ## TODO: Open Invoice in popup window?
    #    function showAdminPopup(triggeringLink, name_regexp, add_popup) {
    #    var name = triggeringLink.id.replace(name_regexp, '');
    #    name = id_to_windowname(name);
    #    var href = triggeringLink.href;
    #    if (add_popup) {
    #        if (href.indexOf('?') === -1) {
    #            href += '?_popup=1';
    #        } else {
    #            href += '&_popup=1';
    #        }
    #    }
    #    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    #    win.focus();
    #    return false;
    # }

    def render_obj(self, value):
        if value.invoice_type == "Payment":
            link_text = "Zahlung"
        else:
            link_text = "Rechnung"
        return mark_safe(
            '<a href="/admin/geno/invoice/%d/" '
            'class="related-widget-wrapper-link change-related">%s</a>' % (value.pk, link_text)
        )

    class Meta:
        attrs = {"class": "paleblue"}


class RentalUnitTable(tables.Table):
    name = tables.RelatedLinkColumn()

    class Meta:
        model = RentalUnit
        fields = ("name",)
        attrs = {"class": "paleblue"}
