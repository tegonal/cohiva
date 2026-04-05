from typing import TYPE_CHECKING

from .base import NkCost, NkCostValueType

if TYPE_CHECKING:
    from report.nk.generator import NkReportGenerator


class NkTotalCost(NkCost):
    """Total costs (one number) that are distributed with a simple key."""

    cost_type_id = "simple_total"

    def __init__(self, report: "NkReportGenerator", cost_config: dict):
        super().__init__(report, cost_config)
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
        self.total_values[NkCostValueType.COST].amount = self.report.config.get(
            f"Kosten:{self.name}"
        )
        self.load_rental_unit_usage()
        self.normalize_monthly_amounts()

    def load_rental_unit_usage(self):
        for ru in self.report.rental_units:
            weight = getattr(ru, self.rental_unit_usage)
            self.rental_unit_values[ru.id][NkCostValueType.USAGE].amount = weight
            self.section_values[ru.section.id][NkCostValueType.USAGE].amount += weight
            self.total_values[NkCostValueType.USAGE].amount += weight

    def get_rental_unit_weights(self, ru_id):
        """Use the usage as weight."""
        return self.rental_unit_values[ru_id][NkCostValueType.USAGE].monthly_amounts


class NkCostPerRentalUnit(NkCost):
    """Costs calculated individually per rental unit based on per-unit and per-person fees.

    Mirrors the logic from the old report_nk.internetrechnung():
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

    def __init__(self, report: "NkReportGenerator", cost_config: dict):
        super().__init__(report, cost_config)
        self.fee_per_unit_key = cost_config.get("fee_per_unit_key")
        self.fee_per_person_key = cost_config.get("fee_per_person_key")
        self.fixed_fees_key = cost_config.get("fixed_fees_key")

    def load_input_data(self):
        super().load_input_data()
        fee_per_unit = self.report.config.get(self.fee_per_unit_key, 0) if self.fee_per_unit_key else 0
        fee_per_person = self.report.config.get(self.fee_per_person_key, 0) if self.fee_per_person_key else 0
        fixed_fees = self.report.config.get(self.fixed_fees_key, {}) if self.fixed_fees_key else {}

        monthly_weights = self.get_monthly_weights()

        for ru in self.report.rental_units:
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
        """Aggregate pre-calculated per-rental-unit costs up to sections and total."""
        for ru in self.report.rental_units:
            for month in range(self.report.num_months):
                amount = self.rental_unit_values[ru.id][NkCostValueType.COST].monthly_amounts[month]
                self.section_values[ru.section.id][NkCostValueType.COST].monthly_amounts[month] += amount
                self.total_values[NkCostValueType.COST].monthly_amounts[month] += amount

        for section in self.report.sections:
            self.section_values[section.id][NkCostValueType.COST].amount = sum(
                self.section_values[section.id][NkCostValueType.COST].monthly_amounts
            )
        self.total_values[NkCostValueType.COST].amount = sum(
            self.total_values[NkCostValueType.COST].monthly_amounts
        )


class NkMonthlyCost(NkCost):
    """Monthly costs that are distributed with a simple key."""

    cost_type_id = "simple_monthly"


class NkTotalEnergyCost(NkCost):
    """Energy costs that are distributed with a simple key."""

    cost_type_id = "energy"

    def __init__(self, report: "NkReportGenerator", cost_config: dict):
        super().__init__(report, cost_config)
        self.base_cost_factor = 0.3  # default 30/70% split
        self.base_cost_object_weights = None
        self.usage_cost_object_weights = None
        self.add_value_type(NkCostValueType.USAGE, "Verbrauch", "kWh")
