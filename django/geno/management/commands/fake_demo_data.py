import datetime
from random import gauss, randrange

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from geno.models import Address, Member


class Command(BaseCommand):
    help = "Add/manipulate some fake demo data."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Not running in the TEST environment. Not doing anything!")

        self.add_memberships()
        self.add_birth_dates()

    def add_memberships(self):
        base_date = datetime.date(2020, 1, 1)
        days_range = 4 * 365
        for adr in Address.objects.filter(active=True):
            member = None
            if not hasattr(adr, "member"):
                member = Member(name=adr)
            elif adr.member.date_join == datetime.date(2024, 2, 10):
                member = adr.member
            if member:
                random_date = datetime.date.fromordinal(
                    base_date.toordinal() + randrange(days_range)
                )
                member.date_join = random_date
                member.save()
                print(f"Set membership date to {random_date} for {adr}.")

    def add_birth_dates(self):
        mean_date = datetime.date(1985, 1, 1)
        days_sigma = 15 * 365
        for adr in Address.objects.filter(active=True):
            if not adr.date_birth:
                random_date = datetime.date.fromordinal(
                    int(gauss(mean_date.toordinal(), days_sigma))
                )
                adr.date_birth = random_date
                adr.save()
                print(f"Set birth date to {random_date} for {adr}.")
