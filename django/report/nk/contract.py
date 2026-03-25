import datetime
from dataclasses import dataclass

from geno.api_views import Akonto
from geno.models import Contract, InvoiceCategory


@dataclass
class NkContract:
    id: int
    date_start: datetime.date
    date_end: datetime.date
    is_virtual: bool = False
    akonto_paid: float | None = None

    @classmethod
    def from_contract(
        cls, contract: Contract, period_start: datetime.date, period_end: datetime.date
    ):
        return NkContract(
            id=contract.id,
            date_start=(
                contract.billing_date_start if contract.billing_date_start else contract.date
            ),
            date_end=contract.billing_date_end if contract.billing_date_end else contract.date_end,
            akonto_paid=cls._get_akonto_paid(contract, period_start, period_end),
        )

    @classmethod
    def _get_akonto_paid(
        cls, contract: Contract, period_start: datetime.date, period_end: datetime.date
    ):
        ## TODO: Improve this implementation
        akonto_view = Akonto()
        akonto_view.contract_id = contract.id
        akonto_view.billing_period_start = period_start
        akonto_view.billing_period_end = period_end
        akonto_view.invoice_category_nk_ausserordentlich = InvoiceCategory.objects.get(
            name="Nebenkosten Akonto ausserordentlich"
        )
        return akonto_view.get_akonto_for_contract()
