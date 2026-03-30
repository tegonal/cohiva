import datetime
from dataclasses import dataclass

from geno.api_views import Akonto
from geno.models import Contract, InvoiceCategory
from report.nk.cost import NkCost, NkCostValueType
from report.nk.rental_unit import NkRentalUnit


@dataclass
class NkContract:
    id: int
    name: str | None = None
    date_start: datetime.date
    date_end: datetime.date
    period_start: datetime.date | None = None
    period_end: datetime.date | None = None
    is_virtual: bool = False
    is_formal: bool = True
    akonto_paid: float | None = None
    rental_units: list[NkRentalUnit] | None = None
    assigned_rental_unit_per_month: dict[int, NkRentalUnit] | None = None

    @classmethod
    def from_contract(
        cls, contract: Contract, period_start: datetime.date, period_end: datetime.date
    ):
        adr = contract.get_contact_address()
        if adr:
            is_formal = adr.formal == "Sie"
        else:
            is_formal = True
        return NkContract(
            id=contract.id,
            date_start=(
                contract.billing_date_start if contract.billing_date_start else contract.date
            ),
            date_end=contract.billing_date_end if contract.billing_date_end else contract.date_end,
            akonto_paid=cls._get_akonto_paid(contract, period_start, period_end),
            is_formal=is_formal,
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

    def __str__(self):
        if self.is_virtual:
            return "virtual%s" % str(self.id)
        return str(self.id)

    def get_contract_info(self):
        if self.is_virtual:
            return self.__str__()
        try:
            return "%05d" % int(self.id)
        except ValueError:
            return self.id

    def get_ru_list_string(self, max_items=8, delimiter="_"):
        objects = [str(ru.id) for ru in self.rental_units or []]
        count = len(objects)
        if count > max_items:
            return delimiter.join(objects[0:max_items]) + f"_und_{count - max_items}_Weitere"
        else:
            return delimiter.join(objects)

    def update_context(self, context, costs: list[NkCost]):
        total_bill_amount = self.get_total_costs(costs) - self.akonto_paid
        context.update(
            {
                "contract_id": self.id,
                "Euer": "Ihr" if self.is_formal else "Dein/Euer",
                "contract_info": self.get_contract_info(),
                "contract_period": "%s – %s"
                % (
                    self.period_start.strftime("%d.%m.%Y"),
                    self.period_end.strftime("%d.%m.%Y"),
                ),
                "total_akonto": self.akonto_paid,
                "bill_lines": [],
                "total_amount": round(total_bill_amount, 2),
                "akonto_threshold": 10,  # Abweichung in Prozent für Empfehlung Anpassung Akonto
                "akonto_change": round(total_bill_amount / context["num_months"], 0),
                "akonto_change_sum": round(
                    total_bill_amount / context["num_months"] * context["num_months_passed"], 0
                ),
                "comment": f"NK {context['billing_period']} {self.get_ru_list_string(delimiter='/')}",
            }
        )
        if self.name:
            context["obj_info_str"] = f"{self.name}_{self.get_ru_list_string()}"
        else:
            context["obj_info_str"] = self.get_ru_list_string()

    def is_active_on(self, date: datetime.date):
        return self.date_start <= date and (not self.date_end or date <= self.date_end)

    def add_rental_unit(self, ru: NkRentalUnit):
        if self.rental_units is None:
            self.rental_units = []
        self.rental_units.append(ru)

    def assign_month(self, month_index: int, ru: NkRentalUnit):
        if self.assigned_rental_unit_per_month is None:
            self.assigned_rental_unit_per_month = {}
        self.assigned_rental_unit_per_month[month_index] = ru

    def get_total_costs(self, costs: list[NkCost], rental_unit: NkRentalUnit | None = None):
        ret = 0
        for cost in costs:
            ret += cost.get_assigned_amount(NkCostValueType.COST, self, rental_unit)
        return ret
