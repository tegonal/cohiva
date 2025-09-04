from django.conf import settings
from django.core.management.base import BaseCommand

from reservation.models import ReservationObject


class Command(BaseCommand):
    help = "Update automatic reservation blockers."

    def handle(self, *args, **options):
        for ro in ReservationObject.objects.filter(reservation_type__active=True):
            print("Updating reservation blockers for %s. (debug=%s)" % (ro, settings.DEBUG))
            ro.update_reservation_blockers()
