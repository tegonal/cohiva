from django.contrib.auth import views as auth_views
from django.urls import path

from portal.auth import CohivaAuthorizationView

# from wagtail import urls as wagtail_urls
from . import views as portal_views

app_name = "portal"
urlpatterns = [
    path("o/authorize/", CohivaAuthorizationView.as_view(), name="authorize"),
    path("login/", portal_views.login),
    path("logout/", portal_views.logout),
    path("password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", portal_views.password_reset, name="password_reset"),
    path("password_reset/done/", portal_views.password_reset_done, name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        portal_views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("reset/done/", portal_views.password_reset_complete, name="password_reset_complete"),
    path("me/", portal_views.oauth_identity),
    path("tenant-admin/", portal_views.tenant_admin_table, name="tenant_admin_table"),
    path(
        "tenant-admin/<tenant_id>/change/",
        portal_views.tenant_admin_edit,
        name="tenant_admin_edit",
    ),
    path("tenant-admin/add/", portal_views.tenant_admin_edit, name="tenant_admin_edit"),
    path("tenant-admin/upload/", portal_views.tenant_admin_upload, name="tenant_admin_upload"),
    path(
        "tenant-admin/upload/commit/",
        portal_views.tenant_admin_upload_commit,
        name="tenant_admin_upload_commit",
    ),
    path(
        "tenant-admin/maintenance/",
        portal_views.tenant_admin_maintenance,
        name="tenant_admin_maintenance",
    ),
    path("cron_maintenance/", portal_views.cron_maintenance, name="cron_maintenance"),
    path(
        "rocket_chat_webhook/<webhook_name>/",
        portal_views.rocket_chat_webhook,
        name="rocket_chat_webhook",
    ),
    path("", portal_views.home, name="portal-home"),
]
