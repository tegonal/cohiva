from enum import Enum
from operator import add
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from geno.utils import nformat
from report.nk.rental_unit import NkVirtualRentalUnitId

from . import NkTotalCost
from .base import NkCommonCostMixin, NkCostValueType, NkMeasurementDataMixin

if TYPE_CHECKING:
    from report.nk.contract import NkContract
    from report.nk.generator import NkReportGenerator
    from report.nk.rental_unit import NkRentalUnit
    from report.nk.section import NkSection


class NkCostVEWACategories(Enum):
    HEAT_WATER = 1  # Warmwasseraufbereitung
    HEAT_HEATING = 2  # Heizung
    WATER_GENERAL = 3  # Wasser- & Abwasserkosten


class NkCostVEWA(NkCommonCostMixin, NkMeasurementDataMixin, NkTotalCost):
    """VEWA (Verbrauchsabhängige Energie- und Wasserkostenabrechnung, vewa.ch)

    Splits between base costs and usage costs (typically 30/70%).

    NkCostValueTypes:
       - COST, USAGE, WEIGHT: Base costs (handled in NkTotalCost)
       - USAGE_COST, USAGE_USAGE, USAGE_WEIGHT: Usage costs
    """

    cost_type_id = "vewa"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.add_value_type(NkCostValueType.USAGE_COST, "Verbrauchsabhängige Kosten", "CHF")
        self.add_value_type(NkCostValueType.USAGE_USAGE, "Verbrauch", "kWh")
        self.add_value_type(NkCostValueType.COMMON_USAGE, "Allgemeinverbrauch", "kWh")

        config = self.generator.config
        self.base_cost_factor = float(config.get(cost_config.get("base_cost_factor_key"), 0.3))
        self.vewa_category = cost_config.get("vewa_category")
        self.exclude_zero_usage_units = cost_config.get("exclude_zero_usage_units", False)
        self._validate_config()

    def load_building_totals(self):
        total_costs = self.get_total_costs()
        if total_costs is None:
            raise ValueError(_("No total costs found for {cost_name}").format(cost_name=self.name))
        ## Split base costs and usage costs
        if "rental_units" not in self.measurements:
            # No rental unit measurements, can't calculate usage costs -> only use base costs
            self.base_cost_factor = 1.0
        if isinstance(total_costs, list):
            self.total_values[NkCostValueType.COST].monthly_amounts = [
                x * self.base_cost_factor for x in total_costs
            ]
            self.total_values[NkCostValueType.USAGE_COST].monthly_amounts = [
                x * (1.0 - self.base_cost_factor) for x in total_costs
            ]
        else:
            self.total_values[NkCostValueType.COST].amount = total_costs * self.base_cost_factor
            self.total_values[
                NkCostValueType.USAGE_COST
            ].monthly_amounts = self.get_monthly_values_by_building_usage(
                total_costs * (1.0 - self.base_cost_factor)
            )

        # Building-level usage
        building_total = self.measurements["building"].get("usage")
        if not building_total:
            building_total = self._get_missing_building_usage()
        elif not isinstance(building_total, list):
            # Distribute usage with monthly usage weights
            building_total = self.get_monthly_values_by_building_usage(building_total)
        self.total_values[NkCostValueType.USAGE_USAGE].monthly_amounts = building_total

    def get_total_costs(self):
        # Try to get the costs from the building measurements
        total_costs = self.measurements["building"].get("costs")
        if isinstance(total_costs, list):
            return total_costs
        return super().get_total_costs()

    def _get_missing_building_usage(self):
        """Try to get the building usage from the rental unit measurements."""
        building_usage = self.generator.num_months * [0]
        if "rental_units" not in self.measurements:
            return building_usage
        for ru in self.generator.rental_units:
            usage = self.measurements["rental_units"].get(ru.name, {}).get("usage")
            if usage:
                building_usage = list(map(add, building_usage, usage))
        return building_usage

    def get_monthly_values_by_building_usage(self, annual_value):
        """Split annual value into monthly values based on monthly usage at the building level."""
        monthly_weights = [0] * self.generator.num_months
        for ru in self.generator.rental_units:
            monthly_weights = list(
                map(add, monthly_weights, self.get_rental_unit_usage_weights(ru))
            )
        total_weight = sum(monthly_weights)
        monthly_values = []
        for i in range(self.generator.num_months):
            monthly_values.append(annual_value * monthly_weights[i] / total_weight)
        return monthly_values

    def get_rental_unit_usage_weights(self, ru):
        """Use rental unit measurements as weights to distribute the building totals."""
        ru_messung = self.measurements.get("rental_units", {}).get(ru.name, {})
        return ru_messung.get("usage", self.generator.num_months * [0.0])

    def get_rental_unit_weights(self, ru):
        if self.exclude_zero_usage_units and self._has_zero_usage(ru):
            self.add_warning(f"Excluding rental unit with zero usage: {ru.name}/{ru.id}")
            return self.generator.num_months * [0.0]
        return super().get_rental_unit_weights(ru)

    def _has_zero_usage(self, ru):
        return sum(self.measurements["rental_units"].get(ru.name, {}).get("usage", [0])) == 0

    def split_costs(self):
        # Base costs are handled by the super class
        super().split_costs()
        # Usage costs
        self._calculate_usage_weights()
        for kind in (NkCostValueType.USAGE_COST, NkCostValueType.USAGE_USAGE):
            self._split_cost(kind, NkCostValueType.USAGE_WEIGHT)
        # Common costs
        self._calculate_and_split_common_costs()
        # self._print_debug_info()

    def _print_debug_info(self):
        groups = [
            {
                "name": "Base",
                "types": [NkCostValueType.COST, NkCostValueType.USAGE, NkCostValueType.WEIGHT],
            },
            {
                "name": "Usage",
                "types": [
                    NkCostValueType.USAGE_COST,
                    NkCostValueType.USAGE_USAGE,
                    NkCostValueType.USAGE_WEIGHT,
                ],
            },
            {
                "name": "Common",
                "types": [
                    NkCostValueType.COMMON_COST,
                    NkCostValueType.COMMON_USAGE,
                    NkCostValueType.COMMON_WEIGHT,
                ],
            },
        ]
        for group in groups:
            print("")
            print(f"*** {group['name']} for {self.name}")
            values = [
                nformat(self.total_values[value_type].amount) for value_type in group["types"]
            ]
            print(f"Total: {' | '.join(values)}")
            for ru in self.generator.rental_units:
                ru_values = [
                    nformat(self.rental_unit_values[ru.id][value_type].amount)
                    for value_type in group["types"]
                ]
                print(f"{ru.name}: {' | '.join(ru_values)}")

    def _calculate_and_split_common_costs(self):
        # Set common costs from virtual rental unit "allg" (Allgemeinstrom)
        #   - costs = base costs + usage costs
        #   - usage = common weight (usually m2)
        self._calculate_common_weights()
        self.set_common_costs(
            list(
                map(
                    add,
                    self.rental_unit_values[NkVirtualRentalUnitId.COMMON][
                        NkCostValueType.COST
                    ].monthly_amounts,
                    self.rental_unit_values[NkVirtualRentalUnitId.COMMON][
                        NkCostValueType.USAGE_COST
                    ].monthly_amounts,
                )
            ),
            self.total_values[NkCostValueType.COMMON_WEIGHT].monthly_amounts,
        )
        self._split_common_costs()

    def _calculate_usage_weights(self):
        self.add_value_type(NkCostValueType.USAGE_WEIGHT, "Gewichtung", "")
        self._calculate_weights_for_type(
            NkCostValueType.USAGE_WEIGHT, "get_rental_unit_usage_weights"
        )

    def update_context(
        self, ru: "NkRentalUnit", contract: "NkContract", context: dict, aggregated_values: dict
    ) -> None:
        context_key, context_prefix = self.get_context_key()
        if context_key not in context:
            context[context_key] = []
        cost_context = self._get_context(ru, contract)
        context[context_key].append(cost_context)
        self._update_aggregated_context(ru, contract, context, aggregated_values)

        # Support for legacy templates: add context variables with fixed prefix for old templates,
        # which support only one cost per prefix.
        for key, value in cost_context.items():
            context[f"{context_prefix}{key}"] = value

    def get_context_key(self):
        """Return the context key and prefix (for legecy templates) for the ODT bill template."""
        if self.vewa_category == NkCostVEWACategories.HEAT_WATER:
            context_key = "vewa_warmwasser"
            legacy_prefix = "ww"
        elif self.vewa_category == NkCostVEWACategories.HEAT_HEATING:
            if self.name == "Fernwaerme_Fussboden":
                legacy_prefix = "hf"
            elif self.name == "Fernwaerme_Radiatoren":
                legacy_prefix = "hr"
            elif self.name == "Fernwaerme_Lueftung":
                legacy_prefix = "hl"
            else:
                legacy_prefix = "h"
            context_key = "vewa_heizung"
        elif self.vewa_category == NkCostVEWACategories.WATER_GENERAL:
            legacy_prefix = "wa"
            context_key = "vewa_wasser"
        else:
            raise ValueError(
                _("Invalid VEWA category: {category}").format(category=self.vewa_category)
            )
        return context_key, legacy_prefix

    def _get_context(self, ru: "NkRentalUnit", contract: "NkContract") -> dict:
        """Return Stromkosten detail variables for the ODT bill template."""

        def fmt(val):
            return nformat(val)

        def fmt_use(val):
            return nformat(val, 0)

        def rate(chf, use):
            return nformat(chf / use if use else 0, 2)

        # Building totals
        bt = {
            "base": {
                "chf": self.total_values[NkCostValueType.COST].amount,
                "use": self.total_values[NkCostValueType.USAGE].amount,
            },
            "usage": {
                "chf": self.total_values[NkCostValueType.USAGE_COST].amount,
                "use": self.total_values[NkCostValueType.USAGE_USAGE].amount,
            },
            "common": {
                "chf": self.total_values[NkCostValueType.COMMON_COST].amount,
                "use": self.total_values[NkCostValueType.COMMON_USAGE].amount,
            },
        }
        # Assigned costs
        d = {
            "base": {
                "chf": self._get_assigned_amount(NkCostValueType.COST, contract, ru),
                "use": self._get_assigned_amount(NkCostValueType.USAGE, contract, ru),
            },
            "usage": {
                "chf": self._get_assigned_amount(NkCostValueType.USAGE_COST, contract, ru),
                "use": self._get_assigned_amount(NkCostValueType.USAGE_USAGE, contract, ru),
            },
            "common": {
                "chf": self._get_assigned_amount(NkCostValueType.COMMON_COST, contract, ru),
                "use": self._get_assigned_amount(NkCostValueType.COMMON_USAGE, contract, ru),
            },
        }
        ctx = {
            # Base costs
            "g_chft": fmt(bt["base"]["chf"]),
            "gt": fmt_use(bt["base"]["use"]),
            "g_eh": rate(bt["base"]["chf"], bt["base"]["use"]),
            "g": fmt_use(d["base"]["use"]),
            "g_chf": fmt(d["base"]["chf"]),
            # Usage costs
            "v_chft": fmt(bt["usage"]["chf"]),
            "vt": fmt_use(bt["usage"]["use"]),
            "v_eh": rate(bt["usage"]["chf"], bt["usage"]["use"]),
            "v": fmt_use(d["usage"]["use"]),
            "v_chf": fmt(d["usage"]["chf"]),
            # Base + Usage costs
            "_chft": fmt(bt["base"]["chf"] + bt["usage"]["chf"]),
            "t": fmt_use(bt["base"]["use"] + bt["usage"]["use"]),
            "_eh": rate(
                bt["base"]["chf"] + bt["usage"]["chf"], bt["base"]["use"] + bt["usage"]["use"]
            ),
            "": fmt_use(d["base"]["use"] + d["usage"]["use"]),
            "_chf": fmt(d["base"]["chf"] + d["usage"]["chf"]),
            # Common costs
            "a_chft": fmt(bt["common"]["chf"]),
            "at": fmt_use(bt["common"]["use"]),
            "a_eh": rate(bt["common"]["chf"], bt["common"]["use"]),
            "a": fmt_use(d["common"]["use"]),
            "a_chf": fmt(d["common"]["chf"]),
        }
        return ctx

    def _update_aggregated_context(
        self, ru: "NkRentalUnit", contract: "NkContract", context: dict, aggregated_values: dict
    ) -> None:
        if self.vewa_category == NkCostVEWACategories.HEAT_WATER:
            self._update_context_totals(
                ["wwbt_chft", "sw_chft"],
                ["wwbt_chf", "wwt_chf", "sw_chf"],
                ["wwt_chf", "sw_chf"],
                ru,
                contract,
                context,
                aggregated_values,
            )
        elif self.vewa_category == NkCostVEWACategories.HEAT_HEATING:
            self._update_context_totals(
                ["ht_chft", "sw_chft"],
                ["ht_chf", "sw_chf"],
                ["sw_chf"],
                ru,
                contract,
                context,
                aggregated_values,
            )
        elif self.vewa_category == NkCostVEWACategories.WATER_GENERAL:
            self._update_context_totals(
                ["wat_chft", "swa_chft"],
                ["wat_chf", "swa_chf"],
                ["swa_chf"],
                ru,
                contract,
                context,
                aggregated_values,
            )
        else:
            raise ValueError(
                _("Invalid VEWA category: {category}").format(category=self.vewa_category)
            )

    def _update_context_totals(
        self,
        building_keys: list[str],
        unit_keys: list[str],
        include_common_keys: list[str],
        ru: "NkRentalUnit",
        contract: "NkContract",
        context: dict,
        aggregated_values: dict,
    ) -> None:
        for key in building_keys + unit_keys:
            if key not in aggregated_values:
                aggregated_values[key] = 0
        building = (
            self.total_values[NkCostValueType.COST].amount
            + self.total_values[NkCostValueType.USAGE_COST].amount
        )
        unit = self._get_assigned_amount(
            NkCostValueType.COST, contract, ru
        ) + self._get_assigned_amount(NkCostValueType.USAGE_COST, contract, ru)
        common_building = self.total_values[NkCostValueType.COMMON_COST].amount
        common_unit = self._get_assigned_amount(NkCostValueType.COMMON_COST, contract, ru)
        # Building totals
        for key in building_keys:
            aggregated_values[key] += building
            if key in include_common_keys:
                # Building totals including the common usage
                aggregated_values[key] += common_building
        # Unit totals
        for key in unit_keys:
            aggregated_values[key] += unit
            if key in include_common_keys:
                # Unit totals including the common usage
                aggregated_values[key] += common_unit
        for key in building_keys + unit_keys:
            context[key] = nformat(aggregated_values.get(key, 0))

    def get_building_cost(self):
        ret = super().get_building_cost()
        return ret + self._get_building_amount(NkCostValueType.USAGE_COST)

    def get_section_cost(self, section: "NkSection"):
        ret = super().get_section_cost(section)
        return ret + self._get_section_amount(section, NkCostValueType.USAGE_COST)

    def get_rental_unit_cost(self, rental_unit: "NkRentalUnit", include_common=False):
        ret = super().get_rental_unit_cost(rental_unit, include_common)
        return ret + self._get_rental_unit_amount(rental_unit, NkCostValueType.USAGE_COST)

    def get_assigned_cost(self, contract: "NkContract", rental_unit: "NkRentalUnit | None" = None):
        ret = super().get_assigned_cost(contract, rental_unit)
        return ret + self._get_assigned_amount(NkCostValueType.USAGE_COST, contract, rental_unit)

    @staticmethod
    def _zero_data(num_months: int) -> dict:
        zeros = num_months * [0.0]
        return {
            "usage": list(zeros),
        }

    def _validate_config(self):
        if self.base_cost_factor < 0.0 or self.base_cost_factor > 1.0:
            raise ValueError(
                _("The base cost factor is not in the range 0.0 - 1.0: {factor}").format(
                    tarif=self.base_cost_factor
                )
            )
        if not isinstance(self.vewa_category, NkCostVEWACategories):
            raise ValueError(
                _("Invalid VEWA category: {category}").format(category=self.vewa_category)
            )
