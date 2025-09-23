import json

from celery.result import AsyncResult
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.core.exceptions import ImproperlyConfigured
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.views.generic.detail import BaseDetailView

# from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from cohiva.views.generic import ZipDownloadView

from .admin import ReportOutputAdmin
from .forms import ReportConfigForm
from .models import Report, ReportInputData, ReportInputField, ReportOutput
from .tasks import generate_nk_report, regenerate_nk_output, test_task


## Test task and querying result backend
@login_required
def test_celery(request):
    if "test_task_id" in request.session:
        res = AsyncResult(request.session["test_task_id"])
        if res.ready():
            # value = res.get()  ## Propagate exceptions
            value = res.get(propagate=False)
            del request.session["test_task_id"]
        else:
            value = "Pending..."
    else:
        # res = test.delay(True)  ## Test exception handling
        res = test_task.delay()  ## No exception
        request.session["test_task_id"] = res.id
        value = "Started NEW task!"
    return HttpResponse(
        f"res.id={res.id}<br>res.state={res.state}<br>res.failed={res.failed()}<br>res.ready={res.ready()}<br>value={value}<br>"
    )


## Test without result backend
@login_required
def test_celery_nobackend(request):
    res = test_task.delay()
    return HttpResponse(f"Test task started (without result backend).<br>res.id={res.id}")


class ReportViewMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.report = Report.objects.get(id=kwargs["report_id"])
        except Report.DoesNotExist:
            self.report = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = self.report
        return context


class ReportConfigView(LoginRequiredMixin, ReportViewMixin, FormView):
    template_name = "report/report_config.html"
    form_class = ReportConfigForm

    def get_initial(self):
        initial = super().get_initial()
        if self.report:
            for field in ReportInputData.objects.filter(report=self.report):
                if field.name.field_type == "bool":
                    initial[f"report_input_{field.name.id}"] = field.value.lower() in [
                        "true",
                        "1",
                        "yes",
                    ]
                elif field.name.field_type == "file" and field.value.startswith("filer:"):
                    initial[f"report_input_{field.name.id}"] = int(field.value[6:])
                else:
                    initial[f"report_input_{field.name.id}"] = field.value
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["report"] = self.report
        return kwargs

    # def get_context_data(self, **kwargs):
    #    kwargs['report'] = self.report
    #    return super().get_context_data(**kwargs)

    def save(self, values):
        for key in values:
            if key.startswith("report_input_"):
                field_id = int(key[13:])
                field = ReportInputField.objects.get(id=field_id)
                if values[key] is None:
                    new_value = ""
                elif field.field_type == "file":
                    new_value = f"filer:{values[key].id}"
                else:
                    new_value = str(values[key])
                try:
                    data = ReportInputData.objects.get(name=field, report=self.report)
                except ReportInputData.DoesNotExist:
                    data = ReportInputData(name=field, report=self.report, value="")
                if data.value != new_value:
                    # print(f"Save: {field.name}: {data.value} => {new_value}")
                    data.value = new_value
                    data.save()

    def form_valid(self, form):
        self.save(form.cleaned_data)
        return HttpResponseRedirect(f"/admin/report/report/{self.report.id}/change")


class ReportOutputView(LoginRequiredMixin, ReportViewMixin, ListView):
    ordering = ("group", "name")

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.report:
            self.queryset = ReportOutput.objects.filter(
                report=self.report
            )  # .order_by('group','name')
            if "regenerate_output_pk" in kwargs:
                regenerate_output(request, kwargs["regenerate_output_pk"])
        else:
            self.queryset = ReportOutput.objects.none()


class ReportDeleteAllOutputView(ReportOutputView):
    def get(self, request, *args, **kwargs):
        if self.queryset.count() == 0:
            self.report.reset()
            return HttpResponseRedirect(f"/admin/report/report/{self.report.id}/change/")
        query = QueryDict(mutable=True)
        query.update(
            {
                "action": "delete_selected",
                "select_across": "1",
                "index": "0",
                "_selected_action": [],
            }
        )
        request.POST = query
        model_admin = ReportOutputAdmin(ReportOutput, admin.site)
        resp = model_admin.response_action(request, self.queryset)
        if not resp:
            return HttpResponseRedirect(f"/admin/report/report/{self.report.id}/change/")
        return resp

    def post(self, request, *args, **kwargs):
        model_admin = ReportOutputAdmin(ReportOutput, admin.site)
        resp = model_admin.response_action(request, self.queryset)
        return resp


class ReportDownloadView(LoginRequiredMixin, ReportViewMixin, BaseDetailView):
    model = ReportOutput

    def render_to_response(self, context):
        filename = self.object.get_filename()
        if "as_attachment" not in context:
            if filename[-3:] in ("png", "jpg", "jpeg", "gif"):
                context["as_attachment"] = False
            else:
                context["as_attachment"] = True
        return FileResponse(open(filename, "rb"), as_attachment=context["as_attachment"])


class ReportDownloadAllView(LoginRequiredMixin, ReportViewMixin, ZipDownloadView):
    def get_zipfile_name(self):
        return f"{self.report.name}.zip"

    def get_files(self):
        files = []
        for output in ReportOutput.objects.filter(report=self.report):
            if output.output_type == "text":
                files.append({"content": output.value, "archive_filename": f"{output.name}.txt"})
            else:
                files.append({"fullpath": output.get_filename(), "archive_filename": output.value})
        return files


@login_required
def generate_report(request, report_id=None, dry_run=True):
    try:
        report = Report.objects.get(pk=report_id)
    except Report.DoesNotExist:
        messages.error(request, f"Fehler: Report mit ID {report_id} nicht gefunden.")
        return HttpResponseRedirect("/admin/report/report/")
    if not settings.DEBUG and report.state != "new":
        messages.error(
            request,
            f"Fehler: Erstellung des Reports wurde bereits gestartet (state={report.state}).",
        )
        return HttpResponseRedirect(f"/admin/report/report/{report.id}/change/")
    if report.report_type.name != "Nebenkostenabrechnung":
        messages.error(
            request,
            f"Fehler: Erstellung von Reports des Typs '{report.report_type.name}' ist (noch) nicht unterstützt.",
        )
        return HttpResponseRedirect(f"/admin/report/report/{report.id}/change/")
    # generate_nk_report.delay_on_commit(report_id,dry_run=dry_run)
    res = generate_nk_report.delay(report_id, dry_run=dry_run)
    if not res:
        messages.error(
            request, "Fehler: Konnte Erstellung des Reports nicht starten. Läuft Celery-Worker?"
        )
        return HttpResponseRedirect(f"/admin/report/report/{report.id}/change/")
    report.task_id = res.id
    report.state = "pending"
    if dry_run:
        report.state_info = "Erstellung des Reports (Testlauf) läuft."
    else:
        report.state_info = "Erstellung des Reports läuft."
    report.save()
    messages.success(request, "Die Erstellung des Reports wurde gestartet.")
    # return HttpResponseRedirect(f'/admin/report/report/{report.id}/change/')
    return HttpResponseRedirect("/admin/report/report/")


def regenerate_output(request, report_id, output_id):
    try:
        output = ReportOutput.objects.get(pk=output_id)
    except ReportOutput.DoesNotExist:
        messages.error(request, f"Der Report-Output mit der ID {output_id} wurde nicht gefunden.")
        return HttpResponseRedirect(f"/report/output/{report_id}/")

    if output.regeneration_json:
        regeneration_data = json.loads(output.regeneration_json)
    else:
        regeneration_data = {}

    regen_type = regeneration_data.get("type")
    if regen_type == "nk_bills" and "contract_id" in regeneration_data:
        res = regenerate_nk_output.delay(
            "contract_bill", output.report.id, regeneration_data["contract_id"]
        )
    else:
        messages.error(
            request,
            f"Das erneute Erstellen von diesem Ausgabetyp wird nicht unterstützt ({output.name}).",
        )
        return HttpResponseRedirect(f"/report/output/{report_id}/")
    if not res:
        messages.error(
            request,
            f"Konnte erneute Erstellung von «{output.name}» nicht starten. Läuft Celery-Worker?",
        )
        return HttpResponseRedirect(f"/report/output/{report_id}/")
    messages.success(
        request, f"Das erneute Erstellen von «{output.name}» wurde gestartet [{res.id}]."
    )
    return HttpResponseRedirect(f"/report/output/{report_id}/")
