import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from geno.models import Building, RentalUnit

if TYPE_CHECKING:
    from report.nk.contract import NkContract
    from report.nk.generator import NkReportGenerator
from report.nk.section import NkSection, get_section_by_id


class NkVirtualRentalUnitId:
    COMMON: int = -1  # Common costs (e.g., Allgemeinstrom)
    NK_FLAT: int = -2  # "Pauschale NK"
    ELECTRICITY_FLAT: int = -3  # "Pauschale Strom"


@dataclass
class NkRentalUnit:
    id: int
    name: str
    label: str | None = None
    section: NkSection | None = None
    building: Building | None = None
    area: float = 0.0
    volume: float = 0.0
    min_occupancy: float = 0
    rooms: float = 0
    custom_weights: dict[str, float] = field(default_factory=dict)
    akonto: float = 0.0
    nk_pauschal: float = 0.0
    strom_pauschal: float = 0.0
    rent_net: float = 0.0
    contract_ids: "list[NkContract] | None" = None
    is_allgemein: bool = False
    is_virtual: bool = False
    assigned_contract_per_month: "dict[int, NkContract] | None" = None
    virtual_contract_id: int | None = None

    @classmethod
    def from_rental_unit(cls, unit: RentalUnit, nkg: "NkReportGenerator"):
        label = cls.get_label(unit)
        section = cls.map_unit_to_section(unit)
        if not section:
            raise ValueError("Keine Bereichs-Zuordnung")
        is_allgemein = cls.is_rental_unit_allgemein(unit)
        if is_allgemein:
            area = 0.0
            volume = 0.0
            min_occupancy = 0
            rooms = 0
        else:
            try:
                area = float(unit.area)
                if unit.volume:
                    volume = float(unit.volume)
                else:
                    nkg.log.append(f"WARNING: Unit {label} has no volume.")
                    nkg.add_warning("Kein Volumen definiert", label)
                    volume = 0
                min_occupancy = float(unit.min_occupancy) if unit.min_occupancy else 0
                rooms = float(unit.rooms) if unit.rooms else 0
            except TypeError as e:
                nkg.log.append(unit)
                raise TypeError(
                    "ERROR: %s for %s (area=%s, volume=%s, min_occupancy=%s, rooms=%s)"
                    % (e, unit.name, unit.area, unit.volume, unit.min_occupancy, unit.rooms)
                ) from None
        obj = cls(
            id=unit.id,
            name=unit.name,
            label=label,
            section=section,
            building=unit.building,
            area=area,
            volume=volume,
            min_occupancy=min_occupancy,
            rooms=rooms,
            is_allgemein=cls.is_rental_unit_allgemein(unit),
            akonto=nkg.num_months * float(unit.nk) if unit.nk else 0,
            nk_pauschal=nkg.num_months * float(unit.nk_flat) if unit.nk_flat else 0,
            strom_pauschal=(
                nkg.num_months * float(unit.nk_electricity) if unit.nk_electricity else 0
            ),
            rent_net=float(unit.rent_netto),
            virtual_contract_id=-1 * unit.virtual_contract.id if unit.virtual_contract else None,
        )
        obj.contract_ids = []
        obj.load_custom_weights(unit)
        return obj

    @classmethod
    def map_unit_to_section(cls, ru: RentalUnit):
        section = None
        # Default is mapping by rental type
        if ru.rental_type in ("Wohnung", "Grosswohnung", "Zimmer", "Selbstausbau"):
            section = get_section_by_id("wohnen")
        elif ru.rental_type in ("Gewerbe", "Hobby"):
            section = get_section_by_id("gewerbe")
        elif ru.rental_type in ("Lager",):
            section = get_section_by_id("lager")

        # Handle special cases by label, TODO: Get this from configuration
        if ru.label in ("Dachküche",):
            section = get_section_by_id("wohnen")
        elif ru.label in (
            "Teeküche",
            "Lückenraum Holliger rechts",
            "Lückenraum Holliger links",
            "Quartierraum Holliger",
        ):
            section = get_section_by_id("gewerbe")
        elif ru.label in ("Lagerraum", "Lagerabteil"):
            section = get_section_by_id("lager")

        return section

    @classmethod
    def is_rental_unit_allgemein(cls, ru: RentalUnit):
        return ru.rental_type in ("Parkplatz", "Gemeinschaftsräume/Diverses")

    @classmethod
    def get_label(cls, ru: RentalUnit):
        if ru.label:
            return f"{ru.label} {ru.name}"
        else:
            return f"{ru.rental_type} {ru.name}"

    def add_contract_id(self, contract_id):
        if self.contract_ids is None:
            self.contract_ids = []
        if contract_id not in self.contract_ids:
            self.contract_ids.append(contract_id)

    def get_contract_ids(self):
        return self.contract_ids or []

    def assign_month_to_contract(
        self, month_index: int, contract: "NkContract", date: dict[str, datetime.date]
    ):
        if self.assigned_contract_per_month is None:
            self.assigned_contract_per_month = {}
        self.assigned_contract_per_month[month_index] = contract
        contract.assign_rental_unit_month(self, date)

    def get_assigned_contract_for_month(self, month_index: int):
        if self.assigned_contract_per_month is None:
            return None
        return self.assigned_contract_per_month.get(month_index, None)

    def load_custom_weights(self, ru: RentalUnit):
        for weight in ru.rentalunitweight_set.all():
            self.custom_weights[f"ru_weight_type_{weight.name.id}"] = float(weight.weight)

    def get_weight(self, key):
        if key.startswith("ru_weight_type_"):
            return self.custom_weights.get(key, 0.0)
        return getattr(self, key, 0.0)

    def get_context(self):
        return {
            "id": self.id,
            "rental_nr": self.name,
            "rental_unit": self.label,
            "section": self.section,
            "area": self.area,
            "volume": self.volume,
            "building": self.building.full_name,
            # "min_occupancy": self.min_occupancy,
            # "rooms": self.rooms,
        }
