from typing import TYPE_CHECKING

from geno.utils import nformat

from .base import NkCost, NkCostValueType

if TYPE_CHECKING:
    from report.nk.generator import NkContract, NkRentalUnit, NkReportGenerator


class NkTotalCost(NkCost):
    """Total costs (one number) that are distributed with a simple key."""

    cost_type_id = "simple_total"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.rental_unit_usage = cost_config.get("object_weights", "area")
        ## TODO: Get name and unit also from config?
        if self.rental_unit_usage == "area":
            self.add_value_type(NkCostValueType.USAGE, "Fläche", "m2")
        elif self.rental_unit_usage == "volume":
            self.add_value_type(NkCostValueType.USAGE, "Volumen", "m3")
        else:
            self.add_value_type(NkCostValueType.USAGE, "Faktor", "")
        self._total_amount = cost_config.get("Betrag", 0)

    def load_input_data(self):
        super().load_input_data()
        self.load_building_totals()
        self.load_rental_unit_usage()
        self.normalize_monthly_amounts()

    def load_building_totals(self):
        self.total_values[NkCostValueType.COST].amount = self.get_total_costs()

    def get_total_costs(self):
        return self._total_amount

    def load_rental_unit_usage(self):
        # We use the weights as usage
        self._calculate_weights()
        for ru in self.generator.rental_units:
            weight = self.rental_unit_values[ru.id][NkCostValueType.WEIGHT].amount
            self.rental_unit_values[ru.id][NkCostValueType.USAGE].amount = weight
            self.section_values[ru.section.id][NkCostValueType.USAGE].amount += weight
            self.total_values[NkCostValueType.USAGE].amount += weight

    def get_rental_unit_weights(self, ru):
        """Use the usage as weight."""
        if self.rental_unit_usage == "uniform":
            ## The base class returns uniform weights
            return super().get_rental_unit_weights(ru)
        return [
            ru.get_weight(self.rental_unit_usage) / self.generator.num_months
        ] * self.generator.num_months

    def get_assigned_usage(
        self, contract: "NkContract", rental_unit: "NkRentalUnit | None" = None
    ):
        return self._get_assigned_amount(NkCostValueType.USAGE, contract, rental_unit)

    def get_building_usage(self):
        return self._get_building_amount(NkCostValueType.USAGE)

    def _get_context(self, ru: "NkRentalUnit", contract: "NkContract") -> dict:
        ctx = super()._get_context(ru, contract)
        amount = self.get_assigned_cost(contract, ru)
        usage = self.get_assigned_usage(contract, ru)
        building_amount = self.get_building_cost()
        building_usage = self.get_building_usage()
        ctx.update(
            {
                "name": self.name,
                "chf": nformat(amount),
                "chft": nformat(building_amount),
                "use": nformat(usage),
                "uset": nformat(building_usage),
                "eh": nformat(building_amount / building_usage),
                "include_in_details": True,
            }
        )
        return ctx

    def update_context(
        self, ru: "NkRentalUnit", contract: "NkContract", context: dict, aggregated_values: dict
    ) -> None:
        context["section_details"] = True


class NkMonthlyCost(NkCost):
    """Monthly costs that are distributed with a simple key."""

    cost_type_id = "simple_monthly"


class NkTotalEnergyCost(NkCost):
    """Energy costs that are distributed with a simple key."""

    cost_type_id = "energy"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.base_cost_factor = 0.3  # default 30/70% split
        self.base_cost_object_weights = None
        self.usage_cost_object_weights = None
        self.add_value_type(NkCostValueType.USAGE, "Verbrauch", "kWh")


class NkPerRentalUnitCost(NkCost):
    """Costs calculated individually per rental unit based on per-unit and per-person fees.

    - If the rental unit has a fixed fee (looked up by name), use that.
    - Otherwise, if the unit has a min_occupancy, the cost is:
        fee_per_unit + min_occupancy * fee_per_person
    - Monthly amounts are scaled by the monthly weights.

    Config is passed via cost_config:
      fee_per_unit   – the per-unit fee (CHF/month)
      fee_per_person – the per-person fee (CHF/month × min_occupancy)
      fixed_fees     – a dict {rental_unit_name: CHF/month}
    """

    cost_type_id = "per_rental_unit"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.fee_per_unit = cost_config.get("fee_per_unit")
        self.fee_per_person = cost_config.get("fee_per_person")
        self.fixed_fees = cost_config.get("fixed_fees")

    def load_input_data(self):
        super().load_input_data()
        fee_per_unit = self.fee_per_unit or 0
        fee_per_person = self.fee_per_person or 0
        fixed_fees = self.fixed_fees or {}

        monthly_weights = self.get_monthly_weights()

        for ru in self.generator.rental_units:
            if ru.is_virtual:
                chf_per_month = 0
            elif ru.name in fixed_fees:
                chf_per_month = fixed_fees[ru.name]
            elif ru.min_occupancy:
                chf_per_month = fee_per_unit + ru.min_occupancy * fee_per_person
            else:
                chf_per_month = 0

            monthly_amounts = [mw * chf_per_month for mw in monthly_weights]
            self.rental_unit_values[ru.id][NkCostValueType.COST].monthly_amounts = monthly_amounts
            self.rental_unit_values[ru.id][NkCostValueType.COST].amount = sum(monthly_amounts)

    def split_costs(self):
        self._calculate_weights()
        self._aggregate_monthly_amounts()
