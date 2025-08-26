from django.urls import path

from . import views as reservation_views

app_name = "reservation"
urlpatterns = [
    path("sync/ical/", reservation_views.sync_ical_reservations),
    path("send_report_emails/", reservation_views.send_report_emails),
    path("cron_maintenance/", reservation_views.cron_maintenance),
]
