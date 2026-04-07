import datetime

from django.conf import settings
from django.db.models import Q, Sum

from cohiva.utils.countries import normalize_country_code
from finance.accounting import Account, AccountKey
from geno.models import Address, Contract, Invoice, InvoiceCategory
from report.nk.cost import NkCost, NkCostValueType
from report.nk.rental_unit import NkRentalUnit


class NkContract:
    def __init__(self, **kwargs):
        if "id" not in kwargs or "date_start" not in kwargs or "date_end" not in kwargs:
            raise ValueError("Missing required parameters")
        self.id: int = kwargs.get("id")
        self.date_start: datetime.date = kwargs.get("date_start")
        self.date_end: datetime.date = kwargs.get("date_end")
        self.billing_period_start: datetime.date | None = None
        self.billing_period_end: datetime.date | None = None
        self.name: str = kwargs.get("name")
        self.is_virtual: bool = kwargs.get("is_virtual", False)
        self.is_formal: bool = kwargs.get("is_formal", True)
        self.akonto_paid: float = kwargs.get("akonto_paid")
        self.akonto_nominal_per_rental_unit: dict[int, float] = {}
        self.rental_units: list[NkRentalUnit] = kwargs.get("rental_units", [])
        self.geno_contract: Contract = kwargs.get("geno_contract")

        if self.is_virtual:
            self.address = Address.objects.filter(organization=settings.GENO_NAME).first()
            if not self.address and hasattr(settings, "GENO_QRBILL_CREDITOR"):
                self.address = Address.objects.create(
                    organization=settings.GENO_QRBILL_CREDITOR["name"],
                    street_name=settings.GENO_QRBILL_CREDITOR["street"],
                    house_number=settings.GENO_QRBILL_CREDITOR["house_num"],
                    city_zipcode=settings.GENO_QRBILL_CREDITOR["pcode"],
                    city_name=settings.GENO_QRBILL_CREDITOR["city"],
                    country=normalize_country_code(settings.GENO_QRBILL_CREDITOR["country"]),
                    comment="Automatisch erzeugt for NK-Abrechnung",
                )
        elif self.geno_contract:
            self.address = self.geno_contract.get_contact_address()
        else:
            self.address = None

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
            geno_contract=contract,
        )

    @classmethod
    def _get_akonto_paid(
        cls, contract: Contract, period_start: datetime.date, period_end: datetime.date
    ) -> float:
        invoice_category_nk_ausserordentlich = InvoiceCategory.objects.get(
            name="Nebenkosten Akonto ausserordentlich"
        )
        akonto_total = 0
        if contract.id >= 0:
            account = Account.from_settings(AccountKey.NK).set_code(contract=contract)
            # Get payments from contract AND linked contracts in case there are invoices
            # before/after the billing contract has been changed!
            for c in Contract.objects.filter(Q(id=contract.id) | Q(billing_contract=contract)):
                akonto = Invoice.objects.filter(
                    contract=c,
                    fin_account=account.code,
                    date__gte=period_start,
                    date__lte=period_end,
                ).aggregate(Sum("amount"))
                if akonto["amount__sum"]:
                    akonto_total += akonto["amount__sum"]
            # Ausserordentliche Akonto-Zahlungen
            for c in Contract.objects.filter(Q(id=contract.id) | Q(billing_contract=contract)):
                akonto = Invoice.objects.filter(
                    contract=c,
                    invoice_category=invoice_category_nk_ausserordentlich,
                    invoice_type="Invoice",
                    date__gte=period_start,
                    date__lte=period_end,
                ).aggregate(Sum("amount"))
                if akonto["amount__sum"]:
                    akonto_total += akonto["amount__sum"]
        return float(akonto_total)

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
        objects = [str(ru.id) for ru in self.rental_units]
        count = len(objects)
        if count > max_items:
            return delimiter.join(objects[0:max_items]) + f"_und_{count - max_items}_Weitere"
        else:
            return delimiter.join(objects)

    def update_context(self, context, costs: list[NkCost]):
        total_bill_amount = self.get_total_costs(costs)
        if self.akonto_paid:
            total_bill_amount -= self.akonto_paid
        if self.address:
            context.update(self.address.get_context())
        context.update(
            {
                "contract_id": self.id,
                "Euer": "Ihr" if self.is_formal else "Dein/Euer",
                "contract_info": self.get_contract_info(),
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
        if self.billing_period_start and self.billing_period_end:
            context["contract_period"] = "%s – %s" % (
                self.billing_period_start.strftime("%d.%m.%Y"),
                self.billing_period_end.strftime("%d.%m.%Y"),
            )
        else:
            context["contract_period"] = "unbekannt"
        if self.name:
            context["obj_info_str"] = f"{self.name}_{self.get_ru_list_string()}"
        else:
            context["obj_info_str"] = self.get_ru_list_string()

    def is_active_on(self, date: datetime.date):
        return self.date_start <= date and (not self.date_end or date <= self.date_end)

    def add_rental_unit(self, ru: NkRentalUnit):
        if ru not in self.rental_units:
            self.rental_units.append(ru)

    def assign_rental_unit_month(self, ru: NkRentalUnit, date: dict[str, datetime.date]):
        self.add_rental_unit(ru)
        if ru.akonto:
            if ru.id not in self.akonto_nominal_per_rental_unit:
                self.akonto_nominal_per_rental_unit[ru.id] = 0
            self.akonto_nominal_per_rental_unit[ru.id] += ru.akonto
        if not self.billing_period_start:
            self.billing_period_start = date["start"]
        if not self.billing_period_end or date["end"] > self.billing_period_end:
            self.billing_period_end = date["end"]

    @property
    def akonto_nominal(self):
        return sum(self.akonto_nominal_per_rental_unit.values())

    def get_total_costs(self, costs: list[NkCost], rental_unit: NkRentalUnit | None = None):
        ret = 0
        for cost in costs:
            ret += cost.get_assigned_amount(NkCostValueType.COST, self, rental_unit)
        return ret

    def get_paid_akonto(self, ru: NkRentalUnit) -> float:
        """Return the paid akonto for the given rental unit.
        Since only the total paid amount is known, the amount per unit is scaled accordingly if
        the total paid amount differs from the total nominal amount
        """
        if self.akonto_nominal and self.akonto_paid:
            nominal_for_unit = self.akonto_nominal_per_rental_unit.get(ru.id, 0.0)
            return nominal_for_unit * self.akonto_paid / self.akonto_nominal
        return 0.0
