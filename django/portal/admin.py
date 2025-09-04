from django.contrib import admin

from geno.admin import GenoBaseAdmin

from .models import TenantAdmin


class TenantAdminAdmin(GenoBaseAdmin):
    model = TenantAdmin
    fields = [
        "name",
        "buildings",
        "notes",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "list_active_buildings", "active"]
    list_filter = ["active"]
    my_search_fields = ["name__name", "name__first_name", "buildings__name", "notes"]
    search_fields = my_search_fields


admin.site.register(TenantAdmin, TenantAdminAdmin)
