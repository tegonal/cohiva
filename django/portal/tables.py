import django_tables2 as tables
from django.utils.safestring import mark_safe

from geno.models import Tenant


class TenantAdminTable(tables.Table):
    selection = tables.CheckBoxColumn(
        accessor="pk", orderable=False, attrs={"th": {"id": "all_row_selector"}}
    )
    email = tables.Column(accessor="name", verbose_name="Email", order_by="name__email")
    invitation_date = tables.Column(verbose_name="Einladung geschickt")
    last_login = tables.Column(
        accessor="name", verbose_name="Letzte Anmeldung", order_by="name__user__last_login"
    )

    class Meta:
        model = Tenant
        fields = (
            "selection",
            "name",
            "email",
            "invitation_date",
            "last_login",
        )  #'ts_created', 'ts_modified')
        attrs = {"class": "tenant-admin"}

    def render_email(self, value):
        return value.email

    def render_last_login(self, value):
        if value.user:
            if value.user.last_login:
                return value.user.last_login
            else:
                return "---"
        else:
            return "---"

    def render_name(self, value, record):
        return mark_safe(
            '<a href="/portal/tenant-admin/%d/change">%s</a>' % (record.pk, value)
        )  # (value.pk, value.name, value.first_name))
