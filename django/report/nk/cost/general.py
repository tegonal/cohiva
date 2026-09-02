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
