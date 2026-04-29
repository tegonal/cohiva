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

    def get_extra_context(self, ru: "NkRentalUnit", contract: "NkContract") -> dict:
        """Return Stromkosten detail variables for the ODT bill template."""

        ru_data = self._strom_data.get(ru.id, self._zero_strom_data(self.generator.num_months))
        d = self.get_assigned_amounts(ru_data, contract, ru)
        bt = self._building_totals

        # Common costs (Allgemeinstrom)
        common_cost = self._get_assigned_amount(NkCostValueType.COMMON_COST, contract, ru)
        common_weight = self._get_assigned_amount(NkCostValueType.COMMON_WEIGHT, contract, ru)
        common_total_cost = self.total_values[NkCostValueType.COMMON_COST].amount
        common_total_weight = self.total_values[NkCostValueType.COMMON_WEIGHT].amount

        def fmt(val):
            return nformat(val)

        def fmt_kwh(val):
            return nformat(val, 0)

        def rate(chf, kwh):
            return nformat(chf / kwh if kwh else 0, 4)

        # Building totals (formatted)
        ctx = {
            # Eigenverbrauch Solar direkt (from roof)
            "ssd_chft": fmt(bt["ssd"]["chf"]),
            "ssdt": fmt_kwh(bt["ssd"]["kwh"]),
            "ssd_eh": rate(bt["ssd"]["chf"], bt["ssd"]["kwh"]),
            "ssd": fmt_kwh(d["kwh_solar"]),
            "ssd_chf": fmt(d["chf_solar_eigen"]),
            # Eigenverbrauch Solar via Speicher/Stromallmend
            "sss_chft": fmt(bt["sss"]["chf"]),
            "ssst": fmt_kwh(bt["sss"]["kwh"]),
            "sss_eh": rate(bt["sss"]["chf"], bt["sss"]["kwh"]),
            "sss": fmt_kwh(d["kwh_solar_speicher"]),
            "sss_chf": fmt(d["chf_solar_speicher"]),
            # Netzstrombezug Hochtarif
            "snh_chft": fmt(bt["snh"]["chf"]),
            "snht": fmt_kwh(bt["snh"]["kwh"]),
            "snh_eh": rate(bt["snh"]["chf"], bt["snh"]["kwh"]),
            "snh": fmt_kwh(d["kwh_netz_hoch"]),
            "snh_chf": fmt(d["chf_netz_hoch"]),
            # Netzstrombezug Niedertarif
            "snt_chft": fmt(bt["snt"]["chf"]),
            "sntt": fmt_kwh(bt["snt"]["kwh"]),
            "snt_eh": rate(bt["snt"]["chf"], bt["snt"]["kwh"]),
            "snt": fmt_kwh(d["kwh_netz_nieder"]),
            "snt_chf": fmt(d["chf_netz_nieder"]),
            # Herkunftsnachweise (HKN)
            "shk_chft": fmt(bt["shk"]["chf"]),
            "shkt": fmt_kwh(bt["shk"]["kwh"]),
            "shk_eh": rate(bt["shk"]["chf"], bt["shk"]["kwh"]),
            "shk": fmt_kwh(d["kwh_solar_einkauf"]),
            "shk_chf": fmt(d["chf_solar_hkn"]),
            # Korrektur
            "sk_chft": fmt(bt["sk"]["chf"]),
            "skt": fmt_kwh(bt["sk"]["kwh"]),
            "sk_eh": rate(bt["sk"]["chf"], bt["sk"]["kwh"]),
            "sk": fmt_kwh(d["kwh_korrektur"]),
            "sk_chf": fmt(d["chf_korrektur"]),
            # Strom subtotal ( of above, no separate Allgemeinstrom/fees in this class)
            "st_chft": fmt(bt["total"]["chf"]),
            "stt": fmt_kwh(bt["total"]["kwh"]),
            "st": fmt_kwh(d["kwh_total"]),
            "st_chf": fmt(d["chf_total"]),
            # Anteil Allgemeinstrom (not computed by this class – leave empty)
            "sa_chft": fmt(common_total_cost),
            "sat": nformat(common_total_weight, 0),
            "sa_eh": nformat(
                common_total_cost / common_total_weight if common_total_weight else 0, 2
            ),
            "sa": nformat(common_weight, 1),
            "sa_chf": fmt(common_cost),
            # Stromnebenkosten/Messung (not computed by this class – leave empty)
            "snk_chft": "",
            "snkt": "",
            "snk_eh": "",
            "snk": "",
            "snk_chf": "",
            # Grand total, building totals already include common costs
            "stot_chft": fmt(bt["total"]["chf"]),
            "stot_chf": fmt(d["chf_total"] + common_cost),
        }
        return ctx

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
