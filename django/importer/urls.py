"""
URL configuration for the importer app.
"""

from django.urls import path

from . import views

app_name = "importer"

urlpatterns = [
    path("upload/", views.upload_import, name="upload"),
    path("job/<int:job_id>/", views.import_job_detail, name="detail"),
]

