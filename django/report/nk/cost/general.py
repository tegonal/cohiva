from typing import TYPE_CHECKING

from .base import NkCost, NkCostValueType

if TYPE_CHECKING:
    from report.nk.generator import NkReportGenerator


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

    def load_input_data(self):
        super().load_input_data()
        self.load_building_totals()
        self.load_rental_unit_usage()
        self.normalize_monthly_amounts()

    def load_building_totals(self):
        self.total_values[NkCostValueType.COST].amount = self.get_total_costs()

    def get_total_costs(self):
        return self.generator.config.get(f"Kosten:{self.name}")

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
            getattr(ru, self.rental_unit_usage) / self.generator.num_months
        ] * self.generator.num_months


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

    Config keys are passed via cost_config:
      fee_per_unit_key   – report config key for the per-unit fee (CHF/month)
      fee_per_person_key – report config key for the per-person fee (CHF/month × min_occupancy)
      fixed_fees_key     – report config key for a dict {rental_unit_name: CHF/month}
    """

    cost_type_id = "per_rental_unit"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.fee_per_unit_key = cost_config.get("fee_per_unit_key")
        self.fee_per_person_key = cost_config.get("fee_per_person_key")
        self.fixed_fees_key = cost_config.get("fixed_fees_key")
        self.fixed_fees = {}

    def load_input_data(self):
        super().load_input_data()
        fee_per_unit = (
            self.generator.config.get(self.fee_per_unit_key, 0) if self.fee_per_unit_key else 0
        )
        fee_per_person = (
            self.generator.config.get(self.fee_per_person_key, 0) if self.fee_per_person_key else 0
        )
        fixed_fees = (
            self.generator.config.get(self.fixed_fees_key, {}) if self.fixed_fees_key else {}
        )

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
