"""
Views for the importer app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .forms import ImportJobForm
from .models import ImportJob
from .services import process_import_job, process_member_address_import


@login_required
@require_http_methods(["GET", "POST"])
def upload_import(request):
    """
    View for uploading Excel files for import.
    """
    if request.method == "POST":
        form = ImportJobForm(request.POST, request.FILES)
        if form.is_valid():
            import_job = form.save(commit=False)
            import_job.created_by = request.user
            import_job.save()

            messages.success(
                request, _("File uploaded successfully. Processing import...")
            )

            # Process the import (in production, consider using Celery for async processing)
            try:
                results = process_import_job(import_job.id)
                messages.success(
                    request,
                    _(
                        "Import completed: {success} records imported, {errors} errors"
                    ).format(
                        success=results["success_count"], errors=results["error_count"]
                    ),
                )
            except Exception as e:
                messages.error(
                    request, _("Import failed: {error}").format(error=str(e))
                )

            return redirect("importer:upload")
    else:
        form = ImportJobForm()

    # Get recent import jobs for this user
    recent_jobs = ImportJob.objects.filter(created_by=request.user).order_by(
        "-created_at"
    )[:10]

    context = {
        "form": form,
        "recent_jobs": recent_jobs,
    }

    return render(request, "importer/upload.html", context)


@login_required
def import_job_detail(request, job_id):
    """
    View for displaying details of an import job.
    """
    import_job = ImportJob.objects.get(id=job_id, created_by=request.user)

    context = {
        "import_job": import_job,
    }

    return render(request, "importer/detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def upload_member_address_import(request):
    """
    View for uploading Excel files for member/address import.
    """
    if request.method == "POST":
        form = ImportJobForm(request.POST, request.FILES)
        if form.is_valid():
            import_job = form.save(commit=False)
            import_job.created_by = request.user
            import_job.save()

            messages.success(
                request, _("File uploaded successfully. Processing member/address import...")
            )

            # Process the member/address import
            try:
                results = process_member_address_import(import_job.id)
                messages.success(
                    request,
                    _(
                        "Member/Address import completed: {success} records imported, {errors} errors"
                    ).format(
                        success=results["success_count"], errors=results["error_count"]
                    ),
                )
            except Exception as e:
                messages.error(
                    request, _("Import failed: {error}").format(error=str(e))
                )

            return redirect("importer:upload_member_address")
    else:
        form = ImportJobForm()

    # Get recent import jobs for this user
    recent_jobs = ImportJob.objects.filter(created_by=request.user).order_by(
        "-created_at"
    )[:10]

    context = {
        "form": form,
        "recent_jobs": recent_jobs,
        "import_type": "Member/Address",
    }

    return render(request, "importer/upload_member_address.html", context)


