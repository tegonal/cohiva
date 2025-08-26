from django.urls import path
from django.views.generic.base import TemplateView  # ,RedirectView

from website import views as website_views

urlpatterns = [
    path("", TemplateView.as_view(template_name="website/main.html"), name="website-main"),
    path("anmeldung/<int:registration_id>/", website_views.registration),
]
