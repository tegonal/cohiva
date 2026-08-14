from collections.abc import Callable
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from geno.utils import nformat
from report.nk.rental_unit import NkVirtualRentalUnitId

from .base import NkCommonCostMixin, NkCost, NkCostValueType, NkMeasurementDataMixin

if TYPE_CHECKING:
    from report.nk.contract import NkContract
    from report.nk.generator import NkReportGenerator
    from report.nk.rental_unit import NkRentalUnit


class NkCostZEVStromallmend(NkCommonCostMixin, NkMeasurementDataMixin, NkCost):
    """ZEV electricity costs calculated individually per rental unit.

    Mirrors the logic from the old report_nk.stromrechnung():
    - Reads tariffs from report config (Strom:Tarif:*)
    - Reads per-unit measurement data from report.object_messung[ru.name]:
        strom_solar, strom_ew_hoch, strom_ew_nieder, chf_netz_hoch, chf_netz_nieder
    - Reads building-level data from report.data_amount:
        Strom_kwh_egon, Strom_kwh_ruecklieferung
    - Computes per-unit costs and injects detailed context variables for the
      "Stromkosten" section in the ODT bill template.

    ODT template variable naming convention:
      ssd_*  Eigenverbrauch Solar direkt (from roof)
      sss_*  Eigenverbrauch Solar via Speicher/Stromallmend
      snh_*  Netzstrombezug Hochtarif
      snt_*  Netzstrombezug Niedertarif
      shk_*  Herkunftsnachweise (HKN) for purchased solar
      sk_*   Korrektur (manual correction)
      st_*   Strom subtotal (before Allgemeinstrom and fees)
      sa_*   Anteil Allgemeinstrom (communal electricity share)
      snk_*  Stromnebenkosten / Messung
      stot_* Grand total

    Suffixes:
      _chft  Building total CHF (formatted string)
      _t     Building total kWh (number)
      _eh    CHF/kWh rate
      (none) Rental unit kWh
      _chf   Rental unit CHF (formatted string)
    """

    cost_type_id = "zev_stromallmend"

    def __init__(self, report_generator: "NkReportGenerator", cost_config: dict):
        super().__init__(report_generator, cost_config)
        self.add_value_type(NkCostValueType.USAGE, "Verbrauch", "kWh")
        self.add_value_type(NkCostValueType.COMMON_USAGE, "Allgemeinverbrauch", "kWh")
        # Per-unit intermediate data: ru_id -> dict
        self._strom_data: dict[int, dict] = {}
        # Building-level totals (populated in load_input_data)
        self._building_totals: dict = {}

        self.tarif_eigenstrom = cost_config.get("tarif_eigenstrom", 0)
        self.tarif_einspeiseverguetung = cost_config.get("tarif_einspeiseverguetung", 12 * [0])
        self.tarif_hkn = cost_config.get("tarif_hkn", 0)
        self.tarif_korrektur = cost_config.get("tarif_korrekturen", {"mittel": 0, "nacht": 0})
        self.korrekturen = cost_config.get("korrekturen", {})
        self._validate_config()

    def load_input_data(self):
        super().load_input_data()

        num_months = self.generator.num_months

        # Building-level: einspeisefaktor per month
        kwh_bezug_zev = self.measurements["building"].get("strom_bezug_zev", num_months * [0])
        kwh_ruecklieferung_ew = self.measurements["building"].get(
            "strom_ruecklieferung_ew", num_months * [0]
        )
        einspeisefaktor = []
        for m in range(num_months):
            if kwh_bezug_zev[m]:
                einspeisefaktor.append(kwh_ruecklieferung_ew[m] / kwh_bezug_zev[m])
            else:
                einspeisefaktor.append(0)

        # Building-level totals accumulators
        totals = {
            "ssd": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # solar direkt
            "sss": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # solar speicher
            "snh": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # netz hoch
            "snt": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # netz nieder
            "shk": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # HKN einkauf
            "sk": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # korrektur
            "total": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},
        }

        for ru in self.generator.rental_units:
            ru_messung = self.measurements["rental_units"].get(ru.name, {})
            if "strom_solar" not in ru_messung:
                self._strom_data[ru.id] = self._zero_strom_data(num_months)
                continue

            messung_solar = ru_messung.get("strom_solar", num_months * [0.0])
            messung_ew_hoch = ru_messung.get("strom_ew_hoch", num_months * [0.0])
            messung_ew_nieder = ru_messung.get("strom_ew_nieder", num_months * [0.0])
            messung_chf_hoch = ru_messung.get("chf_netz_hoch", num_months * [0.0])
            messung_chf_nieder = ru_messung.get("chf_netz_nieder", num_months * [0.0])

            # Korrekturen from config
            kwh_korrektur = num_months * [0.0]
            chf_korrektur = num_months * [0.0]
            if ru.name in self.korrekturen:
                for korr in self.korrekturen[ru.name]:
                    tarif = self.tarif_korrektur.get(korr.get("tarif", "mittel"), 0)
                    for m in range(num_months):
                        kwh_korrektur[m] += korr["kwh"][m]
                        chf_korrektur[m] += korr["kwh"][m] * tarif

            d = {}
            d["kwh_solar"] = list(messung_solar)
            d["kwh_solar_speicher"] = []
            d["kwh_solar_einkauf"] = []
            d["kwh_netzstrom"] = []
            d["kwh_total"] = []
            d["chf_solar_eigen"] = []
            d["chf_solar_speicher"] = []
            d["chf_solar_hkn"] = []
            d["chf_netz_hoch"] = list(messung_chf_hoch)
            d["chf_netz_nieder"] = list(messung_chf_nieder)
            d["kwh_netz_hoch"] = list(messung_ew_hoch)
            d["kwh_netz_nieder"] = list(messung_ew_nieder)
            d["kwh_korrektur"] = kwh_korrektur
            d["chf_korrektur"] = chf_korrektur
            d["chf_total"] = []

            for m in range(num_months):
                kwh_netz = messung_ew_hoch[m] + messung_ew_nieder[m]
                kwh_speicher = einspeisefaktor[m] * kwh_netz
                kwh_einkauf = kwh_netz - kwh_speicher
                kwh_tot = messung_solar[m] + kwh_speicher + kwh_einkauf + kwh_korrektur[m]

                chf_eigen = messung_solar[m] * self.tarif_eigenstrom
                tarif_einsp = (
                    self.tarif_einspeiseverguetung[m]
                    if m < len(self.tarif_einspeiseverguetung)
                    else 0
                )
                chf_speicher = kwh_speicher * (self.tarif_eigenstrom - tarif_einsp)
                chf_hkn = kwh_einkauf * self.tarif_hkn
                chf_tot = (
                    chf_eigen
                    + chf_speicher
                    + chf_hkn
                    + messung_chf_hoch[m]
                    + messung_chf_nieder[m]
                    + chf_korrektur[m]
                )

                d["kwh_solar_speicher"].append(kwh_speicher)
                d["kwh_solar_einkauf"].append(kwh_einkauf)
                d["kwh_netzstrom"].append(kwh_netz)
                d["kwh_total"].append(kwh_tot)
                d["chf_solar_eigen"].append(chf_eigen)
                d["chf_solar_speicher"].append(chf_speicher)
                d["chf_solar_hkn"].append(chf_hkn)
                d["chf_total"].append(chf_tot)

                totals["ssd"]["kwh"][m] += messung_solar[m]
                totals["ssd"]["chf"][m] += chf_eigen
                totals["sss"]["kwh"][m] += kwh_speicher
                totals["sss"]["chf"][m] += chf_speicher
                totals["snh"]["kwh"][m] += messung_ew_hoch[m]
                totals["snh"]["chf"][m] += messung_chf_hoch[m]
                totals["snt"]["kwh"][m] += messung_ew_nieder[m]
                totals["snt"]["chf"][m] += messung_chf_nieder[m]
                totals["shk"]["kwh"][m] += kwh_einkauf
                totals["shk"]["chf"][m] += chf_hkn
                totals["sk"]["kwh"][m] += kwh_korrektur[m]
                totals["sk"]["chf"][m] += chf_korrektur[m]
                totals["total"]["kwh"][m] += kwh_tot
                totals["total"]["chf"][m] += chf_tot

            self._strom_data[ru.id] = d

        # Store building totals as simple sums
        self._building_totals = {
            k: {
                "kwh": sum(v["kwh"]),
                "chf": sum(v["chf"]),
            }
            for k, v in totals.items()
        }

        # Set COST and USAGE totals for the base cost aggregation
        # self.total_values[NkCostValueType.COST].amount = self._building_totals["total"]["chf"]
        self.total_values[NkCostValueType.USAGE].amount = self._building_totals["total"]["kwh"]
        for ru in self.generator.rental_units:
            d = self._strom_data[ru.id]
            # self.rental_unit_values[ru.id][NkCostValueType.COST].amount = sum(d["chf_total"])
            self.rental_unit_values[ru.id][NkCostValueType.USAGE].amount = sum(d["kwh_total"])
            self.rental_unit_values[ru.id][NkCostValueType.COST].monthly_amounts = d["chf_total"]

        # Set common costs from virtual rental unit "allg" (Allgemeinstrom)
        self.set_common_costs(
            self._strom_data[NkVirtualRentalUnitId.COMMON]["chf_total"],
            self._strom_data[NkVirtualRentalUnitId.COMMON]["kwh_total"],
        )

        self.normalize_monthly_amounts()

    def split_costs(self):
        self._calculate_weights()
        self._split_common_costs()
        self._aggregate_monthly_amounts()

    def _get_context(self, ru: "NkRentalUnit", contract: "NkContract") -> dict:
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
    def _zero_strom_data(num_months: int) -> dict:
        zeros = num_months * [0.0]
        return {
            "kwh_solar": list(zeros),
            "kwh_solar_speicher": list(zeros),
            "kwh_solar_einkauf": list(zeros),
            "kwh_netzstrom": list(zeros),
            "kwh_total": list(zeros),
            "chf_solar_eigen": list(zeros),
            "chf_solar_speicher": list(zeros),
            "chf_solar_hkn": list(zeros),
            "chf_netz_hoch": list(zeros),
            "chf_netz_nieder": list(zeros),
            "kwh_netz_hoch": list(zeros),
            "kwh_netz_nieder": list(zeros),
            "kwh_korrektur": list(zeros),
            "chf_korrektur": list(zeros),
            "chf_total": list(zeros),
        }

    def _validate_config(self):
        self._validate_korrekturen(self.korrekturen)

    def _validate_korrekturen(self, korrekturen: dict):
        for ru_name in korrekturen:
            self.generator.get_rental_unit_by_name(ru_name)
            for korr in korrekturen[ru_name]:
                if korr.get("tarif") not in self.tarif_korrektur:
                    raise ValueError(
                        _("Unknown rate for correction: {tarif}").format(tarif=korr.get("tarif"))
                    )
