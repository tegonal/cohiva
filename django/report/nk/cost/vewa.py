from collections.abc import Callable
from enum import Enum
from operator import add
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from geno.utils import nformat

from . import NkTotalCost
from .base import NkCommonCostMixin, NkCostValueType, NkMeasurementDataMixin

if TYPE_CHECKING:
    from report.nk.contract import NkContract
    from report.nk.generator import NkReportGenerator
    from report.nk.rental_unit import NkRentalUnit


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
        ## Split base costs and usage costs
        if isinstance(total_costs, list):
            self.total_values[NkCostValueType.COST].monthly_amounts = [
                x * self.base_cost_factor for x in total_costs
            ]
            self.total_values[NkCostValueType.USAGE_COST].monthly_amounts = [
                x * (1 - self.base_cost_factor) for x in total_costs
            ]
        else:
            self.total_values[NkCostValueType.COST].amount = total_costs * self.base_cost_factor
            self.total_values[
                NkCostValueType.USAGE_COST
            ].monthly_amounts = self.get_monthly_values_by_building_usage(
                total_costs * (1.0 - self.base_cost_factor)
            )

        # Building-level usage
        building_total = self.measurements["building"].get("verbrauch")
        if not building_total:
            building_total = self.generator.num_months * [0]
        elif not isinstance(building_total, list):
            # Distribute usage with monthly usage weights
            building_total = self.get_monthly_values_by_building_usage(building_total)
        self.total_values[NkCostValueType.USAGE_USAGE].monthly_amounts = building_total

        # Set common costs from virtual rental unit "allg" (Allgemeinstrom)
        # self.set_common_costs(
        #    self._strom_data[NkVirtualRentalUnitId.COMMON]["chf_total"],
        #    self._strom_data[NkVirtualRentalUnitId.COMMON]["kwh_total"],
        # )

    def get_monthly_values_by_building_usage(self, annual_value):
        """Split annual value into monthly values based on monthly usage at the building level."""
        monthly_weights = [0] * self.generator.num_months
        for ru in self.generator.rental_units:
            monthly_weights = list(
                map(add, monthly_weights, self.get_rental_unit_usage_weights(ru.id))
            )
        total_weight = sum(monthly_weights)
        monthly_values = []
        for i in range(self.generator.num_months):
            monthly_values.append(annual_value * monthly_weights[i] / total_weight)
        return monthly_values

    def get_rental_unit_usage_weights(self, ru_id):
        """Use rental unit measurements as weights to disribute the building totals."""
        ru = self.generator.get_rental_unit_by_id(ru_id)
        ru_messung = self.measurements["rental_units"].get(ru.name, {})
        return ru_messung.get("verbrauch", self.generator.num_months * [0.0])

    def get_rental_unit_weights(self, ru_id):
        if self.exclude_zero_usage_units and self._has_zero_usage(ru_id):
            return 0
        return super().get_rental_unit_weights(ru_id)

    def _has_zero_usage(self, ru_id):
        return self.measurements["rental_units"].get(ru_id, {}).get("verbrauch", 0) == 0

    def split_costs(self):
        # Base costs are handled by the super class
        super().split_costs()
        # Split usage costs
        self._calculate_usage_weights()
        for kind in (NkCostValueType.USAGE_COST, NkCostValueType.USAGE_USAGE):
            self._split_cost(kind, NkCostValueType.USAGE_WEIGHT)
        # self._calculate_weights()
        # self._split_common_costs()
        # self._aggregate_monthly_amounts()

    def _calculate_usage_weights(self):
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
        self._update_aggregated_context(ru, contract, aggregated_values, context)

        # Support for legacy templates: add context variables with fixed prefix for old templates,
        # which support only one cost per prefix.
        for key, value in cost_context.items():
            context[f"{context_prefix}_{key}"] = value

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
            return nformat(val, 1)

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
                ["sw_chft", "wwt_chf", "sw_chf"],
                ru,
                contract,
                context,
                aggregated_values,
            )
        elif self.vewa_category == NkCostVEWACategories.HEAT_HEATING:
            self._update_context_totals(
                ["ht_chft", "sw_chft"],
                ["ht_chf", "sw_chf"],
                ["sw_chft", "sw_chf"],
                ru,
                contract,
                context,
                aggregated_values,
            )
        elif self.vewa_category == NkCostVEWACategories.WATER_GENERAL:
            self._update_context_totals(
                ["wat_chft", "swa_chft"],
                ["wat_chf", "swa_chf"],
                ["swa_chft", "swa_chf"],
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

    def get_export_extra_info(
        self, include_percent: bool = False, formatter: Callable = lambda x: x
    ) -> list:
        lines = []
        for key in (
            "kwh_solar",  # "messung_strom_solar",
            "kwh_solar_speicher",
            "kwh_solar_einkauf",
            "kwh_netzstrom",
            "kwh_netz_hoch",
            "kwh_netz_nieder",
            "kwh_korrektur",
            "kwh_total",
            "chf_solar_eigen",
            "chf_solar_speicher",  # "chf_solar_einspeise",
            "chf_solar_hkn",
            "chf_netz_hoch",  # "messung_chf_netz_hoch",
            "chf_netz_nieder",  # "messung_chf_netz_nieder",
            "chf_korrektur",
            "chf_total",
        ):
            obj_data = []
            total = 0
            for ru in self.generator.rental_units:
                d = self._strom_data.get(ru.id, self._zero_strom_data(self.generator.num_months))
                value = d.get(key)
                if value:
                    annual_value = sum(value)
                    total += annual_value
                    obj_data.append(formatter(annual_value))
                else:
                    obj_data.append("")
                if include_percent:
                    obj_data.append("")

            row = [key, formatter(total)]
            for _s in self.generator.sections:
                row.append("")
                if include_percent:
                    row.append("")
            row += obj_data
            lines.append(row)
        return lines

    @staticmethod
    def _zero_data(num_months: int) -> dict:
        zeros = num_months * [0.0]
        return {
            "verbrauch": list(zeros),
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
