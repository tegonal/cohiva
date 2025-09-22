"""
URL configuration for Cohiva.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

## django-filer

if "cms" in settings.COHIVA_FEATURES:
    from wagtail import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls
    from wagtail.documents import urls as wagtaildocs_urls

# from schema_graph.views import Schema

admin.site.site_header = settings.GENO_NAME + " – Cohiva"
admin.site.site_title = "Cohiva " + settings.COHIVA_SITE_NICKNAME
admin.site.index_title = "Genossenschafts-Administration"
admin.site.site_url = None  ## To disable 'view on site' link

urlpatterns = [
    ## Secure downloads for django-filer
    path("", include("filer.server.urls")),
    # Coviva core
    path("admin/", admin.site.urls),
    path("geno/", include("geno.urls")),
]

if "reservation" in settings.COHIVA_FEATURES:
    from reservation import views as reservation_views

    urlpatterns += [
        path("reservation/", include("reservation.urls")),
        path("api/v1/reservation/", include("reservation.api_urls")),
        path("calendar/feed/<calendar_id>/", reservation_views.calendar_feed),
    ]

if "credit_accounting" in settings.COHIVA_FEATURES:
    urlpatterns += [
        path("credit_accounting/", include("credit_accounting.urls")),
        path("api/v1/credit_accounting/", include("credit_accounting.api_urls")),
    ]

if "report" in settings.COHIVA_FEATURES:
    urlpatterns += [
        path("report/", include("report.urls")),
        # path('api/v1/report/', include('report.api_urls')),
    ]

if "portal" in settings.COHIVA_FEATURES:
    from portal.auth import CohivaAuthorizationView

    urlpatterns += [
        path(
            "login/sendpass/", RedirectView.as_view(url="/portal/", permanent=False), name="portal"
        ),
        path("login/", RedirectView.as_view(url="/portal/", permanent=False), name="portal"),
        path(
            "logout/", RedirectView.as_view(url="/portal/logout", permanent=False), name="portal"
        ),
        path("portal/", include("portal.urls")),
        ## Auth
        path("o/authorize/", CohivaAuthorizationView.as_view(), name="authorize"),
        path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
        path("idp/", include("djangosaml2idp.urls")),
    ]
else:
    urlpatterns += [
        path(
            "login/", RedirectView.as_view(url="/admin/login", permanent=False), name="admin-login"
        ),
        path(
            "logout/",
            RedirectView.as_view(url="/admin/logout", permanent=False),
            name="admin-logout",
        ),
    ]

if "api" in settings.COHIVA_FEATURES:
    urlpatterns += [
        # API
        path("api/v1/geno/", include("geno.api_urls")),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
        path("dj-rest-auth/", include("dj_rest_auth.urls")),
    ]

if "cms" in settings.COHIVA_FEATURES:
    # Wagtail
    urlpatterns += [
        path("cms/", include(wagtailadmin_urls)),
        path("documents/", include(wagtaildocs_urls)),
    ]
    if "portal" in settings.COHIVA_FEATURES:
        urlpatterns += [
            path("portal/", include(wagtail_urls)),
        ]

## Serve media files through the test server (don't do that for production!)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## Must be last to be able to handle root/wildcard URLs.
if "website" in settings.COHIVA_FEATURES:
    urlpatterns += [
        path("", include("website.urls")),
    ]
