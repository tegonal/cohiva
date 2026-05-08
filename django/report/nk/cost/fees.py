from typing import TYPE_CHECKING

from ..rental_unit import NkRentalUnit
from .base import NkCost, NkCostValueType

if TYPE_CHECKING:
    from report.nk.generator import NkReportGenerator


class NkAdminFeeCost(NkCost):
    """Admin fees as a percentage of the total costs."""

    cost_type_id = "admin_fee"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.fee_percentage = float(
            report_generator.config.get(cost_config.get("fee_percentage_key"), 0.0)
        )

    def update(self):
        super().update()

        for ru in self.generator.rental_units:
            self.rental_unit_values[ru.id][
                NkCostValueType.COST
            ].amount = self._calculate_fees_for_rental_unit(ru, self.generator.costs)

        self.normalize_monthly_amounts()
        self._calculate_weights()
        self._aggregate_monthly_amounts()

    def _calculate_fees_for_rental_unit(self, ru: NkRentalUnit, costs: list[NkCost]) -> float:
        if ru.is_virtual:
            return 0.0

        total_costs = 0
        for cost in costs:
            # print(
            #    f" - sum costs: {cost.name} {cost.get_rental_unit_cost(ru, include_common=True)}"
            # )
            total_costs += cost.get_rental_unit_cost(ru, include_common=True)

        # monthly_weights = self.get_monthly_weights()
        # monthly_amounts = [mw * chf_per_month for mw in monthly_weights]
        # self.rental_unit_values[ru.id][NkCostValueType.COST].monthly_amounts = monthly_amounts
        # self.rental_unit_values[ru.id][NkCostValueType.COST].amount = sum(monthly_amounts)
        # print(f"Fees for {ru.name} {total_costs} -> {self.fee_percentage / 100 * total_costs}")
        return self.fee_percentage / 100 * total_costs
