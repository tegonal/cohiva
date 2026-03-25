from dataclasses import dataclass

from report.nk.cost import NkCost, NkTotalCost


@dataclass
class CostConfig:
    cost_class: type[NkCost]
    config: dict


def get_costs_from_config():
    ## TODO: Implement this with configuration from DB
    costs = [
        {"name": "Hauswartung_ServiceHeizungLüftung"},
        {"name": "Betriebskosten_Gemeinschaft"},
        {
            "name": "Reinigung",
            "section_weights": "reinigung",
        },
        {
            "name": "Winterdienst",
        },
        {"name": "Umgebung_Siedlung"},
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
        {"name": "Kehrichtgebuehren"},
        {
            "name": "Lift",
            "class": NkTotalCost,
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
        },
        {
            "name": "Strom_Total",
            "category": "strom",
            "time_period": "monthly",
            "amount_from_objects": "chf_total",
            "section_weights": None,
            "object_weights": None,
        },
        {"name": "Serviceabo Energiemessung"},
        {
            "name": "Internet/WLAN",
            "category": "internet",
            "time_period": "monthly",
            "amount_from_objects": "chf_internet",
            "section_weights": None,
            "object_weights": None,
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
