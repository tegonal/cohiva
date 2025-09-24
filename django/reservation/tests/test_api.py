import datetime
from io import BytesIO
from unittest import skip

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

import cohiva.base_config as cbc
from reservation.models import Report, ReportCategory, ReportPicture, ReportType, Reservation

from .base import ReservationTestCase


class ReservationTypeAPITests(APITestCase, ReservationTestCase):
    def get(self, username):
        self.client.login(username=username, password="secret")
        url = reverse("reservationtype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def check_rooms(self, results, expected):
        for r in results:
            if r["name"] not in expected:
                print(f"{r['name']} not found in {expected}")
                return False
        return True

    def test_get_unauthenticated(self):
        url = reverse("reservationtype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get(self):
        response = self.get("user.external")
        self.assertTrue(response.data["count"] == 1)
        for key in (
            "id",
            "name",
            "fixed_time",
            "default_time_start",
            "default_time_end",
            "summary_required",
            "required_role",
        ):
            self.assertTrue(key in response.data["results"][0])
        self.assertTrue(self.check_rooms(response.data["results"], ("Sitzungszimmer")))
        self.assertEqual(response.data["results"][0]["required_role"], "user")

    def test_get_filter_inactive(self):
        response = self.get("user.inactive")
        self.assertEqual(response.data["count"], 0)

    def test_get_filter_roles(self):
        response = self.get("user.tenant")
        self.assertEqual(response.data["count"], 2)
        self.assertTrue(
            self.check_rooms(response.data["results"], ("Sitzungszimmer", "Werkstatt"))
        )

        response = self.get("user.member")
        self.assertEqual(response.data["count"], 2)
        self.assertTrue(
            self.check_rooms(response.data["results"], ("Sitzungszimmer", "Dachküche"))
        )

        response = self.get("user.renter")
        self.assertEqual(response.data["count"], 4)
        self.assertTrue(
            self.check_rooms(
                response.data["results"],
                ("Sitzungszimmer", "Dachküche", "Werkstatt", "Gästezimmer"),
            )
        )

        response = self.get("user.renter_nonmember")
        self.assertEqual(response.data["count"], 3)
        self.assertTrue(
            self.check_rooms(
                response.data["results"], ("Sitzungszimmer", "Werkstatt", "Gästezimmer")
            )
        )


class ReservationAPITests(APITestCase, ReservationTestCase):
    def get(self, username):
        self.client.login(username=username, password="secret")
        url = reverse("reservation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_unauthenticated(self):
        url = reverse("reservation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty(self):
        response = self.get("user.external")
        self.assertEqual(response.data["count"], 0)

    def test_get_own(self):
        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["external"]["address"],
            date_start=datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 1, 17, 0, 0, tzinfo=self.local_tz),
        )

        response = self.get("user.external")
        self.assertTrue(response.data["count"] == 1)
        for key in (
            "id",
            "name",
            "reservation_type",
            "date_start",
            "date_end",
            "can_edit",
            "summary",
        ):
            self.assertTrue(key in response.data["results"][0])
        self.assertFalse(response.data["results"][0]["can_edit"])
        # print(response.data)

    def test_filters(self):
        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["external"]["address"],
            date_start=datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 1, 17, 0, 0, tzinfo=self.local_tz),
        )
        response = self.get("user.member")
        self.assertEqual(response.data["count"], 0)

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 2, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 2, 17, 0, 0, tzinfo=self.local_tz),
            state="deleted",
        )
        response = self.get("user.member")
        self.assertEqual(response.data["count"], 0)

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 3, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 3, 17, 0, 0, tzinfo=self.local_tz),
            state="cancelled",
        )
        response = self.get("user.member")
        self.assertEqual(response.data["count"], 0)

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 4, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 4, 17, 0, 0, tzinfo=self.local_tz),
            state="approved",
        )
        response = self.get("user.member")
        self.assertEqual(response.data["count"], 1)

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 5, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 5, 17, 0, 0, tzinfo=self.local_tz),
            state="new",
        )
        response = self.get("user.member")
        self.assertEqual(response.data["count"], 2)

        self.reservationtypes["Sitzungszimmer"].active = False
        self.reservationtypes["Sitzungszimmer"].save()

        response = self.get("user.member")
        self.assertEqual(response.data["count"], 0)

    def test_cors_enabled(self):
        """Make sure CORS is enabled a given endpoint
        # Technique inspired from https://stackoverflow.com/a/47609921
        """
        self.client.login(username="user.renter", password="secret")
        url = reverse("reservation-list")
        request_headers = {
            "HTTP_ACCESS_CONTROL_REQUEST_METHOD": "GET",
            "HTTP_ORIGIN": "http://somethingelse.com",
        }
        response = self.client.get(url, {}, **request_headers)
        self.assertFalse(response.has_header("Access-Control-Allow-Origin"))

        request_headers["HTTP_ORIGIN"] = "https://app." + cbc.DOMAIN
        response = self.client.get(url, {}, **request_headers)
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "https://app." + cbc.DOMAIN
        )
        self.assertTrue(response.headers["Access-Control-Allow-Credentials"])


class ReservationSearchAPITests(APITestCase, ReservationTestCase):
    def test_get_unauthenticated(self):
        url = reverse("reservation-search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_query(self):
        self.client.login(username="user.external", password="secret")
        url = reverse("reservation-search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        ## TODO: Change this to error?
        response = self.client.get(url, {"reservationType": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        response = self.client.get(url, {"reservationType": "Sitzungszimmer"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            url, {"reservationType": "Sitzungszimmer", "dateFrom": "01.01.2000"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
                "timeTo": "invalid",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
                "timeTo": "18:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        for key in ("id", "title", "subtitle", "costs", "text", "isAvailable", "unavailableDate"):
            self.assertTrue(key in response.data[0])
        self.assertEqual(response.data[0]["title"], "Sitzungszimmer gross")

    def test_not_permitted(self):
        self.client.login(username="user.inactive", password="secret")
        url = reverse("reservation-search")

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
                "timeTo": "18:00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_availability(self):
        self.client.login(username="user.external", password="secret")
        url = reverse("reservation-search")
        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
                "timeTo": "18:00",
            },
        )
        self.assertTrue(response.data[0]["isAvailable"])

        res = Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 1, 15, 0, 0, tzinfo=self.local_tz),
            state="cancelled",
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
                "timeTo": "18:00",
            },
        )
        self.assertTrue(response.data[0]["isAvailable"])

        res.state = "approved"
        res.save()

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "13:00",
                "timeTo": "18:00",
            },
        )
        self.assertFalse(response.data[0]["isAvailable"])
        self.assertEqual(
            response.data[0]["unavailableDate"], "01.01.2000 12:00 bis 01.01.2000 15:00"
        )

    def test_timezone_dst_winter(self):
        self.client.login(username="user.external", password="secret")
        url = reverse("reservation-search")

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 1, 14, 45, 0, tzinfo=self.local_tz),
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "15:00",
                "timeTo": "18:00",
            },
        )
        self.assertTrue(response.data[0]["isAvailable"])

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 1, 1, 14, 45, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 1, 1, 15, 15, 0, tzinfo=self.local_tz),
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.01.2000",
                "dateTo": "01.01.2000",
                "timeFrom": "15:00",
                "timeTo": "18:00",
            },
        )
        self.assertFalse(response.data[0]["isAvailable"])
        self.assertEqual(
            response.data[0]["unavailableDate"], "01.01.2000 00:00 bis 01.01.2000 15:15"
        )

    def test_timezone_dst_sommer(self):
        self.client.login(username="user.external", password="secret")
        url = reverse("reservation-search")

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 7, 1, 0, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 7, 1, 14, 45, 0, tzinfo=self.local_tz),
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.07.2000",
                "dateTo": "01.07.2000",
                "timeFrom": "15:00",
                "timeTo": "18:00",
            },
        )
        self.assertTrue(response.data[0]["isAvailable"])

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2000, 7, 1, 14, 45, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2000, 7, 1, 15, 15, 0, tzinfo=self.local_tz),
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "01.07.2000",
                "dateTo": "01.07.2000",
                "timeFrom": "15:00",
                "timeTo": "18:00",
            },
        )
        self.assertFalse(response.data[0]["isAvailable"])
        self.assertEqual(
            response.data[0]["unavailableDate"], "01.07.2000 00:00 bis 01.07.2000 15:15"
        )

    def test_timezone_dst_edge(self):
        self.client.login(username="user.external", password="secret")
        url = reverse("reservation-search")

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2025, 3, 29, 0, 0, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2025, 3, 29, 17, 45, 0, tzinfo=self.local_tz),
        )

        Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2025, 3, 30, 6, 15, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2025, 3, 30, 12, 0, 0, tzinfo=self.local_tz),
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "29.03.2025",
                "dateTo": "30.03.2025",
                "timeFrom": "18:00",
                "timeTo": "06:00",
            },
        )
        self.assertTrue(response.data[0]["isAvailable"])

        res3 = Reservation.objects.create(
            name=self.reservationobjects["Sitzungszimmer gross"],
            contact=self.prototypes["member"]["address"],
            date_start=datetime.datetime(2025, 3, 29, 17, 45, 0, tzinfo=self.local_tz),
            date_end=datetime.datetime(2025, 3, 29, 18, 15, 0, tzinfo=self.local_tz),
        )

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "29.03.2025",
                "dateTo": "30.03.2025",
                "timeFrom": "18:00",
                "timeTo": "06:00",
            },
        )
        self.assertEqual(
            response.data[0]["unavailableDate"], "29.03.2025 00:00 bis 29.03.2025 18:15"
        )

        res3.date_start = datetime.datetime(2025, 3, 30, 5, 45, 0, tzinfo=self.local_tz)
        res3.date_end = datetime.datetime(2025, 3, 30, 6, 15, 0, tzinfo=self.local_tz)
        res3.save()

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "29.03.2025",
                "dateTo": "30.03.2025",
                "timeFrom": "18:00",
                "timeTo": "06:00",
            },
        )
        self.assertEqual(
            response.data[0]["unavailableDate"], "30.03.2025 05:45 bis 30.03.2025 12:00"
        )

        res3.date_start = datetime.datetime(2025, 3, 29, 17, 45, 0, tzinfo=self.local_tz)
        res3.date_end = datetime.datetime(2025, 3, 30, 6, 15, 0, tzinfo=self.local_tz)
        res3.save()

        response = self.client.get(
            url,
            {
                "reservationType": "Sitzungszimmer",
                "dateFrom": "29.03.2025",
                "dateTo": "30.03.2025",
                "timeFrom": "18:00",
                "timeTo": "06:00",
            },
        )
        self.assertEqual(
            response.data[0]["unavailableDate"], "29.03.2025 00:00 bis 30.03.2025 12:00"
        )


class ReservationEditAPITests(APITestCase, ReservationTestCase):
    def test_post_unauthenticated(self):
        url = reverse("reservation-edit")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_and_cancel(self):
        self.client.login(username="user.external", password="secret")
        url = reverse("reservation-edit")

        response = self.client.post(url, {"invalid": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {"action": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {"action": "add"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        request_data = {
            "action": "add",
            "reservationType": "Sitzungszimmer",
            "dateFrom": "01.01.2000",
            "dateTo": "01.01.2000",
            "timeFrom": "13:00",
            "timeTo": "18:00",
            "selectedRoom": self.reservationobjects["Sitzungszimmer gross"].id,
            "summary": "Test-Summary",
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")
        self.assertEqual(response.data["msg"], "Datum liegt in der Vergangenheit.")

        self.assertEqual(Reservation.objects.count(), 0)

        request_data["dateFrom"] = "01.01.2100"
        request_data["dateTo"] = "01.01.2100"
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        self.assertEqual(Reservation.objects.count(), 1)
        res = Reservation.objects.all()[0]
        self.assertEqual(res.name, self.reservationobjects["Sitzungszimmer gross"])
        self.assertEqual(res.contact, self.prototypes["external"]["address"])
        self.assertEqual(res.date_start, datetime.datetime(2100, 1, 1, 13, tzinfo=self.local_tz))
        self.assertEqual(res.date_end, datetime.datetime(2100, 1, 1, 18, tzinfo=self.local_tz))
        self.assertEqual(res.state, "new")
        self.assertEqual(res.summary, "Test-Summary")

        response = self.client.post(url, {"action": "cancel"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {"action": "cancel", "reservationId": res.id + 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {"action": "cancel", "reservationId": res.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")
        res2 = Reservation.objects.all()[0]
        self.assertEqual(res2.state, "cancelled")

    def test_add_with_confirmation_email(self):
        self.client.login(username="user.renter", password="secret")
        url = reverse("reservation-edit")

        request_data = {
            "action": "add",
            "reservationType": "Gästezimmer",
            "dateFrom": "01.01.2100",
            "dateTo": "02.01.2100",
            "timeFrom": "13:00",
            "timeTo": "18:00",
            "selectedRoom": self.reservationobjects["Gästezimmer A"].id,
            "summary": "Test-Summary",
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        self.assertEqual(Reservation.objects.count(), 1)
        res = Reservation.objects.all()[0]
        self.assertEqual(res.name, self.reservationobjects["Gästezimmer A"])
        self.assertEqual(res.contact, self.prototypes["renter"]["address"])
        self.assertEqual(res.date_start, datetime.datetime(2100, 1, 1, 13, tzinfo=self.local_tz))
        self.assertEqual(res.date_end, datetime.datetime(2100, 1, 2, 18, tzinfo=self.local_tz))
        self.assertEqual(res.state, "approved")

        self.assertEmailSent(
            1,
            "Bestätigung Reservation Gästezimmer A",
            f"Reservations-Bestätigung:\n\nBezeichnung: Gästezimmer A\nVon: 01.01.2100 13:00\nBis: 02.01.2100 18:00\nReservationsnummer: {res.id}",
            "renter_first renter",
        )


class ReportSubmissionAPITests(APITestCase, ReservationTestCase):
    def test_get_unauthenticated(self):
        url = reverse("report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_unauthenticated(self):
        url = reverse("report")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get(self):
        self.client.login(username="user.renter", password="secret")

        url = reverse("report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["report_type"], 1)
        self.assertEqual(response.data["categories"], [])
        self.assertEqual(response.data["contact"], "renter_first renter, renter@example.com")
        self.assertEqual(response.data["rental_units"][0]["label"], "Test Wohnung (Test)")

        ReportCategory.objects.create(name="Kat1", report_type=report_type)
        ReportCategory.objects.create(name="Kat2", report_type=report_type)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["categories"][0]["label"], "Kat1")
        self.assertEqual(response.data["categories"][1]["label"], "Kat2")

    def test_post(self):
        self.client.login(username="user.renter", password="secret")
        url = reverse("report")

        request_data = {
            #'action': "add",
            "unit": "__OTHER__",
            "category": "INVALID",
            "subject": "Test-Subject",
            "contact_text": "Test-Contact",
            "text": "Test-Text",
            #'pictures':
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")

        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

        request_data["category"] = 1

        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)
        request_data["category"] = cat1.id

        self.assertEqual(Report.objects.count(), 0)

        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        self.assertEqual(Report.objects.count(), 1)

        rep = Report.objects.all()[0]
        self.assertEqual(rep.name, "Test-Subject")
        self.assertEqual(rep.report_type, report_type)
        self.assertEqual(rep.category, cat1)
        self.assertEqual(rep.rental_unit, None)
        self.assertEqual(rep.contact, self.prototypes["renter"]["address"])
        self.assertEqual(rep.contact_text, "Test-Contact")
        self.assertEqual(rep.text, "Test-Text")
        self.assertEqual(rep.report_date.date(), timezone.now().date())
        self.assertEqual(rep.status_date.date(), timezone.now().date())
        self.assertEqual(rep.status, "new")

        self.assertEmailSent(
            1,
            "Reparaturmeldung: 000/renter, renter_first - Test-Subject",
            "Es wurde folgende Meldung im System registriert:",
            sender=f'"Cohiva {settings.COHIVA_SITE_NICKNAME}" <{settings.GENO_DEFAULT_EMAIL}>',
        )

    def test_post_with_rental_unit(self):
        self.client.login(username="user.renter", password="secret")
        url = reverse("report")

        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)

        request_data = {
            #'action': "add",
            "unit": "INVALID",
            "category": cat1.id,
            "subject": "Test-Subject",
            "contact_text": "Test-Contact",
            "text": "Test-Text",
            #'pictures':
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

        request_data["unit"] = self.prototypes["renter"]["rental_unit"].id + 100

        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

        request_data["unit"] = self.prototypes["renter"]["rental_unit"].id

        self.assertEqual(Report.objects.count(), 0)

        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        self.assertEqual(Report.objects.count(), 1)

        rep = Report.objects.all()[0]
        self.assertEqual(rep.rental_unit, self.prototypes["renter"]["rental_unit"])

        self.assertEmailSent(
            1,
            "Reparaturmeldung: Test/renter, renter_first - Test-Subject",
            "Es wurde folgende Meldung im System registriert:",
        )

    def test_post_with_pictures_duplicate_name(self):
        self.client.login(username="user.renter", password="secret")
        url = reverse("report")

        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)

        request_data = {
            #'action': "add",
            "unit": "__OTHER__",
            "category": cat1.id,
            "subject": "Test-Subject",
            "contact_text": "Test-Contact",
            "text": "Test-Text",
            "pictures": ["Name", "Name"],
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

    @skip("Need to implement checks for invalid files first")
    def test_post_with_pictures_invalid(self):
        self.client.login(username="user.renter", password="secret")
        url = reverse("report")

        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)

        request_data = {
            #'action': "add",
            "unit": "__OTHER__",
            "category": cat1.id,
            "subject": "Test-Subject",
            "contact_text": "Test-Contact",
            "text": "Test-Text",
            "pictures": ["Invalid"],
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ERROR")

    def test_post_with_pictures(self):
        self.client.login(username="user.renter", password="secret")
        url = reverse("report")

        report_type = ReportType.objects.create(id=1, name="Reparaturmeldung")
        cat1 = ReportCategory.objects.create(name="Kat1", report_type=report_type)

        pic1 = BytesIO(
            b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00"
        )
        pic1.name = "Picture1.gif"
        pic2 = BytesIO(
            b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00"
        )
        pic2.name = "Picture2.gif"

        self.assertEqual(Report.objects.count(), 0)
        self.assertEqual(ReportPicture.objects.count(), 0)

        request_data = {
            #'action': "add",
            "unit": "__OTHER__",
            "category": cat1.id,
            "subject": "Test-Subject",
            "contact_text": "Test-Contact",
            "text": "Test-Text",
            "pictures": [pic1, pic2],
        }
        response = self.client.post(url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "OK")

        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(ReportPicture.objects.count(), 2)

        rep = Report.objects.all()[0]

        count = 1
        for ri in ReportPicture.objects.all():
            self.assertEqual(ri.report, rep)
            self.assertEqual(ri.name, f"000_Meldung-{rep.id}_Bild-{count}")
            self.assertEqual(
                ri.image.name,
                f"report/images/000_Meldung-{rep.id}_Bild-{count}_Picture{count}.gif",
            )
            self.assertEqual(ri.image.size, 35)
            count += 1
