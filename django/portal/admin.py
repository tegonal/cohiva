from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from geno.admin import GenoBaseAdmin

from .models import OAuthAppPermissionRule, OAuthAppSettings, OAuthUserStats, TenantAdmin


@admin.register(TenantAdmin)
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
    search_fields = ["name__name", "name__first_name", "buildings__name", "notes"]
    autocomplete_fields = ["name", "buildings"]


@admin.register(OAuthUserStats)
class OAuthUserStatsAdmin(ModelAdmin):
    model = OAuthUserStats
    fields = ["application", "user", "first_login_at", "last_seen_at"]
    list_filter = fields
    list_display = fields
    search_fields = ["application__name", "user__email", "user__username"]


class OAuthAppPermissionRuleInline(TabularInline):
    model = OAuthAppPermissionRule
    fields = ["order", "role", "group", "role_or_group_must_match", "action"]
    extra = 0


@admin.register(OAuthAppSettings)
class OAuthAppSettingsAdmin(ModelAdmin):
    model = OAuthAppSettings
    fields = ["application", "notify_on_first_login", "notify_email"]
    list_display = fields
    list_filter = ["notify_on_first_login"]
    search_fields = ["application__name", "notify_email"]
    autocomplete_fields = ["application"]
    inlines = [OAuthAppPermissionRuleInline]
