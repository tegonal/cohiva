import datetime

from django.conf import settings
from django.utils import timezone

from geno.models import Address
from reservation.models import Report, ReportCategory, ReportType, Reservation

from .base import ReservationTestCase


class ReservationModelsTest(ReservationTestCase):
    # @classmethod
    # def setUpTestData(cls):
    #    super().setUpTestData()
    #    geno_testdata.create_users(cls)

    def test_status_date_update(self):
        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)
        date1 = datetime.datetime(2024, 11, 18, 12, 0, 0, tzinfo=self.local_tz)
        report = Report.objects.create(
            name="Test",
            report_type=report_type,
            category=cat1,
            report_date=date1,
            status_date=date1,
        )

        self.assertEqual(report.status, "new")
        self.assertEqual(report.status_date, date1)

        report.text = "Change that does not affect status_date"
        report.save()

        new_report = Report.objects.get(id=report.id)
        self.assertEqual(new_report.text, "Change that does not affect status_date")
        self.assertEqual(new_report.status_date, date1)

        report.status = "open"
        report.save()

        new_report2 = Report.objects.get(id=report.id)
        self.assertEqual(new_report2.status, "open")
        self.assertTrue(new_report2.status_date > date1)

    def test_status_date_update_with_update_fields(self):
        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)
        date1 = datetime.datetime(2024, 11, 18, 12, 0, 0, tzinfo=self.local_tz)
        report = Report.objects.create(
            name="Test",
            report_type=report_type,
            category=cat1,
            report_date=date1,
            status_date=date1,
        )

        self.assertEqual(report.status, "new")
        self.assertEqual(report.status_date, date1)

        report.text = "Change that does not affect status_date"
        report.save(update_fields={"text"})

        new_report = Report.objects.get(id=report.id)
        self.assertEqual(new_report.text, "Change that does not affect status_date")
        self.assertEqual(new_report.status_date, date1)

        report.status = "open"
        report.save(update_fields={"status"})

        new_report2 = Report.objects.get(id=report.id)
        self.assertEqual(new_report2.status, "open")
        self.assertTrue(new_report2.status_date > date1)

    def test_update_reservaton_blockers(self):
        prev_settings = settings.RESERVATION_BLOCKER_RULES
        count_before = (
            Reservation.objects.filter(name=self.reservationobjects["Dachküche"])
            .filter(is_auto_blocker=True)
            .count()
        )
        settings.RESERVATION_BLOCKER_RULES = []
        self.reservationobjects["Dachküche"].update_reservation_blockers()
        count_after = (
            Reservation.objects.filter(name=self.reservationobjects["Dachküche"])
            .filter(is_auto_blocker=True)
            .count()
        )
        self.assertEqual(count_before, count_after)

        adr = Address.objects.create(
            organization="ReservationBlockerTestOrga", name="ReservationBlockerTestName"
        )
        settings.RESERVATION_BLOCKER_RULES = [
            {
                "object": "Dachküche",
                "contact": {
                    "organization": "ReservationBlockerTestOrga",
                    "name": "ReservationBlockerTestName",
                },
                "rule": {
                    "type": "weekly",  # weekly
                    "weekdays": [1, 4],  # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
                    "time_start": "17:00",  # HH:MM
                    "time_end": "23:59",  # HH:MM
                    "summary": "Dachküche - ReservationBlockerTest",
                },
            },
        ]
        self.reservationobjects["Dachküche"].update_reservation_blockers()
        count_after = (
            Reservation.objects.filter(name=self.reservationobjects["Dachküche"])
            .filter(is_auto_blocker=True)
            .count()
        )
        self.assertTrue(count_before < count_after)

        now = timezone.localtime(timezone.now())
        sample_blocker_date = now + datetime.timedelta(days=365)
        while sample_blocker_date.weekday() != 1:
            sample_blocker_date += datetime.timedelta(days=1)
        start = sample_blocker_date.replace(hour=17, minute=0, second=0, microsecond=0)
        end = sample_blocker_date.replace(hour=23, minute=59, second=0, microsecond=0)
        sample_blocker = Reservation.objects.get(
            name=self.reservationobjects["Dachküche"], date_start=start, date_end=end
        )
        self.assertEqual("Dachküche - ReservationBlockerTest", sample_blocker.summary)
        self.assertTrue(sample_blocker.is_auto_blocker)
        self.assertEqual(sample_blocker.contact, adr)
        settings.RESERVATION_BLOCKER_RULES = prev_settings
