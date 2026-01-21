from django.urls import path
from django.views.generic.base import RedirectView

from website import views as website_views

urlpatterns = [
    ## Redirect root to /admin as long as there is no website in place.
    path("", RedirectView.as_view(url="/admin/", permanent=False), name="root-redirect"),
    # path("", TemplateView.as_view(template_name="website/main.html"), name="website-main"),
    path("anmeldung/<int:registration_id>/", website_views.registration),
]
