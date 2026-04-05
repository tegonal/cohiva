from typing import TYPE_CHECKING

from geno.utils import nformat

from .base import NkCost, NkCostValueType

if TYPE_CHECKING:
    from report.nk.contract import NkContract
    from report.nk.generator import NkReportGenerator
    from report.nk.rental_unit import NkRentalUnit


class NkCostZEVStromallmend(NkCost):
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

    def __init__(self, report: "NkReportGenerator", cost_config: dict):
        super().__init__(report, cost_config)
        self.add_value_type(NkCostValueType.USAGE, "Verbrauch", "kWh")
        # Per-unit intermediate data: ru_id -> dict
        self._strom_data: dict[int, dict] = {}
        # Building-level totals (populated in load_input_data)
        self._building_totals: dict = {}

    def load_input_data(self):
        super().load_input_data()

        config = self.report.config
        tarif_eigenstrom = config.get("Strom:Tarif:Eigenstrom", 0)
        tarif_einspeiseverguetung = config.get("Strom:Tarif:Einspeisevergütung", 12 * [0])
        tarif_hkn = config.get("Strom:Tarif:HKN", 0)
        tarif_korrektur = config.get("Strom:Tarif:Korrekturen", {"mittel": 0, "nacht": 0})

        num_months = self.report.num_months

        # Building-level: einspeisefaktor per month
        kwh_egon = self.report.data_amount.get("Strom_kwh_egon", num_months * [0])
        kwh_ruecklieferung = self.report.data_amount.get(
            "Strom_kwh_ruecklieferung", num_months * [0]
        )
        einspeisefaktor = []
        for m in range(num_months):
            if kwh_egon[m]:
                einspeisefaktor.append(kwh_ruecklieferung[m] / kwh_egon[m])
            else:
                einspeisefaktor.append(0)

        # Building-level totals accumulators
        totals = {
            "ssd": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # solar direkt
            "sss": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # solar speicher
            "snh": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # netz hoch
            "snt": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # netz nieder
            "shk": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},  # HKN einkauf
            "sk": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},   # korrektur
            "total": {"kwh": num_months * [0.0], "chf": num_months * [0.0]},
        }

        for ru in self.report.rental_units:
            if ru.is_virtual:
                self._strom_data[ru.id] = self._zero_strom_data(num_months)
                continue

            ru_messung = self.report.object_messung.get(ru.name, {})
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
            korrektur_config = config.get("Strom:Korrekturen", {})
            if ru.name in korrektur_config:
                for korr in korrektur_config[ru.name]:
                    tarif = tarif_korrektur.get(korr.get("tarif", "mittel"), 0)
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
            d["kwh_korrektur"] = kwh_korrektur
            d["chf_korrektur"] = chf_korrektur
            d["chf_total"] = []

            for m in range(num_months):
                kwh_netz = messung_ew_hoch[m] + messung_ew_nieder[m]
                kwh_speicher = einspeisefaktor[m] * kwh_netz
                kwh_einkauf = kwh_netz - kwh_speicher
                kwh_tot = (
                    messung_solar[m]
                    + kwh_speicher
                    + kwh_einkauf
                    + kwh_korrektur[m]
                )

                chf_eigen = messung_solar[m] * tarif_eigenstrom
                tarif_einsp = (
                    tarif_einspeiseverguetung[m]
                    if m < len(tarif_einspeiseverguetung)
                    else 0
                )
                chf_speicher = kwh_speicher * (tarif_eigenstrom - tarif_einsp)
                chf_hkn = kwh_einkauf * tarif_hkn
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
        self._building_totals_monthly = totals

        # Set COST and USAGE totals for the base cost aggregation
        self.total_values[NkCostValueType.COST].amount = self._building_totals["total"]["chf"]
        self.total_values[NkCostValueType.USAGE].amount = self._building_totals["total"]["kwh"]
        for ru in self.report.rental_units:
            d = self._strom_data[ru.id]
            self.rental_unit_values[ru.id][NkCostValueType.COST].amount = sum(d["chf_total"])
            self.rental_unit_values[ru.id][NkCostValueType.USAGE].amount = sum(d["kwh_total"])
            monthly_amounts = d["chf_total"]
            self.rental_unit_values[ru.id][NkCostValueType.COST].monthly_amounts = monthly_amounts

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

    def get_extra_context(self, ru: "NkRentalUnit", contract: "NkContract") -> dict:
        """Return Stromkosten detail variables for the ODT bill template."""
        d = self._strom_data.get(ru.id, self._zero_strom_data(self.report.num_months))
        bt = self._building_totals

        def fmt(val):
            return nformat(val)

        def rate(chf, kwh):
            return nformat(chf / kwh if kwh else 0, 4)

        # Building totals (formatted)
        ctx = {
            # Eigenverbrauch Solar direkt (from roof)
            "ssd_chft": fmt(bt["ssd"]["chf"]),
            "ssdt": bt["ssd"]["kwh"],
            "ssd_eh": rate(bt["ssd"]["chf"], bt["ssd"]["kwh"]),
            "ssd": sum(d["kwh_solar"]),
            "ssd_chf": fmt(sum(d["chf_solar_eigen"])),
            # Eigenverbrauch Solar via Speicher/Stromallmend
            "sss_chft": fmt(bt["sss"]["chf"]),
            "ssst": bt["sss"]["kwh"],
            "sss_eh": rate(bt["sss"]["chf"], bt["sss"]["kwh"]),
            "sss": sum(d["kwh_solar_speicher"]),
            "sss_chf": fmt(sum(d["chf_solar_speicher"])),
            # Netzstrombezug Hochtarif
            "snh_chft": fmt(bt["snh"]["chf"]),
            "snht": bt["snh"]["kwh"],
            "snh_eh": rate(bt["snh"]["chf"], bt["snh"]["kwh"]),
            "snh": sum(d["kwh_netzstrom"]),
            "snh_chf": fmt(sum(d["chf_netz_hoch"])),
            # Netzstrombezug Niedertarif
            "snt_chft": fmt(bt["snt"]["chf"]),
            "sntt": bt["snt"]["kwh"],
            "snt_eh": rate(bt["snt"]["chf"], bt["snt"]["kwh"]),
            "snt": sum(d["kwh_netzstrom"]),  # combined with Hoch for total netz
            "snt_chf": fmt(sum(d["chf_netz_nieder"])),
            # Herkunftsnachweise (HKN)
            "shk_chft": fmt(bt["shk"]["chf"]),
            "shkt": bt["shk"]["kwh"],
            "shk_eh": rate(bt["shk"]["chf"], bt["shk"]["kwh"]),
            "shk": sum(d["kwh_solar_einkauf"]),
            "shk_chf": fmt(sum(d["chf_solar_hkn"])),
            # Korrektur
            "sk_chft": fmt(bt["sk"]["chf"]),
            "skt": bt["sk"]["kwh"],
            "sk_eh": rate(bt["sk"]["chf"], bt["sk"]["kwh"]),
            "sk": sum(d["kwh_korrektur"]),
            "sk_chf": fmt(sum(d["chf_korrektur"])),
            # Strom subtotal (sum of above, no separate Allgemeinstrom/fees in this class)
            "st_chft": fmt(bt["total"]["chf"]),
            "stt": bt["total"]["kwh"],
            "st": sum(d["kwh_total"]),
            "st_chf": fmt(sum(d["chf_total"])),
            # Anteil Allgemeinstrom (not computed by this class – leave empty)
            "sa_chft": "",
            "sat": "",
            "sa_eh": "",
            "sa": "",
            "sa_chf": "",
            # Stromnebenkosten/Messung (not computed by this class – leave empty)
            "snk_chft": "",
            "snkt": "",
            "snk_eh": "",
            "snk": "",
            "snk_chf": "",
            # Grand total
            "stot_chft": fmt(bt["total"]["chf"]),
            "stot_chf": fmt(sum(d["chf_total"])),
        }
        return ctx

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
            "kwh_korrektur": list(zeros),
            "chf_korrektur": list(zeros),
            "chf_total": list(zeros),
        }
