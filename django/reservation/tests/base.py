import geno.tests.data as geno_testdata
import reservation.tests.data as reservation_testdata
from geno.tests.base import BaseTestCase


class ReservationTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_prototype_users(cls)
        reservation_testdata.create_reservationobjects(cls)
