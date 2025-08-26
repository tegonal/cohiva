from django.urls import include, path
from rest_framework import routers

from . import api_views as views

## URLs for app API endpoints that live under /api/v<version>/<app>/

router = routers.DefaultRouter()
router.register(r"reservations", views.ReservationViewSet, basename="reservation")
router.register(r"reservationtypes", views.ReservationTypeViewSet, basename="reservationtype")

urlpatterns = [
    ## API endpoints
    path("", include(router.urls)),
    path("search/", views.ReservationSearch.as_view(), name="reservation-search"),
    path("edit/", views.ReservationEdit.as_view(), name="reservation-edit"),
    path("report/", views.ReportSubmission.as_view(), name="report"),
    path("calendar_feeds/", views.CalendarFeeds.as_view(), name="calendar-feeeds"),
]
