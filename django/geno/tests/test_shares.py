from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from ..models import Address, Building, Contract, Share, ShareType
from .base import GenoAdminTestCase


class ShareTest(GenoAdminTestCase):
    def test_share_overview(self):
        response = self.client.get("/geno/share/overview/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Summe CHF: 40'500.00", response.content.decode())

    def test_share_detail_selectedContractAndBuilding(self):
        now = timezone.now()
        contract = Contract.objects.create(date=now)
        building = Building.objects.create()
        address = Address.objects.create()
        sharetype = ShareType.objects.create()

        # Check model constraint
        constraint_name = "geno_share_attached_to_building_or_contract"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Share.objects.create(
                name=address,
                date=now,
                share_type=sharetype,
                value=200,
                attached_to_contract=contract,
                attached_to_building=building,
            )

        # Check form validation
        with self.assertRaises(ValidationError):
            share = Share(
                name=address,
                date=now,
                share_type=sharetype,
                value=200,
                attached_to_contract=contract,
                attached_to_building=building,
            )
            share.clean()
