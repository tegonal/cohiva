from django.core.exceptions import ValidationError
from django.utils import timezone

from .base import GenoAdminTestCase
from ..models import Share, Building, Contract, Address, ShareType


class ShareTest(GenoAdminTestCase):
    def test_share_overview(self):
        response = self.client.get("/geno/share/overview/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Summe CHF: 40'500.00", response.content.decode())

    def test_share_detail_selectedContractAndBuilding(self):
        now = timezone.localtime(timezone.now())
        contract = Contract(date=now)
        contract.save()
        building = Building()
        building.save()
        address = Address()
        address.save()

        type = ShareType()
        type.save()

        share = Share(name=address, date=now, share_type=type, value=200, attached_to_contract=contract, attached_to_building=building)
        try:
            share.save()
        except ValidationError:
            return
