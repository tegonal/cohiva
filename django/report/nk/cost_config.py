import datetime
from collections.abc import Iterator
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
from report.nk.cost.vewa import VEWA_CATEGORY_DESCRIPTIONS, NkCostVEWACategories
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
    DATE = 7
    INT = 8
    FLOAT = 9
    FILE = 10
    JSON = 11
    VEWA_CATEGORY = 12
    SECTION_WEIGHTS = 13
    MONTHLY_WEIGHTS = 14
    OBJECT_WEIGHTS = 15


@dataclass
class CostConfigField:
    key: str
    type: CostConfigFieldTypes
    required: bool = True
    subfields: list["CostConfigField | CostConfigMeasurementSourceField"] | None = None
    verbose_name: str | None = None

    def __str__(self):
        if self.verbose_name:
            return self.verbose_name
        return self.key


@dataclass
class CostConfigMeasurementSourceField:
    key: str
    supported_sources: list[type[NkMeasurementDataBase]]
    keys: list[str]


@dataclass
class BaseSettingsConfig:
    config: dict

    @classmethod
    def get_fields(cls):
        return [
            CostConfigField("name", CostConfigFieldTypes.STRING),
            CostConfigField("bezeichnung", CostConfigFieldTypes.STRING),
            CostConfigField(
                "Startjahr", CostConfigFieldTypes.INT, verbose_name="Startjahr der Abrechnung"
            ),
            CostConfigField(
                "Vorlage:Abrechnung",
                CostConfigFieldTypes.FILE,
                verbose_name="ODT Vorlage für die Abrechnugn",
            ),
            CostConfigField(
                "Vorlage:EmpfehlungAkonto",
                CostConfigFieldTypes.FILE,
                verbose_name="ODT Vorlage für Empfehlung Anpassung Akonto",
            ),
            CostConfigField(
                "Ausgabe:LimitiereVertragsIDs",
                CostConfigFieldTypes.JSON,
                verbose_name="Ausgabe auf diese Vertrags IDs limitieren",
            ),
            CostConfigField(
                "Ausgabe:QR-Rechnungen",
                CostConfigFieldTypes.BOOL,
                verbose_name="PDFs/QR-Rechnungen erstellen und buchen?",
            ),
            CostConfigField(
                "Ausgabe:Plots", CostConfigFieldTypes.BOOL, verbose_name="Analyse-Plots erstellen?"
            ),
            CostConfigField(
                "Vorperiode:Bezeichnung",
                CostConfigFieldTypes.STRING,
                verbose_name='Bezeichnung der Vorperiode z.B. "2022/2023"',
            ),  # z.B. "2022/2023"
            CostConfigField(
                "Vorperiode:Datei",
                CostConfigFieldTypes.FILE,
                verbose_name="Datei der Vorperiode (json)",
            ),
        ]


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
            CostConfigField(
                "billing_group",
                CostConfigFieldTypes.STRING,
                required=False,
                verbose_name="Kosten zusammenfassen unter (optional)",
            ),
            CostConfigField(
                "monthly_weights",
                CostConfigFieldTypes.MONTHLY_WEIGHTS,
                verbose_name="Verteilschlüssel nach Monat",
            ),
            CostConfigField(
                "section_weights",
                CostConfigFieldTypes.SECTION_WEIGHTS,
                verbose_name="Verteilschlüssel nach Objekttyp",
            ),
        ]


@dataclass
class NkTotalCostConfig(CostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField(
                "object_weights",
                CostConfigFieldTypes.OBJECT_WEIGHTS,
                verbose_name="Verteilschlüssel nach Mietobjekt",
            ),
            CostConfigField("Betrag", CostConfigFieldTypes.FLOAT),
        ]


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
    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField("vewa_category", CostConfigFieldTypes.VEWA_CATEGORY),
            CostConfigField("base_cost_factor_key", CostConfigFieldTypes.INPUT_KEY),
            CostConfigField("exclude_zero_usage_units", CostConfigFieldTypes.BOOL, required=False),
            CostConfigField(
                "common_cost_section_weights", CostConfigFieldTypes.SECTION_WEIGHTS, required=False
            ),
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


def get_report_item_config() -> Iterator[CostConfig | BaseSettingsConfig]:
    """Get a list of implemented cost types that should be available in the UI"""
    # The first element is always general settings
    # Default values
    default_base_settings = {
        "name": "BaseSettings",
        "bezeichnung": "Grundeinstellungen",
        "Startjahr": datetime.date.today().year,
        "config": BaseSettingsConfig,
    }
    yield BaseSettingsConfig(default_base_settings)
    cost_item_types = [
        {
            "name": "Standard",
            "bezeichnung": "Standard-Nebenkosten (Betrag pro Jahr, verteilt nach Schlüssel)",
            "billing_group": "Hauswartung",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        }
    ]
    for cost in cost_item_types:
        if "class" in cost:
            yield CostConfig(cost.get("class"), cost)


def get_costs_from_config(report) -> Iterator[CostConfig]:
    """Get the list of the configured costs from the Report config with actual values for this run."""


def get_costs_from_config_for_tests() -> Iterator[CostConfig]:
    ## Test configuration that is used for tests (Warmbächli reference configuration)
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
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Fernwaerme_Warmwasser",
            "bezeichnung": "Fernwärme: Warmwasser",
            "billing_group": "Wärmekosten",
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
            "class": NkCostVEWA,
            "config": NkVEWACostConfig,
            "name": "Fernwaerme_Fussboden",
            "bezeichnung": "Fernwärme: Fussbodenheizung",
            "billing_group": "Wärmekosten",
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
            "class": NkTotalCost,
        },
        {
            "class": NkPerRentalUnitCost,
            "config": NkPerRentalUnitCostConfig,
            "name": "Internet/WLAN",
            "bezeichnung": "Internet/WLAN",
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


def _build_report_item_categories() -> tuple[tuple[str, str], ...]:
    categories: dict[str, str] = {}
    for cost in get_report_item_config():
        if isinstance(cost, BaseSettingsConfig):
            key = "BaseSettingsConfig"
        else:
            key = cost.cost_class.__name__
        # Multiple labels per Class are possible.
        categories[cost.config.get("name", key)] = cost.config.get("bezeichnung", key)
    # order returned tuple by label
    return tuple(sorted(categories.items(), key=lambda item: (item[1], item[0])))


def build_section_weights_choices() -> list[tuple[str, str]]:
    ## Section weights are still hard-coded. We need
    ## a better way to configure them in the future.
    from report.nk.generator import NK_SECTION_WEIGHTS

    return _build_weights_choices_from_dict(NK_SECTION_WEIGHTS)


def build_monthly_weights_choices() -> list[tuple[str, str]]:
    ## Monthly weights are still hard-coded. We need
    ## a better way to configure them in the future.
    from report.nk.generator import NK_MONTHLY_WEIGHTS

    return _build_weights_choices_from_dict(NK_MONTHLY_WEIGHTS)


def _build_weights_choices_from_dict(weights: dict) -> list[tuple[str, str]]:
    choices = []
    for weight, values in weights.items():
        vals = []
        for k, v in values.items():
            vals.append(f"{k}: {v}")
        choices.append((weight, f"{weight}: " + ", ".join(vals)))
    return choices


def build_vewa_category_choices() -> list[tuple[str, str]]:
    choices = []
    for cat in NkCostVEWACategories:
        choices.append((cat.name, VEWA_CATEGORY_DESCRIPTIONS.get(cat.name), cat.name))
    return choices


def build_object_weights_choices() -> list[tuple[str, str]]:
    return [
        ("area", "Fläche (m2)"),
        ("volume", "Volumen (m3)"),
        ("rooms", "Zimmeranzahl"),
        ("min_occupancy", "Mindestbelegung"),
        ("uniform", "Gleichverteilung"),
        ("nk_factor_1", "NK-Faktor 1"),
        ("nk_factor_2", "NK-Faktor 2"),
        ("nk_factor_3", "NK-Faktor 3"),
    ]


REPORT_ITEM_CATEGORY = _build_report_item_categories()
