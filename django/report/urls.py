from django.urls import path

from . import views as report_views

urlpatterns = [
    path("test_celery/", report_views.test_celery, name="celery-test"),
    path(
        "test_celery_nobackend/", report_views.test_celery_nobackend, name="celery-test-nobackend"
    ),
    path(
        "configure/<int:report_id>/",
        report_views.ReportConfigView.as_view(),
        name="report-configure",
    ),
    path("output/<int:report_id>/", report_views.ReportOutputView.as_view(), name="report-output"),
    path(
        "output/<int:report_id>/download/all/",
        report_views.ReportDownloadAllView.as_view(),
        name="report-download-all",
    ),
    path(
        "output/<int:report_id>/download/<int:pk>/",
        report_views.ReportDownloadView.as_view(),
        name="report-download",
    ),
    path(
        "output/<int:report_id>/regenerate/<int:output_id>/",
        report_views.regenerate_output,
        name="report-regenerate-output",
    ),
    path(
        "delete_output/<int:report_id>/",
        report_views.ReportDeleteAllOutputView.as_view(),
        name="report-delete-all-output",
    ),
    path(
        "generate/<int:report_id>/",
        report_views.generate_report,
        {"dry_run": False},
        name="report-generate",
    ),
    path(
        "generate_dryrun/<int:report_id>/",
        report_views.generate_report,
        name="report-generate_dryrun",
    ),
]
