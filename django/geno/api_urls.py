from django.urls import include, path
from rest_framework import routers

from . import api_views as views

## URLs for app API endpoints that live under /api/v<version>/<app>/

router = routers.DefaultRouter()
router.register(r"rentalunit", views.RentalUnitViewSet)
router.register(r"contract", views.ContractViewSet)

urlpatterns = [
    ## API endpoints
    path("", include(router.urls)),
    path("qrbill/", views.QRBill.as_view()),
    path("akonto/", views.Akonto.as_view()),
    path("capabilities/", views.CapabilitiesView.as_view()),
]
