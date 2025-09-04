from reservation.models import ReservationObject

from .base import ReservationTestCase


class ReservationsTest(ReservationTestCase):
    # @classmethod
    # def setUpTestData(cls):
    #    super().setUpTestData()
    #    testdata.create_contracts(cls)

    def test_reservation_prices(self):
        ro = ReservationObject.objects.all()
        self.assertEqual(ro.count(), 4)
