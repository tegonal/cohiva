from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from report.nk.generator import NkReportGenerator


class NkCostValueType(Enum):
    COST = 1  # The costs that are billed
    USAGE = 2  # The usage that is billed (consumed energy, rental unit area, etc.)
    WEIGHT = 3  # The (internal) weight for the distribution of the costs


@dataclass
class NkCostValue:
    name: str
    unit: str
    amount: float | None = None
    monthly_amounts: list[float] | None = None
    percent: float | None = None
    monthly_percent: list[float] | None = None


class NkCost:
    """Base class for all costs."""

    value_cls = NkCostValue
    cost_type_id = None
    is_meta = False
    is_special = False

    def __init__(self, report: "NkReportGenerator", cost_config: dict):
        self.report = report
        self.name = cost_config.get("name")
        self.total_values = {}
        self.section_values = {}
        self.rental_unit_values = {}
        self.section_weights = cost_config.get("section_weights", "default")
        self.add_value_type(NkCostValueType.COST, "Kosten", "CHF")

    def add_value_type(self, kind: NkCostValueType, name: str, unit: str):
        self._add_value_type_to_dict(self.total_values, kind, name, unit)
        for ru in self.report.rental_units:
            if ru.id not in self.rental_unit_values:
                self.rental_unit_values[ru.id] = {}
            self._add_value_type_to_dict(self.rental_unit_values[ru.id], kind, name, unit)
        for section in self.report.sections:
            if section.id not in self.section_values:
                self.section_values[section.id] = {}
            self._add_value_type_to_dict(self.section_values[section.id], kind, name, unit)

    def _add_value_type_to_dict(
        self, container: dict, kind: NkCostValueType, name: str, unit: str
    ):
        if kind in container:
            raise ValueError(f"Es existiert bereits ein Wert vom gleichen Typ wie {name}")
        container[kind] = self.value_cls(name, unit, 0, self.report.num_months * [0])

    def load_input_data(self):
        pass
        # raise NotImplementedError("load_input_data() must be implemented by subclasses")

    def normalize_monthly_amounts(self):
        """Set monthly values from annual value, or vice versa, depending on which is available."""
        self._normalize_monthly_amounts_for_dict(self.total_values)
        for ru in self.report.rental_units:
            self._normalize_monthly_amounts_for_dict(self.rental_unit_values[ru.id])
        for section in self.report.sections:
            self._normalize_monthly_amounts_for_dict(self.section_values[section.id])

    def _normalize_monthly_amounts_for_dict(self, container: dict, value_required=False):
        for _kind, value in container.items():
            # pprint(value)
            total = None
            if value.monthly_amounts:
                if len(value.monthly_amounts) != self.report.num_months:
                    raise ValueError(
                        f"Inkonsistente Anzahl der Monatswerte {len(value.monthly_amounts)} "
                        f"und Anzahl der Monate {self.report.num_months} für {value.name}/{_kind}"
                    )
                total = sum(value.monthly_amounts)
            if value.amount:
                if total:
                    # Annual and monthly values are given, check consistency
                    if total != value.amount:
                        raise ValueError(
                            f"Inkonsistente Angaben für Totalbetrag {value.amount} und "
                            f"Summe der Monatswerte {total} für {value.name}/{_kind}"
                        )
                else:
                    # Set monthly values from annual value
                    value.monthly_amounts = [
                        value.amount / self.report.num_months
                    ] * self.report.num_months
            elif total:
                # Set annual value from monthly values
                value.amount = total
            elif value_required:
                raise ValueError(
                    f"Kein Totalbetrag und keine Monatswerte angegeben für {value.name}/{_kind}"
                )

    def split_costs(self):
        self._calculate_weights()
        for kind in self.total_values:
            if kind == NkCostValueType.WEIGHT:
                continue
            amount_per_weight = (
                (self.total_values[kind].amount / self.total_values[NkCostValueType.WEIGHT].amount)
                if self.total_values[NkCostValueType.WEIGHT].amount
                else 0
            )
            self._calculate_amounts(self.total_values, kind, amount_per_weight)
            for ru in self.report.rental_units:
                self._calculate_amounts(self.rental_unit_values[ru.id], kind, amount_per_weight)
            for section in self.report.sections:
                self._calculate_amounts(self.section_values[section.id], kind, amount_per_weight)

    def _calculate_amounts(self, values, kind: NkCostValueType, amount_per_weight):
        for month in range(self.report.num_months):
            amount = amount_per_weight * values[NkCostValueType.WEIGHT].monthly_amounts[month]
            if (
                values[kind].monthly_amounts[month]
                and abs(values[kind].monthly_amounts[month] - amount) > 0.01
            ):
                print(
                    "WARNING: overwriting existing monthly amount: "
                    f"{values[kind].monthly_amounts[month]} => {amount}"
                )
            values[kind].monthly_amounts[month] = amount
        total_amount = sum(values[kind].monthly_amounts)
        if values[kind].amount and abs(values[kind].amount - total_amount) > 0.01:
            print(f"WARNING: overwriting existing amount: {values[kind].amount} => {total_amount}")
        values[kind].amount = total_amount

    def _calculate_weights(self):
        self.add_value_type(NkCostValueType.WEIGHT, "Gewichtung", "")
        monthly_weights = self.get_monthly_weights()
        section_weights = self.get_section_weights()
        total = self.total_values[NkCostValueType.WEIGHT]
        for ru in self.report.rental_units:
            ru_weights = self.get_rental_unit_weights(ru.id)
            values = self.rental_unit_values[ru.id][NkCostValueType.WEIGHT]
            section = self.section_values[ru.section.id][NkCostValueType.WEIGHT]
            for month in range(self.report.num_months):
                weight = (
                    monthly_weights[month] * section_weights[ru.section.id] * ru_weights[month]
                )
                values.monthly_amounts[month] = weight
                section.monthly_amounts[month] += weight
                total.monthly_amounts[month] += weight
            values.amount = sum(values.monthly_amounts)
        for section in self.report.sections:
            self.section_values[section.id][NkCostValueType.WEIGHT].amount = sum(
                self.section_values[section.id][NkCostValueType.WEIGHT].monthly_amounts
            )
        total.amount = sum(total.monthly_amounts)

    def get_monthly_weights(self):
        """Default with equal weights for all months."""
        return self.report.num_months * [1.0]

    def get_section_weights(self):
        """Default with equal weights for all sections."""
        weights = {}
        for section in self.report.sections:
            weights[section.id] = 1.0
        return weights

    def get_rental_unit_weights(self, ru_id):
        """Default with equal weights for all rental units."""
        ru = self.report.get_rental_unit_by_id(ru_id)
        if ru.is_virtual:
            return self.report.num_months * [0.0]
        else:
            return self.report.num_months * [1.0]

    def get_export_cost_row(self, include_percent=False):
        row = self._get_export_row(NkCostValueType.COST, include_percent)
        return row

    def get_export_weight_row(self, include_percent=False):
        row = self._get_export_row(NkCostValueType.WEIGHT, include_percent)
        return row

    def _get_export_row(self, kind, include_percent):
        ## TODO: implement include_percent (if still needed)
        row = [self.name]
        if self.is_meta:
            row.append("")  # No total
        else:
            row.append(self.total_values[kind].amount)
        for section in self.report.sections:
            row.append(self.section_values[section.id][kind].amount)
        for ru in self.report.rental_units:
            row.append(self.rental_unit_values[ru.id][kind].amount)
        return row
