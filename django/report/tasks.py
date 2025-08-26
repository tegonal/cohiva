import time

from celery import shared_task
from django.conf import settings

from .models import Report
from .report_nk import main, regenerate_bill


@shared_task
def test_task(failure=False):
    sleeptime = 2
    print(
        f"Running test celery task (sleep for {sleeptime} seconds). BASE_URL={settings.BASE_URL}, DEBUG={settings.DEBUG}"
    )
    time.sleep(2)
    if failure:
        raise Exception(f"Test exception BASE_URL={settings.BASE_URL}, DEBUG={settings.DEBUG}")
    return f"OK BASE_URL={settings.BASE_URL}, DEBUG={settings.DEBUG}"


@shared_task
def generate_nk_report(report_id, dry_run=True):
    try:
        report = Report.objects.get(pk=report_id)
        log = main(report, dry_run)
        if dry_run:
            report.state = "generated_dryrun"
        else:
            report.state = "generated"
        report.state_info = log
        report.save()
    except Exception as e:
        report.state = "invalid"
        report.state_info = f"Fehler beim erstellen des Reports: {e.__class__.__name__}: {e}"
        report.save()
        if settings.DEBUG:
            raise


@shared_task
def regenerate_nk_output(output_type, report_id, item_id):
    try:
        report = Report.objects.get(pk=report_id)
        if output_type == "contract_bill":
            regenerate_bill(report, item_id)
    except Exception:
        if settings.DEBUG:
            raise
