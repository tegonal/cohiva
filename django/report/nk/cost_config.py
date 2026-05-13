from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from report.nk.cost import (
    NkCost,
    NkCostVEWA,
    NkCostZEVStromallmend,
    NkPerRentalUnitCost,
    NkTotalCost,
)
from report.nk.cost.vewa import NkCostVEWACategories
from report.nk.measurement_data import (
    NkMeasurementDataAnnual,
    NkMeasurementDataBase,
    NkMeasurementDataEgon,
    NkMeasurementDataMonthlyCSVFile,
)


class CostConfigFieldTypes(Enum):
    NKCOST_CLASS = 1
    STRING = 2
    STRING_LIST = 3
    BOOL = 4
    INPUT_KEY = 5
    MEASUREMENT_SOURCES = 6
    VEWA_CATEGORY = 7

@dataclass
class CostConfigField:
    key: str
    type: CostConfigFieldTypes
    required: bool = True
    subfields: list["CostConfigField | CostConfigMeasurementSourceField"] | None = None


@dataclass
class CostConfigMeasurementSourceField:
    key: str
    supported_sources: list[type[NkMeasurementDataBase]]
    keys: list[str]


@dataclass
class CostConfig:
    cost_class: type[NkCost]
    config: dict

    @classmethod
    def get_fields(cls):
        return [
            CostConfigField("class", CostConfigFieldTypes.NKCOST_CLASS),
            CostConfigField("name", CostConfigFieldTypes.STRING),
            CostConfigField("bezeichnung", CostConfigFieldTypes.STRING),
            CostConfigField("billing_group", CostConfigFieldTypes.STRING, required=False),
            CostConfigField(
                "section_weights", CostConfigFieldTypes.STRING, required=False
            ),  # TODO: Where to get the value from? Should this be an input_key?
        ]


@dataclass
class NkTotalCostConfig(CostConfig):
    def get_fields(cls):
        return super().get_fields()


@dataclass
class NkPerRentalUnitCostConfig(CostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField("fee_per_unit_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("fee_per_person_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("fixed_fees_key", CostConfigFieldTypes.INPUT_KEY),
        ]


@dataclass
class NkZEVStromallmendCostConfig(CostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField("tarif_eigenstrom_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("tarif_einspeiseverguetung_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("tarif_hkn_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("tarif_korrektur_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("korrekturen_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField(
                "measurement_data",
                CostConfigFieldTypes.MEASUREMENT_SOURCES,
                subfields=[
                    CostConfigMeasurementSourceField(
                        "building",
                        supported_sources=[NkMeasurementDataMonthlyCSVFile],
                        keys=["strom_bezug_zev", "strom_ruecklieferung_ew"],
                    ),
                    CostConfigMeasurementSourceField(
                        "rental_units",
                        supported_sources=[NkMeasurementDataEgon],
                        keys=[
                            "strom_ew_nieder",
                            "strom_ew_hoch",
                            "strom_solar",
                            "chf_netz_nieder",
                            "chf_netz_hoch",
                        ],
                    ),
                ],
            ),
        ]
        # Example generated measurement sources config:
        #
        # "building": {
        #    "class": NkMeasurementDataMonthlyCSVFile,
        #    "file_key": "Messdaten:Liegenschaft",
        #    "headers": {
        #        "month": "Monat",
        #        "strom_bezug_zev": "Strom_kwh_egon",  # kWh bezogen von EW, gem. Messung durch ZEV intern
        #        "strom_ruecklieferung_ew": "Strom_kwh_ruecklieferung",  # kWh rückgeliefert, gem. Messung durch EW
        #    },
        # },
        # "rental_units": {
        #    "class": NkMeasurementDataEgon,
        #    "file_key": "Messdaten:Mieteinheiten",
        #    "file_prefix": "egon_Strom",
        #    "headers": {
        #        "rental_unit": "Gebäudeeinheit",
        #        "time_period": "Mieter Abrechnungsperiode",
        #        "strom_ew_nieder": "Strombezug Niedertarif(kWh)",
        #        "strom_ew_hoch": "Strombezug Hochtarif EW (kWh)",
        #        "strom_solar": "Solarstrom (kWh)",
        #        "chf_netz_nieder": "Strombezug Niedertarif(CHF)",
        #        "chf_netz_hoch": "Strombezug EW (CHF)",
        #    },
        # },


@dataclass
class NkVEWACostConfig(NkTotalCostConfig):
    def get_fields(cls):
        return super().get_fields(cls) + [
            CostConfigField("vewa_category", CostConfigFieldTypes.VEWA_CATEGORY),
            CostConfigField("base_cost_factor_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("exclude_zero_usage_units", CostConfigFieldTypes.BOOL, required=False),
            CostConfigField(
                "common_cost_section_weights", CostConfigFieldTypes.STRING, required=False
            ),  # TODO: Where to get the value from? Should this be an input_key?
            CostConfigField(
                "measurement_data",
                CostConfigFieldTypes.MEASUREMENT_SOURCES,
                subfields=[
                    CostConfigMeasurementSourceField(
                        "building",
                        supported_sources=[NkMeasurementDataAnnual],
                        keys=["usage", "costs"],
                    ),
                    CostConfigMeasurementSourceField(
                        "rental_units",
                        supported_sources=[NkMeasurementDataEgon],
                        keys=["usage"],
                    ),
                ],
            ),
        ]
        # Example generated config:
        #
        # "class": NkCostVEWA,
        # "name": "Wasser_Abwasser",
        # "billing_group": "Wasserkosten",
        # "vewa_category": NkCostVEWACategories.WATER_GENERAL,
        # "base_cost_factor_key": "Wasserkosten:Grundkostenanteil",
        # "exclude_zero_usage_units": True,
        # "measurement_data": {
        #     "building": {
        #         "class": NkMeasurementDataAnnual,
        #         "value_key": "Messdaten:Wasserverbrauch",
        #     },
        #     "rental_units": {
        #         "class": NkMeasurementDataEgon,
        #         "file_key": "Messdaten:Mieteinheiten",
        #         "file_prefix": "egon_Waerme",
        #         "headers": {
        #             "rental_unit": "Gebäudeeinheit",
        #             "time_period": "Mieter Abrechnungsperiode",
        #             "usage": "Warmwasser Verbrauch (Kubikmeter)",
        #         },
        #     },
        # },
        #


@dataclass
class MeasurementSourceConfigField:
    name: str
    type: CostConfigFieldTypes
    required: bool = True
    subfields: list[str] | None = None


@dataclass
class MeasurementSourceConfig:
    pass


@dataclass
class NkMeasurementDataAnnualConfig(MeasurementSourceConfig):
    @classmethod
    def get_fields(cls):
        return [MeasurementSourceConfigField("value_key", CostConfigFieldTypes.INPUT_KEY)]
        # Example generated measurement sources config:
        #
        # "measurement_data": {
        #     "building": {
        #         "class": NkMeasurementDataAnnual,
        #         "value_key": "Messdaten:Wasserverbrauch",
        #     },


@dataclass
class NkMeasurementDataMonthlyConfig(MeasurementSourceConfig):
    @classmethod
    def get_fields(cls):
        return [
            MeasurementSourceConfigField("file_key", CostConfigFieldTypes.INPUT_KEY),
            MeasurementSourceConfigField(
                "required_headers", CostConfigFieldTypes.STRING_LIST, subfields=["month"]
            ),
        ]
        # Example generated measurement sources config:
        #
        # "building": {
        #    "class": NkMeasurementDataMonthlyCSVFile,
        #    "file_key": "Messdaten:Liegenschaft",
        #    "headers": {
        #        "month": "Monat",
        #        "strom_bezug_zev": "Strom_kwh_egon",  # kWh bezogen von EW, gem. Messung durch ZEV intern
        #        "strom_ruecklieferung_ew": "Strom_kwh_ruecklieferung",  # kWh rückgeliefert, gem. Messung durch EW
        #    },
        # },


@dataclass
class NkMeasurementDataEgonConfig(MeasurementSourceConfig):
    @classmethod
    def get_fields(cls):
        return [
            MeasurementSourceConfigField("file_key", CostConfigFieldTypes.INPUT_KEY),
            MeasurementSourceConfigField("file_prefix", CostConfigFieldTypes.STRING),
            MeasurementSourceConfigField(
                "required_headers",
                CostConfigFieldTypes.STRING_LIST,
                subfields=["rental_unit", "time_period"],
            ),
        ]
        # Example generated measurement sources config:
        #
        # "measurement_data": {
        #     "rental_units": {
        #         "class": NkMeasurementDataEgon,
        #         "file_key": "Messdaten:Mieteinheiten",
        #         "file_prefix": "egon_Waerme",
        #         "headers": {
        #             "rental_unit": "Gebäudeeinheit",
        #             "time_period": "Mieter Abrechnungsperiode",
        #             "usage": "Warmwasser Verbrauch (Kubikmeter)",
        #         },
        #     },
        # },


def get_costs_from_config() -> Iterator[CostConfig]:
    ## TODO: Implement this with configuration from DB
    costs = [
        {
            "name": "Hauswartung_ServiceHeizungLüftung",
            "bezeichnung": "Hauswartung (Service, Heizung, Lüftung)",
            "billing_group": "Hauswartung, Service Heizung/Lüftung",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Reinigung",
            "bezeichnung": "Reinigung",
            "section_weights": "reinigung",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Umgebung_Siedlung",
            "bezeichnung": "Umgebung/Siedlungspflege",
            "billing_group": "Siedlung/Umgebungspflege",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Betriebskosten_Gemeinschaft",
            "bezeichnung": "Betriebskosten Gemeinschaftsanlagen",
            "billing_group": "Betriebskosten Gemeinschaftsanlagen",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Winterdienst",
            "bezeichnung": "Winterdienst",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Lift",
            "bezeichnung": "Lift",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Kehrichtgebuehren",
            "bezeichnung": "Kehrichtgebühren",
            "billing_group": "Kehrichtgebühren",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "Fernwaerme_Fussboden_Grundkosten",
            "bezeichnung": "Fernwärme Fußbodenheizung: Grundkosten",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Fussboden",  ## Will be imported
            "amount_factor": 0.3,  ## 30% Grundkosten gemäss Modell Verbrauchsabh. NK-Abrechnung
            "section_weights": "nur_wohnen",
            "object_weights": "volume",  #'area',
        },
        {
            "name": "Fernwaerme_Fussboden_Verbrauch",
            "bezeichnung": "Fernwärme Fußbodenheizung: Verbrauch",
            "category": "waerme_wasser_verbrauch",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Fussboden",  ## Will be imported
            "amount_factor": 0.7,
            "section_weights": "nur_wohnen",
            "object_weights": "messung_heizung",
        },
        {
            "name": "Fernwaerme_Radiatoren",
            "bezeichnung": "Fernwärme: Radiatoren",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Radiatoren",  ## Will be imported
            "section_weights": "radiatoren",
            "object_weights": "volume",
        },
        {
            "name": "Fernwaerme_Lueftung",
            "bezeichnung": "Fernwärme: Lüftung",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_data": "Fernwaerme_Lueftung",  ## Will be imported
            "section_weights": "lueftung",  #'default',
            "object_weights": "volume",  #'area',
        },
        {
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Fernwaerme_Warmwasser",
            "bezeichnung": "Fernwärme: Warmwasser",
            "billing_group": "Wärmekosten",
            "vewa_category": NkCostVEWACategories.HEAT_WATER,
            "base_cost_factor_key": "VEWA:GrundkostenanteilWarmwasser",
            "exclude_zero_usage_units": True,
            "common_cost_section_weights": "wasser_allgemein",
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataMonthlyCSVFile,
                    "file_key": "Messdaten:Liegenschaft",
                    "headers": {
                        "month": "Monat",
                        "costs": "Fernwaerme_Warmwasser",
                    },
                },
                "rental_units": {
                    "class": NkMeasurementDataEgon,
                    "file_key": "Messdaten:Mieteinheiten",
                    "file_prefix": "egon_Waerme",
                    "headers": {
                        "rental_unit": "Gebäudeeinheit",
                        "time_period": "Mieter Abrechnungsperiode",
                        "usage": "Warmwasser Verbrauch (Kubikmeter)",
                    },
                },
            },
        },
        {
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Fernwaerme_Fussboden",
            "bezeichnung": "Fernwärme: Fussbodenheizung",
            "billing_group": "Wärmekosten",
            "vewa_category": NkCostVEWACategories.HEAT_HEATING,
            "section_weights": "nur_wohnen",
            "object_weights": "volume",  #'area',
            "base_cost_factor_key": "VEWA:GrundkostenanteilHeizung",
            "exclude_zero_usage_units": False,
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataMonthlyCSVFile,
                    "file_key": "Messdaten:Liegenschaft",
                    "headers": {
                        "month": "Monat",
                        "costs": "Fernwaerme_Fussboden",
                    },
                },
                "rental_units": {
                    "class": NkMeasurementDataEgon,
                    "file_key": "Messdaten:Mieteinheiten",
                    "file_prefix": "egon_Waerme",
                    "headers": {
                        "rental_unit": "Gebäudeeinheit",
                        "time_period": "Mieter Abrechnungsperiode",
                        "usage": "Wärmeverbrauch (kWh)",
                    },
                },
            },
        },
        {
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Fernwaerme_Radiatoren",
            "bezeichnung": "Fernwärme: Radiatoren",
            "billing_group": "Wärmekosten",
            "vewa_category": NkCostVEWACategories.HEAT_HEATING,
            "section_weights": "radiatoren",
            "object_weights": "volume",
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataMonthlyCSVFile,
                    "file_key": "Messdaten:Liegenschaft",
                    "headers": {
                        "month": "Monat",
                        "costs": "Fernwaerme_Radiatoren",
                    },
                },
            },
        },
        {
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Fernwaerme_Lueftung",
            "bezeichnung": "Fernwärme: Lüftung",
            "billing_group": "Wärmekosten",
            "vewa_category": NkCostVEWACategories.HEAT_HEATING,
            "section_weights": "lueftung",
            "object_weights": "volume",
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataMonthlyCSVFile,
                    "file_key": "Messdaten:Liegenschaft",
                    "headers": {
                        "month": "Monat",
                        "costs": "Fernwaerme_Lueftung",
                    },
                },
            },
        },
        {
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Wasser_Abwasser",
            "bezeichnung": "Wasser/Abwasser",
            "billing_group": "Wasserkosten",
            "vewa_category": NkCostVEWACategories.WATER_GENERAL,
            "base_cost_factor_key": "Wasserkosten:Grundkostenanteil",
            "exclude_zero_usage_units": False,
            "common_cost_section_weights": "wasser_allgemein",
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataAnnual,
                    "value_key": "Messdaten:Wasserverbrauch",
                },
                "rental_units": {
                    "class": NkMeasurementDataEgon,
                    "file_key": "Messdaten:Mieteinheiten",
                    "file_prefix": "egon_Waerme",
                    "headers": {
                        "rental_unit": "Gebäudeeinheit",
                        "time_period": "Mieter Abrechnungsperiode",
                        "usage": "Warmwasser Verbrauch (Kubikmeter)",
                    },
                },
            },
        },
        {
            "class": NkCostZEVStromallmend,
            "config": NkZEVStromallmendCostConfig,
            "name": "Strom_Total",
            "bezeichnung": "Stromkosten",
            "billing_group": "Stromkosten",
            "tarif_eigenstrom_key": "Strom:Tarif:Eigenstrom",
            "tarif_einspeiseverguetung_key": "Strom:Tarif:Einspeisevergütung",
            "tarif_hkn_key": "Strom:Tarif:HKN",
            "tarif_korrektur_key": "Strom:Tarif:Korrekturen",
            "korrekturen_key": "Strom:Korrekturen",
            "measurement_data": {
                "building": {
                    "class": NkMeasurementDataMonthlyCSVFile,
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
            "bezeichnung": "Serviceabo Energiemessung",
            # "class": NkTotalCost, Currently included with Strom total, add it later
        },
        {
            "class": NkPerRentalUnitCost,
            "config": NkPerRentalUnitCostConfig,
            "name": "Internet/WLAN",
            "bezeichnung": "Internet/WLAN",
            # "category": "internet",
            "fee_per_unit_key": "Internet:Tarif:ProWohnung",
            "fee_per_person_key": "Internet:Tarif:ProPerson",
            "fixed_fees_key": "Internet:Tarif:Fix",
        },
        ## Anteile an "Allgemein" (special object 0000)
        {
            "name": "Anteil_Allgemein_Warmwasser_Verbrauch",
            "bezeichnung": "Anteil Allgemein Warmwasser Verbrauch",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_meta": "Fernwaerme_Warmwasser_Verbrauch",  ## Will be imported
            "section_weights": "wasser_allgemein",
        },
        {
            "name": "Anteil_Allgemein_Wasser_Abwasser_Verbrauch",
            "bezeichnung": "Anteil Allgemein Wasser/Abwasser Verbrauch",
            "category": "waerme_wasser_grund",
            "time_period": "monthly",
            "amount_meta": "Wasser_Abwasser_Verbrauch",  ## Will be imported
            "section_weights": "wasser_allgemein",
        },
        {
            "name": "Anteil_Allgemein_Strom",
            "bezeichnung": "Anteil Allgemein Strom",
            "category": "strom_allgemein",
            "time_period": "monthly",
            "amount_meta": "Strom_Total",  ## Will be imported
        },
    ]
    for cost in costs:
        if "class" in cost:
            yield CostConfig(cost.get("class"), cost)

def _build_report_item_categories() -> tuple[tuple[str, str], ...]:
    categories: dict[str, str] = {}
    for cost in get_costs_from_config():
        key = cost.cost_class.__name__
        # Multiple labels per Class are possible.
        categories[cost.config.get("name", key)] = cost.config.get("bezeichnung", key)
    # order returned tuple by label
    return tuple(sorted(categories.items(), key=lambda item: (item[1], item[0])))

REPORT_ITEM_CATEGORY = _build_report_item_categories()
