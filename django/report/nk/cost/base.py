from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from report.nk.contract import NkContract
    from report.nk.generator import NkReportGenerator
    from report.nk.rental_unit import NkRentalUnit
    from report.nk.section import NkSection


class NkCostValueType(Enum):
    ## Default costs / base costs, when costs are split into base costs and usage costs
    COST = 1  # The costs that are billed
    USAGE = 2  # The usage that is billed (consumed energy, rental unit area, etc.)
    WEIGHT = 3  # The (internal) weight for the distribution of the costs
    ## Usage costs, when costs are split into base costs and usage costs
    USAGE_COST = 4  # Usage costs
    USAGE_USAGE = 5  # Measured usage
    USAGE_WEIGHT = 6
    ## Costs from common usage (e.g., Allgemeinstrom), that is split between all rental units
    COMMON_COST = 7
    COMMON_USAGE = 8
    COMMON_WEIGHT = 9


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

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        self.generator = report_generator
        self.total_values: dict[NkCostValueType, NkCostValue] = {}
        self.section_values: dict[int, dict[NkCostValueType, NkCostValue]] = {}
        self.rental_unit_values: dict[int, dict[NkCostValueType, NkCostValue]] = {}
        self.add_value_type(NkCostValueType.COST, "Kosten", "CHF")
        self.add_value_type(NkCostValueType.WEIGHT, "Gewichtung", "")
        self.warnings = []
        self.name = cost_config.get("name")
        self.billing_group = cost_config.get("billing_group", self.name)
        self.monthly_weights_key = cost_config.get("monthly_weights", "default")
        self.section_weights_key = cost_config.get("section_weights", "default")

    def add_value_type(self, kind: NkCostValueType, name: str, unit: str):
        self._add_value_type_to_dict(self.total_values, kind, name, unit)
        for ru in self.generator.rental_units:
            if ru.id not in self.rental_unit_values:
                self.rental_unit_values[ru.id] = {}
            self._add_value_type_to_dict(self.rental_unit_values[ru.id], kind, name, unit)
        for section in self.generator.sections:
            if section.id not in self.section_values:
                self.section_values[section.id] = {}
            self._add_value_type_to_dict(self.section_values[section.id], kind, name, unit)

    def _add_value_type_to_dict(
        self, container: dict, kind: NkCostValueType, name: str, unit: str
    ):
        if kind in container:
            raise ValueError(f"Es existiert bereits ein Wert vom gleichen Typ wie {name}")
        container[kind] = self.value_cls(name, unit, 0, self.generator.num_months * [0])

    def load_input_data(self):
        pass

    def normalize_monthly_amounts(self):
        """Set monthly values from annual value, or vice versa, depending on which is available."""
        self._normalize_monthly_amounts_for_dict(self.total_values)
        for ru in self.generator.rental_units:
            self._normalize_monthly_amounts_for_dict(self.rental_unit_values[ru.id])
        for section in self.generator.sections:
            self._normalize_monthly_amounts_for_dict(self.section_values[section.id])

    def _normalize_monthly_amounts_for_dict(self, container: dict, value_required=False):
        for _kind, value in container.items():
            total = None
            if value.monthly_amounts:
                if len(value.monthly_amounts) != self.generator.num_months:
                    raise ValueError(
                        f"Inkonsistente Anzahl der Monatswerte {len(value.monthly_amounts)} "
                        f"und Anzahl der Monate {self.generator.num_months} für {value.name}/{_kind}"
                    )
                total = sum(value.monthly_amounts)
            if value.amount:
                if total:
                    # Annual and monthly values are given, check consistency
                    if abs(total - value.amount) > 0.00001:
                        raise ValueError(
                            f"Inkonsistente Angaben für Totalbetrag {value.amount} und "
                            f"Summe der Monatswerte {total} für {value.name}/{_kind}"
                        )
                else:
                    # Set monthly values from annual value
                    value.monthly_amounts = [
                        value.amount / self.generator.num_months
                    ] * self.generator.num_months
            elif total:
                # Set annual value from monthly values
                value.amount = total
            elif value_required:
                raise ValueError(
                    f"Kein Totalbetrag und keine Monatswerte angegeben für {value.name}/{_kind}"
                )

    def split_costs(self):
        self._calculate_weights()
        for kind in (NkCostValueType.COST, NkCostValueType.USAGE):
            if kind in self.total_values:
                self._split_cost(kind, NkCostValueType.WEIGHT)

    def update(self):
        pass

    def _split_cost(self, cost_type, weight_type):
        amount_per_weight = self.generator.num_months * [0]
        for month in range(self.generator.num_months):
            amount_per_weight[month] = (
                (
                    self.total_values[cost_type].monthly_amounts[month]
                    / self.total_values[weight_type].monthly_amounts[month]
                )
                if self.total_values[weight_type].monthly_amounts[month]
                else 0
            )
        self._calculate_amounts(self.total_values, cost_type, weight_type, amount_per_weight)
        for ru in self.generator.rental_units:
            self._calculate_amounts(
                self.rental_unit_values[ru.id], cost_type, weight_type, amount_per_weight
            )
        for section in self.generator.sections:
            self._calculate_amounts(
                self.section_values[section.id], cost_type, weight_type, amount_per_weight
            )

    def _calculate_amounts(
        self, values, kind: NkCostValueType, weight_type: NkCostValueType, amount_per_weight
    ):
        for month in range(self.generator.num_months):
            amount = amount_per_weight[month] * values[weight_type].monthly_amounts[month]
            if (
                values[kind].monthly_amounts[month]
                and abs(values[kind].monthly_amounts[month] - amount) > 0.01
                and kind != NkCostValueType.USAGE
            ):
                self.add_warning(
                    "overwriting existing monthly amount for "
                    f"{self.name} {kind}/{month}: "
                    f"{values[kind].monthly_amounts[month]} => {amount}"
                )
            values[kind].monthly_amounts[month] = amount
        total_amount = sum(values[kind].monthly_amounts)
        if (
            values[kind].amount
            and abs(values[kind].amount - total_amount) > 0.01
            and kind != NkCostValueType.USAGE
        ):
            self.add_warning(
                f"overwriting existing amount: {values[kind].amount} => {total_amount}"
            )

        values[kind].amount = total_amount

    def _calculate_weights(self):
        self._calculate_weights_for_type(NkCostValueType.WEIGHT, "get_rental_unit_weights")

    def _calculate_weights_for_type(
        self, value_type: NkCostValueType, rental_unit_weights_function_name: str
    ):
        self._zero_values(value_type)
        monthly_weights = self.get_monthly_weights()
        section_weights = self.get_section_weights(value_type)
        total = self.total_values[value_type]
        rental_unit_weights_function = getattr(self, rental_unit_weights_function_name)
        if not callable(rental_unit_weights_function):
            raise ValueError(f"Invalid function name: {rental_unit_weights_function_name}")
        for ru in self.generator.rental_units:
            ru_weights = rental_unit_weights_function(ru)
            values = self.rental_unit_values[ru.id][value_type]
            section = self.section_values[ru.section.id][value_type]
            for month in range(self.generator.num_months):
                weight = (
                    monthly_weights[month] * section_weights[ru.section.id] * ru_weights[month]
                )
                values.monthly_amounts[month] = weight
                section.monthly_amounts[month] += weight
                total.monthly_amounts[month] += weight
            values.amount = sum(values.monthly_amounts)
        for section in self.generator.sections:
            self.section_values[section.id][value_type].amount = sum(
                self.section_values[section.id][value_type].monthly_amounts
            )
        total.amount = sum(total.monthly_amounts)

    def _zero_values(self, value_type: NkCostValueType):
        for ru in self.generator.rental_units:
            self.rental_unit_values[ru.id][value_type].amount = 0
            self.rental_unit_values[ru.id][value_type].monthly_amounts = (
                self.generator.num_months * [0]
            )
        for section in self.generator.sections:
            self.section_values[section.id][value_type].amount = 0
            self.section_values[section.id][value_type].monthly_amounts = (
                self.generator.num_months * [0]
            )
        self.total_values[value_type].amount = 0
        self.total_values[value_type].monthly_amounts = self.generator.num_months * [0]

    def _aggregate_monthly_amounts(self, value_type: NkCostValueType = NkCostValueType.COST):
        """Aggregate pre-calculated monthly per-rental-unit costs up to sections and total."""
        for ru in self.generator.rental_units:
            for month in range(self.generator.num_months):
                amount = self.rental_unit_values[ru.id][value_type].monthly_amounts[month]
                self.section_values[ru.section.id][value_type].monthly_amounts[month] += amount
                self.total_values[value_type].monthly_amounts[month] += amount

        for section in self.generator.sections:
            self.section_values[section.id][value_type].amount = sum(
                self.section_values[section.id][value_type].monthly_amounts
            )
        self.total_values[value_type].amount = sum(self.total_values[value_type].monthly_amounts)

    def get_monthly_weights(self):
        monthly_weights = self.generator.monthly_weights.get(self.monthly_weights_key)
        if monthly_weights is None:
            raise KeyError(
                _("Unknown monthly weights '{key}' for cost '{cost_name}'").format(
                    key=self.monthly_weights_key, cost_name=self.name
                )
            )
        weights = []
        for date in self.generator.dates:
            month = date["start"].month
            weight = monthly_weights.get(month)
            if weight is None:
                raise KeyError(
                    _("Monthly weight for month '{month}' not found for '{key}'").format(
                        month=month, key=self.monthly_weights_key
                    )
                )
            weights.append(weight)
        return weights

    def get_section_weights(self, value_type: NkCostValueType) -> dict[int, float]:
        """Return weights per section, using the configured section_weights profile if available."""

        weight_profile = self._get_weight_profile(value_type)
        weights = {}
        for section in self.generator.sections:
            if weight_profile is not None:
                weights[section.id] = weight_profile.get(section.id.capitalize())
            else:
                weights[section.id] = 1.0
        return weights

    def _get_weight_profile(self, value_type: NkCostValueType):
        if self.section_weights_key:
            return self.generator.section_weights.get(self.section_weights_key)
        return None

    def get_rental_unit_weights(self, ru: "NkRentalUnit"):
        """Default with uniform weights for all rental units (excluding virtual units)"""
        if ru.is_virtual:
            return self.generator.num_months * [0.0]
        else:
            return self.generator.num_months * [1.0]

    def get_export_cost_row(self, include_percent=False):
        row = self._get_export_row([NkCostValueType.COST], include_percent)
        return row

    def get_export_weight_row(self, include_percent=False):
        row = self._get_export_row([NkCostValueType.WEIGHT], include_percent)
        return row

    def get_export_extra_info(self, include_percent=False, formatter=None):
        return None

    def _get_export_row(self, cost_types: list[NkCostValueType], include_percent):
        ## TODO: implement include_percent (if still needed)
        row = [self.name]
        if self.is_meta:
            row.append("")  # No total
        else:
            row.append(self._sum_cost_types(self.total_values, cost_types))
        for section in self.generator.sections:
            row.append(self._sum_cost_types(self.section_values[section.id], cost_types))
        for ru in self.generator.rental_units:
            row.append(self._sum_cost_types(self.rental_unit_values[ru.id], cost_types))
        return row

    def _get_assigned_amount(
        self,
        value_type: NkCostValueType,
        contract: "NkContract",
        rental_unit: "NkRentalUnit | None" = None,
    ):
        ret = 0
        rental_units = [rental_unit] if rental_unit else contract.rental_units
        for ru in rental_units:
            ret += self._get_assigned_sum(
                self.rental_unit_values[ru.id][value_type].monthly_amounts, contract, ru
            )
        return ret

    def get_assigned_cost(self, contract: "NkContract", rental_unit: "NkRentalUnit | None" = None):
        return self._get_assigned_amount(NkCostValueType.COST, contract, rental_unit)

    @classmethod
    def get_assigned_amounts(
        cls,
        data: dict[str, list[float]],
        contract: "NkContract",
        rental_unit: "NkRentalUnit",
    ):
        ret = {}
        for kind, monthly_values in data.items():
            ret[kind] = cls._get_assigned_sum(monthly_values, contract, rental_unit)
        return ret

    @staticmethod
    def _get_assigned_sum(
        monthly_values: list[float],
        contract: "NkContract",
        rental_unit: "NkRentalUnit",
    ):
        ret = 0
        for idx, amount in enumerate(monthly_values):
            assigned_contract = rental_unit.get_assigned_contract_for_month(idx)
            if assigned_contract == contract:
                ret += amount
        return ret

    @staticmethod
    def _sum_cost_types(
        values: dict[NkCostValueType, NkCostValue], cost_types: list[NkCostValueType]
    ) -> float:
        ret = 0.0
        for kind in cost_types:
            if values[kind].amount is not None:
                ret += values[kind].amount
        return ret

    def get_building_cost(self):
        return self._get_building_amount(NkCostValueType.COST)

    def _get_building_amount(self, value_type: NkCostValueType):
        return self.total_values[value_type].amount

    def get_section_cost(self, section):
        return self._get_section_amount(section, NkCostValueType.COST)

    def _get_section_amount(self, section: "NkSection", value_type: NkCostValueType):
        return self.section_values[section.id][value_type].amount

    def get_rental_unit_cost(self, rental_unit, include_common=False):
        return self._get_rental_unit_amount(rental_unit, NkCostValueType.COST)

    def _get_rental_unit_amount(self, rental_unit: "NkRentalUnit", value_type: NkCostValueType):
        return self.rental_unit_values[rental_unit.id][value_type].amount

    def _get_context(self, ru: "NkRentalUnit", contract: "NkContract") -> dict:
        """Return extra context variables for ODT template rendering. Override in subclasses."""
        return {}

    def update_context(
        self, ru: "NkRentalUnit", contract: "NkContract", context: dict, aggregated_values: dict
    ) -> None:
        context.update(self._get_context(ru, contract))

    def add_warning(self, msg):
        print(f"WARNING: {msg}")
        self.warnings.append(msg)


class NkMeasurementDataMixin(NkCost):
    """Mixin for NkCosts that require measurement data."""

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.measurements = {}
        measurements_configs = cost_config.get("measurement_data")
        if measurements_configs:
            for key, config in measurements_configs.items():
                self.measurements[key] = config["class"](report_generator, config)

    def load_input_data(self):
        if self.measurements:
            for m in self.measurements.values():
                m.load()
                for warning in m.warnings:
                    print(warning)
                    self.generator.add_warning(warning[0], warning[1])
        super().load_input_data()


class NkCommonCostMixin(NkCost):
    """Mixin for NkCosts that have a common usage part (e.g., Allgemeinstrom), which is distributed among all rental units."""

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.common_cost_section_weights = cost_config.get(
            "common_cost_section_weights", "default"
        )
        self.add_value_type(NkCostValueType.COMMON_COST, "Allgemeinkosten", "CHF")
        self.add_value_type(NkCostValueType.COMMON_WEIGHT, "Gewichtung", "")

    def get_rental_unit_cost(self, rental_unit, include_common=False):
        ret = super().get_rental_unit_cost(rental_unit, include_common)
        if include_common:
            ret += self._get_rental_unit_amount(rental_unit, NkCostValueType.COMMON_COST)
        return ret

    def get_assigned_cost(self, contract: "NkContract", rental_unit: "NkRentalUnit | None" = None):
        ret = super().get_assigned_cost(contract, rental_unit)
        return ret + self._get_assigned_amount(NkCostValueType.COMMON_COST, contract, rental_unit)

    def get_rental_unit_common_weights(self, ru):
        """Default is the rental unit area (per period)."""
        if ru.is_virtual:
            return self.generator.num_months * [0.0]
        else:
            return self.generator.num_months * [ru.area / self.generator.num_months]

    def set_common_costs(self, cost: float | list[float], usage: float | list[float] | None):
        if isinstance(cost, list):
            self.total_values[NkCostValueType.COMMON_COST].monthly_amounts = cost
        else:
            self.total_values[NkCostValueType.COMMON_COST].amount = cost
        if usage:
            if isinstance(usage, list):
                self.total_values[NkCostValueType.COMMON_USAGE].monthly_amounts = usage
            else:
                self.total_values[NkCostValueType.COMMON_USAGE].amount = usage
        self.normalize_monthly_amounts()

    def _split_common_costs(self):
        self._calculate_common_weights()
        for kind in (NkCostValueType.COMMON_COST, NkCostValueType.COMMON_USAGE):
            self._split_cost(kind, NkCostValueType.COMMON_WEIGHT)

    def _calculate_common_weights(self):
        self._calculate_weights_for_type(
            NkCostValueType.COMMON_WEIGHT, "get_rental_unit_common_weights"
        )

    def _get_weight_profile(self, value_type: NkCostValueType):
        if value_type in (
            NkCostValueType.COMMON_COST,
            NkCostValueType.COMMON_USAGE,
            NkCostValueType.COMMON_WEIGHT,
        ):
            if self.common_cost_section_weights:
                return self.generator.section_weights.get(self.common_cost_section_weights)
            else:
                return None
        return super()._get_weight_profile(value_type)
