import time

from celery.contrib.testing.worker import start_worker

from cohiva.celery import app
from geno.tests.base import BaseTransactionTestCase
from report.models import Report, ReportConfiguration
from report.tasks import generate_nk_report


class ReportTasksTest(BaseTransactionTestCase):
    # @classmethod
    # def setUpClass(cls):
    #    super().setUpClass()
    #    cls.celery_worker = start_worker(app, perform_ping_check=False)
    #    cls.celery_worker.__enter__()
    def setUp(self):
        super().setUp()
        self.celery_worker = start_worker(app, perform_ping_check=False)
        self.celery_worker.__enter__()

    # @classmethod
    # def tearDownClass(cls):
    #    cls.celery_worker.__exit__(None, None, None)
    #    super().tearDownClass()

    def tearDown(self):
        self.celery_worker.__exit__(None, None, None)
        super().tearDown()

    def test_generate_report_unconfigured(self):
        report_config = ReportConfiguration.objects.create(name="Test Config", report_type="NK")
        report = Report.objects.create(name="Test", report_configuration=report_config)
        self.task = generate_nk_report.delay(report.id)
        self.assertEqual(len(self.task.id), 36)

        time.sleep(1)
        result = Report.objects.get(id=report.id)
        self.assertEqual(result.state, "invalid")
        self.assertEqual(
            result.state_info,
            (
                "Fehler beim Erstellen des Reports: "
                "ValueError: Setting Startjahr needs to be an integer"
            ),
        )
