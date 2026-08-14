import datetime
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from report.models import ReportInputData

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
    # NKCOST_CLASS = 1
    STRING = 2
    STRING_LIST = 3
    BOOL = 4
    # INPUT_KEY = 5
    # MEASUREMENT_SOURCES = 6
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
    is_measurement: bool = False

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
                verbose_name="ODT Vorlage für die Abrechnung",
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

    @classmethod
    def build(cls, item_config: dict, report_input_data):
        config = {}
        field: ReportInputData
        for field in report_input_data:
            config[field.name.name] = field.get_value()
        return cls(config)

    def set_name(self, name):
        self.config["name"] = name


@dataclass
class CostConfig:
    cost_class: type[NkCost]
    config: dict
    building_field_name = "Liegenschaft"
    unit_field_name = "Mietobjekte"

    @classmethod
    def get_fields(cls):
        return [
            # CostConfigField("class", CostConfigFieldTypes.NKCOST_CLASS),
            CostConfigField("name", CostConfigFieldTypes.STRING),
            CostConfigField("bezeichnung", CostConfigFieldTypes.STRING),
            CostConfigField(
                "billing_group",
                CostConfigFieldTypes.STRING,
                required=False,
                verbose_name="Kostengruppe (optional)",
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

    @classmethod
    def build(cls, item_config: dict, report_input_data):
        config = {}
        cls.store_fields_in_config(report_input_data, config)
        return cls(item_config["class"], config)

    @classmethod
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        """Store field data in the config structure. Most fields are single values that are just
        stored in the dict with the field name as the key."""
        single_value_keys = []
        for field in cls.get_fields():
            if not field.is_measurement:
                single_value_keys.append(field.key)
        for field in fields:
            name = field.name.name
            if name in single_value_keys:
                config[name] = field.get_value()

    def set_name(self, name):
        self.config["name"] = name


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
            CostConfigField("Betrag", CostConfigFieldTypes.FLOAT, verbose_name="Gesamtkosten CHF"),
        ]


@dataclass
class NkPerRentalUnitCostConfig(CostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField(
                "fee_per_unit",
                CostConfigFieldTypes.FLOAT,
                verbose_name="Betrag/Monat pro Mieteinheit",
            ),
            CostConfigField(
                "fee_per_person",
                CostConfigFieldTypes.FLOAT,
                verbose_name="Betrag/Monat pro Person (Mindestbelegung)",
            ),
            CostConfigField(
                "fixed_fees",
                CostConfigFieldTypes.JSON,
                verbose_name="Ausnahmen/Mietobj. mit Fixbeträgen",
            ),
        ]

    @classmethod
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        for field in fields:
            name = field.name.name
            if name in ("fee_per_unit", "fee_per_person", "fixed_fees"):
                config[name] = field.get_value()


class NkAdminFeeCostConfig(CostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField(
                "adminfee_percentage",
                CostConfigFieldTypes.FLOAT,
                verbose_name="Verwaltungsaufwand in Prozent",
            ),
        ]


@dataclass
class NkZEVStromallmendCostConfig(CostConfig):
    building_field_headers = ["strom_bezug_zev", "strom_ruecklieferung_ew"]
    unit_field_headers = [
        "strom_ew_nieder",
        "strom_ew_hoch",
        "strom_solar",
        "chf_netz_nieder",
        "chf_netz_hoch",
    ]

    @classmethod
    def get_fields(cls):
        return (
            super().get_fields()
            + [
                CostConfigField(
                    "tarif_eigenstrom",
                    CostConfigFieldTypes.FLOAT,
                    verbose_name="Tarif Eigenstrom (CHF/kWh)",
                ),
                CostConfigField(
                    "tarif_einspeiseverguetung",
                    CostConfigFieldTypes.JSON,
                    verbose_name="Tarif Einspeisevergütung (CHF/kWh für jeden Monat)",
                ),
                CostConfigField(
                    "tarif_hkn", CostConfigFieldTypes.FLOAT, verbose_name="Tarif HKN (CHF/kWh)"
                ),
                CostConfigField(
                    "tarif_korrekturen",
                    CostConfigFieldTypes.JSON,
                    verbose_name="Tarif für Korrekturen (CHF/kWh)",
                ),
                CostConfigField(
                    "korrekturen", CostConfigFieldTypes.JSON, verbose_name="Korrekturen (optional)"
                ),
            ]
            + NkMeasurementDataMonthlyCSVFile.get_config_fields(
                cls.building_field_name, headers=cls.building_field_headers
            )
            + NkMeasurementDataEgon.get_config_fields(
                cls.unit_field_name, headers=cls.unit_field_headers
            )
        )

    @classmethod
    ## TODO: refactor (identical method in NkVEWACostConfigMonthlyEGON and similar in other classes)
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        """Store field data in the config structure. Single value fields are stored by the super
        class, here we just store the measurement substructure."""
        super().store_fields_in_config(fields, config)
        config["measurement_data"] = {
            "building": NkMeasurementDataMonthlyCSVFile.get_config(
                fields, cls.building_field_name, headers=cls.building_field_headers
            ),
            "rental_units": NkMeasurementDataEgon.get_config(
                fields, cls.unit_field_name, headers=cls.unit_field_headers
            ),
        }


@dataclass
class NkVEWACostConfig(NkTotalCostConfig):
    building_field_headers = ["Kosten"]
    unit_field_headers = ["Verbrauch"]

    @classmethod
    def get_fields(cls):
        return super().get_fields() + [
            CostConfigField(
                "vewa_category", CostConfigFieldTypes.VEWA_CATEGORY, verbose_name="VEWA Kategorie"
            ),
            CostConfigField(
                "base_cost_factor",
                CostConfigFieldTypes.FLOAT,
                verbose_name="Grundkostenanteil (z.B. 0.3 für 30%)",
            ),
            CostConfigField(
                "exclude_zero_usage_units",
                CostConfigFieldTypes.BOOL,
                required=False,
                verbose_name="Keine Grundkosten wenn kein Verbrauch",
            ),
            CostConfigField(
                "common_cost_section_weights",
                CostConfigFieldTypes.SECTION_WEIGHTS,
                required=False,
                verbose_name="Verteilschlüssel für allgemeine Kosten nach Objekttyp",
            ),
        ]


@dataclass
class NkVEWACostConfigAnnual(NkVEWACostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + NkMeasurementDataAnnual.get_config_fields("Liegenschaft")

    @classmethod
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        """Store field data in the config structure. Single value fields are stored by the super
        class, here we just store the measurement substructure."""
        super().store_fields_in_config(fields, config)
        config["measurement_data"] = {
            "building": NkMeasurementDataAnnual.get_config(
                fields, cls.building_field_name, headers=cls.building_field_headers
            )
        }


@dataclass
class NkVEWACostConfigMonthly(NkVEWACostConfig):
    @classmethod
    def get_fields(cls):
        return super().get_fields() + NkMeasurementDataMonthlyCSVFile.get_config_fields(
            cls.building_field_name, headers=cls.building_field_headers
        )

    @classmethod
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        """Store field data in the config structure. Single value fields are stored by the super
        class, here we just store the measurement substructure."""
        super().store_fields_in_config(fields, config)
        config["measurement_data"] = {
            "building": NkMeasurementDataMonthlyCSVFile.get_config(
                fields, cls.building_field_name, headers=cls.building_field_headers
            ),
        }


@dataclass
class NkVEWACostConfigAnnualEGON(NkVEWACostConfig):
    @classmethod
    def get_fields(cls):
        return (
            super().get_fields()
            + NkMeasurementDataAnnual.get_config_fields(cls.building_field_name)
            + NkMeasurementDataEgon.get_config_fields(
                cls.unit_field_name, headers=cls.unit_field_headers
            )
        )

    @classmethod
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        """Store field data in the config structure. Single value fields are stored by the super
        class, here we just store the measurement substructure."""
        super().store_fields_in_config(fields, config)
        config["measurement_data"] = {
            "building": NkMeasurementDataAnnual.get_config(
                fields, cls.building_field_name, headers=cls.building_field_headers
            ),
            "rental_units": NkMeasurementDataEgon.get_config(
                fields, cls.unit_field_name, headers=cls.unit_field_headers
            ),
        }


@dataclass
class NkVEWACostConfigMonthlyEGON(NkVEWACostConfig):
    @classmethod
    def get_fields(cls):
        return (
            super().get_fields()
            + NkMeasurementDataMonthlyCSVFile.get_config_fields(
                cls.building_field_name, headers=cls.building_field_headers
            )
            + NkMeasurementDataEgon.get_config_fields(
                cls.unit_field_name, headers=cls.unit_field_headers
            )
        )

    @classmethod
    def store_fields_in_config(cls, fields: "list[ReportInputData]", config: dict):
        """Store field data in the config structure. Single value fields are stored by the super
        class, here we just store the measurement substructure."""
        super().store_fields_in_config(fields, config)
        config["measurement_data"] = {
            "building": NkMeasurementDataMonthlyCSVFile.get_config(
                fields, cls.building_field_name, headers=cls.building_field_headers
            ),
            "rental_units": NkMeasurementDataEgon.get_config(
                fields, cls.unit_field_name, headers=cls.unit_field_headers
            ),
        }
        # Should generate (example):
        # "building": {
        #      "class": NkMeasurementDataMonthlyCSVFile,
        #      "file_key": "Messdaten:Liegenschaft",
        #      "headers": {
        #          "month": "Monat",
        #          "costs": "Fernwaerme_Warmwasser",
        #      },
        #  },
        #  "rental_units": {
        #      "class": NkMeasurementDataEgon,
        #      "file_key": "Messdaten:Mieteinheiten",
        #      "file_prefix": "egon_Waerme",
        #      "headers": {
        #          "rental_unit": "Gebäudeeinheit",
        #          "time_period": "Mieter Abrechnungsperiode",
        #          "usage": "Warmwasser Verbrauch (Kubikmeter)",
        #      },
        #  },


def get_report_item_config() -> Iterator[CostConfig | BaseSettingsConfig]:
    """Get a list of implemented cost types that should be available in the UI

    The configuration can contain default values for some fields.
    """
    # The first element is always general settings
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
            # "billing_group": "Hauswartung",
            "class": NkTotalCost,
            "config": NkTotalCostConfig,
        },
        {
            "name": "VEWA-Annual",
            "bezeichnung": "Wärme/Wasser aufgrund Gesamtkosten und Gesamtverbrauch",
            "class": NkCostVEWA,
            "config": NkVEWACostConfigAnnual,
        },
        {
            "name": "VEWA-Monthly",
            "bezeichnung": "Wärme/Wasser aufgrund Kosten pro Monat",
            "class": NkCostVEWA,
            "config": NkVEWACostConfigMonthly,
        },
        {
            "name": "VEWA-AnnualEGON",
            "bezeichnung": "Wärme/Wasser aufgrund Gesamtkosten und Verbrauch von EGON",
            "class": NkCostVEWA,
            "config": NkVEWACostConfigAnnualEGON,
        },
        {
            "name": "VEWA-MonthlyEGON",
            "bezeichnung": "Wärme/Wasser aufgrund Kosten pro Monat und Verbrauch von EGON",
            "class": NkCostVEWA,
            "config": NkVEWACostConfigMonthlyEGON,
        },
        {
            "name": "ZEV_Stromallmend",
            "bezeichnung": "ZEV-Abrechnung mit dem Stromallmend-Modell",
            "billing_group": "Stromkosten",
            "class": NkCostZEVStromallmend,
            "config": NkZEVStromallmendCostConfig,
        },
        {
            "name": "PerRentalUnit",
            "bezeichnung": "Gebühren nach Mieteinheit und Personen Mindestbelegung",
            "class": NkPerRentalUnitCost,
            "config": NkPerRentalUnitCostConfig,
        },
        {
            "name": "Verwaltungsaufwand",
            "bezeichnung": "Verwaltungsaufwand als Prozentsatz der Gesamtkosten",
            "class": NkAdminFeeCost,
            "config": NkAdminFeeCostConfig,
            "adminfee_percentage": "1.5",
        },
    ]
    for cost in cost_item_types:
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
        choices.append((cat.value, VEWA_CATEGORY_DESCRIPTIONS.get(cat, cat.name)))
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


def get_enum_value(enum_type: str, value: str) -> Enum | str | None:
    """Get the appropriate value for enum fields, or None if not found."""
    if enum_type == "enum_vewa_category":
        for cat in NkCostVEWACategories:
            if str(cat.value) == value:
                return cat
    else:
        return value
    return None


REPORT_ITEM_CATEGORY = _build_report_item_categories()
