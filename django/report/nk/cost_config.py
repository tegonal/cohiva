from dataclasses import dataclass
from enum import Enum

from report.nk.cost import (
    NkAdminFeeCost,
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
            CostConfigField("billing_group", CostConfigFieldTypes.STRING, required=False),
            CostConfigField(
                "section_weights", CostConfigFieldTypes.STRING, required=False
            ),  # TODO: Where to get the value from? Should this be an input_key?
        ]


@dataclass
class NkTotalCostConfig(CostConfig):
    pass


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
        return super().get_fields() + [
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
        # "base_cost_factor_key": "VEWA:Grundkostenanteil",
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


def get_costs_from_config():
    ## TODO: Implement this with configuration from DB
    ## Cost config for tests
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
            "name": "Fernwaerme_Warmwasser",
            "billing_group": "Wärmekosten",
            "class": NkCostVEWA,
            "vewa_category": NkCostVEWACategories.HEAT_WATER,
            "base_cost_factor_key": "VEWA:Grundkostenanteil",
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
            "name": "Fernwaerme_Fussboden",
            "billing_group": "Wärmekosten",
            "class": NkCostVEWA,
            "vewa_category": NkCostVEWACategories.HEAT_HEATING,
            "section_weights": "nur_wohnen",
            "object_weights": "volume",  #'area',
            "base_cost_factor_key": "VEWA:Grundkostenanteil",
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
            "name": "Fernwaerme_Radiatoren",
            "billing_group": "Wärmekosten",
            "class": NkCostVEWA,
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
            "name": "Fernwaerme_Lueftung",
            "billing_group": "Wärmekosten",
            "class": NkCostVEWA,
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
            "name": "Wasser_Abwasser",
            "billing_group": "Wasserkosten",
            "class": NkCostVEWA,
            "vewa_category": NkCostVEWACategories.WATER_GENERAL,
            "base_cost_factor_key": "VEWA:Grundkostenanteil",
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
            "name": "Strom_Total",
            "billing_group": "Stromkosten",
            "class": NkCostZEVStromallmend,
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
            "class": NkTotalCost,
        },
        {
            "name": "Internet/WLAN",
            "class": NkPerRentalUnitCost,
            "fee_per_unit_key": "Internet:Tarif:ProWohnung",
            "fee_per_person_key": "Internet:Tarif:ProPerson",
            "fixed_fees_key": "Internet:Tarif:Fix",
        },
        {
            "name": "Verwaltungsaufwand",
            "class": NkAdminFeeCost,
            "fee_percentage_key": "Verwaltungsaufwand:Faktor",
        },
    ]
    for cost in costs:
        if "class" in cost:
            yield CostConfig(cost.get("class"), cost)
