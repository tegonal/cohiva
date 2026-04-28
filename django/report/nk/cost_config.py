from dataclasses import dataclass

from report.nk.cost import NkCost, NkCostZEVStromallmend, NkPerRentalUnitCost, NkTotalCost
from report.nk.measurement_data import (
    NkMeasurementDataEgon,
    NkMeasurementDataMonthly,
)


@dataclass
class CostConfig:
    cost_class: type[NkCost]
    config: dict


def get_costs_from_config():
    ## TODO: Implement this with configuration from DB
    costs = [
        {
            "name": "Hauswartung_ServiceHeizungLüftung",
            "billing_group": "Hauswartung, Service Heizung/Lüftung",
            "class": NkTotalCost,
        },
        {
            "name": "Reinigung",
            "section_weights": "reinigung",
            "class": NkTotalCost,
        },
        {
            "name": "Umgebung_Siedlung",
            "billing_group": "Siedlung/Umgebungspflege",
            "class": NkTotalCost,
        },
        {
            "name": "Betriebskosten_Gemeinschaft",
            "billing_group": "Betriebskosten Gemeinschaftsanlagen",
            "class": NkTotalCost,
        },
        {
            "name": "Winterdienst",
            "class": NkTotalCost,
        },
        {
            "name": "Lift",
            "class": NkTotalCost,
        },
        {
            "name": "Kehrichtgebuehren",
            "billing_group": "Kehrichtgebühren",
            "class": NkTotalCost,
        },
        {
            "name": "Wasser_Abwasser_Grundkosten",
            "category": "waerme_wasser_grund",
            "amount_factor": 0.3,
        },
        {
            "name": "Wasser_Abwasser_Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "amount_factor": 0.7,
            "object_weights": "messung_wasser",
        },
        {
            "name": "Fernwaerme_Fussboden_Grundkosten",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Fussboden",  ## Will be imported
            "amount_factor": 0.3,  ## 30% Grundkosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "section_weights": "nur_wohnen",
            "object_weights": "volume",  #'area',
        },
        {
            "name": "Fernwaerme_Fussboden_Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Fussboden",  ## Will be imported
            "amount_factor": 0.7,
            "section_weights": "nur_wohnen",
            "object_weights": "messung_heizung",
        },
        {
            "name": "Fernwaerme_Radiatoren",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Radiatoren",  ## Will be imported
            "section_weights": "radiatoren",
            "object_weights": "volume",
        },
        {
            "name": "Fernwaerme_Lueftung",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Lueftung",  ## Will be imported
            "section_weights": "lueftung",  #'default',
            "object_weights": "volume",  #'area',
        },
        {
            "name": "Fernwaerme_Warmwasser_Grundkosten",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Warmwasser",  ## Will be imported
            "amount_factor": 0.3,  ## 30% Grundkosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "object_weights": "area_warmwasser",
        },
        {
            "name": "Fernwaerme_Warmwasser_Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Warmwasser",  ## Will be imported
            "amount_factor": 0.7,  ## 70% Verbrauchsabhängige Kosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "object_weights": "messung_warmwasser",
            "data_file_prefix": "egon_Waerme",
            "data_headers": {
                "rental_unit": "Gebäudeeinheit",
                "time_period": "Mieter Abrechnungsperiode",
                "warmwasser": "Warmwasser Verbrauch (Kubikmeter)",
                "heizung": "Wärmeverbrauch (kWh)",
            },
        },
        {
            "class": NkCostZEVStromallmend,
            "name": "Strom_Total",
            "billing_group": "Stromkosten",
            "tarif_eigenstrom_key": "Strom:Tarif:Eigenstrom",
            "tarif_einspeiseverguetung_key": "Strom:Tarif:Einspeisevergütung",
            "tarif_hkn_key": "Strom:Tarif:HKN",
            "tarif_korrektur_key": "Strom:Tarif:Korrekturen",
            "korrekturen_key": "Strom:Korrekturen",
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataMonthly,
                    "file_key": "Messdaten:Liegenschaft",
                    "headers": {
                        "month": "Monat",
                        "strom_bezug_zev": "Strom_kwh_egon",  # kWh bezogen von EW, gem. Messung durch ZEV intern
                        "strom_ruecklieferung_ew": "Strom_kwh_ruecklieferung",  # kWh rückgeliefert, gem. Messung durch EW
                    },
                },
                "rental_units": {
                    "class": NkMeasurementDataEgon,
                    "file_key": "Messdaten:Mieteinheiten",
                    "file_prefix": "egon_Strom",
                    "headers": {
                        "rental_unit": "Gebäudeeinheit",
                        "time_period": "Mieter Abrechnungsperiode",
                        "strom_ew_nieder": "Strombezug Niedertarif(kWh)",
                        "strom_ew_hoch": "Strombezug Hochtarif EW (kWh)",
                        "strom_solar": "Solarstrom (kWh)",
                        "chf_netz_nieder": "Strombezug Niedertarif(CHF)",
                        "chf_netz_hoch": "Strombezug EW (CHF)",
                    },
                },
            },
        },
        {
            "name": "Serviceabo Energiemessung",
            # "class": NkTotalCost, Currently included with Strom total, add it later
        },
        {
            "class": NkPerRentalUnitCost,
            "name": "Internet/WLAN",
            "category": "internet",
            "fee_per_unit_key": "Internet:Tarif:ProWohnung",
            "fee_per_person_key": "Internet:Tarif:ProPerson",
            "fixed_fees_key": "Internet:Tarif:Fix",
        },
        ## Anteile an "Allgemein" (special object 0000)
        {
            "name": "Anteil_Allgemein_Warmwasser_Verbrauch",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_meta": "Fernwaerme_Warmwasser_Verbrauch",  ## Will be imported
            "section_weights": "wasser_allgemein",
        },
        {
            "name": "Anteil_Allgemein_Wasser_Abwasser_Verbrauch",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_meta": "Wasser_Abwasser_Verbrauch",  ## Will be imported
            "section_weights": "wasser_allgemein",
        },
        {
            "name": "Anteil_Allgemein_Strom",
            "category": "strom_allgemein",
            "time_period": "monthly",
            "amount_meta": "Strom_Total",  ## Will be imported
        },
    ]
    for cost in costs:
        if "class" in cost:
            yield CostConfig(cost.get("class"), cost)
