"""
Building and RentalUnit Excel Importer for VFN data.

This module handles the import of building and rental unit data from the
VFN Excel file: Liegenschaften Mietobjekte Cohiva.xlsx

Expected columns (one row per rental unit):
  Liegenschaft ID, Liegenschaft Name, Strasse, PLZ, Ort, EGID,
  Einheit ID, Einheit Nummer, Einheit Bezeichnung, Typ,
  Etage, Zimmer, Fläche, NK Akonto, Nettomiete, EWID
"""

import datetime
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from cohiva.utils.countries import normalize_country_code
from geno.models import RENTAL_UNIT_TYPES, Address, Building, Contract, RentalUnit

from .services import ExcelImporter
from .utils import parse_decimal, parse_int

logger = logging.getLogger(__name__)


class ImporterTenantPropertyVFN(ExcelImporter):
    """
    Specialized importer for Building and RentalUnit data from VFN files.

    Handles Excel files (Liegenschaften Mietobjekte Cohiva.xlsx) with
    building and rental unit information. Uses ID fields to link data.
    """

    RENTAL_TYPE_ALIASES = {
        "Hobbyraum": "Hobby",
        "Abstellplatz": "Parkplatz",
        "Zimmer": "Jokerzimmer",
    }

    def _has_existing(self, row_data: dict, sheet: str | None = None) -> bool:
        """
        Check if a RentalUnit already exists based on import_id or name+building.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        if sheet == "Liegenschaften":
            return self._has_existing_building(row_data)
        elif sheet == "Mietobjekte":
            building = self._get_building_from_row_data(row_data)
            return self._has_existing_rental_unit(row_data, building)
        elif sheet == "Mieterspiegel":
            # Ignore this sheet
            # rental_unit = self._get_rental_unit_from_row_data(row_data)
            return False
        return False

    @staticmethod
    def _has_existing_building(row_data: dict) -> bool:
        building_name = str(row_data.get("Name der Liegenschaft") or "").strip()
        if not building_name:
            raise ValidationError(_("Name der Liegenschaft ist erforderlich"))

        if Building.objects.filter(name=building_name).exists():
            raise ValidationError(
                _("Liegenschaft mit Name %(building_name)s existiert bereits."),
                params={"building_name": building_name},
            )
        return False

    @staticmethod
    def _has_existing_rental_unit(row_data: dict, building: Building) -> bool:
        unit_id = row_data.get("Import-ID")
        import_id = f"vfn_{unit_id}" if unit_id else None

        if import_id and RentalUnit.objects.filter(import_id=import_id).exists():
            raise ValidationError(
                _("Mietobjekt mit Import-ID %(import_id)s existiert bereits."),
                params={"import_id": import_id},
            )

        unit_name = str(row_data.get("Einheit Nummer") or "").strip()
        if (
            unit_name
            and building
            and RentalUnit.objects.filter(name=unit_name, building=building).exists()
        ):
            raise ValidationError(
                _("Mietobjekt %(unit_name)s in Liegenschaft %(building_name)s existiert bereits."),
                params={"unit_name": unit_name, "building_name": building.name},
            )

        return False

    def _process_single_row(self, row_data: dict, sheet: str | None = None):
        """
        Process a single row and create/update Building and RentalUnit records.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If the row data is invalid
        """
        if sheet == "Liegenschaften":
            building = self._create_or_update_building(row_data)
            logger.info(f"Successfully processed building {building}")
        elif sheet == "Mietobjekte":
            building = self._get_building_from_row_data(row_data)
            rental_unit = self._create_or_update_rental_unit(row_data, building)
            contract = self._create_or_update_contract(row_data, rental_unit)
            if contract:
                logger.info(f"Successfully processed {rental_unit} and {contract} in {building}")
            else:
                logger.info(f"Successfully processed {rental_unit} in {building}")
        elif sheet == "Mieterspiegel":
            ## Ignore this sheet
            return
            # rental_unit = self._get_rental_unit_from_row_data(row_data)
            # self._update_tenants(row_data, rental_unit)
            # logger.info(f"Successfully updated tenants of {rental_unit} in {building}")
        else:
            raise ValidationError(_("Unbekannte Tabelle: {sheet}"))

    @staticmethod
    def _create_or_update_building(row_data: dict) -> Building:
        """Create or update a Building from row data."""
        building_name = str(row_data.get("Name der Liegenschaft") or "").strip()
        if not building_name:
            raise ValidationError(_("Name der Liegenschaft ist erforderlich"))

        try:
            building = Building.objects.get(name=building_name)
            logger.debug(f"Found existing building: {building_name}")
        except Building.DoesNotExist:
            building = Building(name=building_name)
            logger.debug(f"Creating new building: {building_name}")

        building.description = str(row_data.get("Beschreibung") or "").strip()
        building.street_name = str(row_data.get("Strasse") or "").strip()
        building.house_number = str(row_data.get("Hausnummer") or "").strip()
        building.city_zipcode = str(row_data.get("PLZ") or "").strip()
        building.city_name = str(row_data.get("Ort") or "").strip()
        building.country = normalize_country_code(str(row_data.get("Land") or "CH").strip())
        building.value_insurance = parse_decimal(row_data.get("Gebäudeversicherungswert (Fr.)"))
        building.value_build = parse_decimal(row_data.get("Anlagekosten (Fr.)"))
        building.save()
        return building

    def _create_or_update_rental_unit(self, row_data: dict, building: Building) -> RentalUnit:
        """Create or update a RentalUnit from row data."""
        unit_number = str(row_data.get("Nr.") or "").strip()
        if not unit_number:
            raise ValidationError(_("Nr. ist erforderlich"))

        try:
            rental_unit = RentalUnit.objects.get(name=unit_number, building=building)
            logger.debug(f"Found existing rental unit: {unit_number}")
        except RentalUnit.DoesNotExist:
            rental_unit = RentalUnit(name=unit_number, building=building)
            logger.debug(f"Creating new rental unit: {unit_number}")

        type_raw = str(row_data.get("Typ") or "").strip()
        rental_unit.rental_type = self._map_rental_type(type_raw)
        if rental_unit.rental_type != type_raw:
            # Store the original type in label_short if it differs from the mapped type
            rental_unit.label_short = type_raw

        rental_unit.label = str(row_data.get("Bezeichnung") or "").strip()
        rental_unit.floor = str(row_data.get("Stockwerk") or "").strip()
        rental_unit.rooms = parse_decimal(row_data.get("Anzahl Zimmer"))
        rental_unit.min_occupancy = parse_decimal(row_data.get("Mindestbelegung"))
        rental_unit.area = parse_decimal(row_data.get("Fläche (m²)"))
        rental_unit.area_balcony = parse_decimal(row_data.get("Balkonfläche (m²)"))
        rental_unit.area_add = parse_decimal(row_data.get("Zusatzfläche (m²)"))
        rental_unit.height = str(row_data.get("Raumhöhe (m)") or "").strip()
        rental_unit.volume = parse_decimal(row_data.get("Volumen (m³)"))

        rental_unit.payment_period = parse_int(row_data.get("Zahlungsperiodizität"))
        rental_unit.nk = parse_decimal(row_data.get("Nebenkosten akonto (CHF/Mt.)"))
        rental_unit.nk_flat = parse_decimal(row_data.get("Nebenkosten pauschal (CHF/Mt.)"))
        rental_unit.nk_electricity = parse_decimal(row_data.get("Strompauschale (CHF/Mt.)"))

        rental_unit.rent_netto = parse_decimal(row_data.get("Nettomiete (CHF/Mt.)"))
        rental_unit.depot = parse_decimal(row_data.get("Mietzinsdepot (CHF)"))
        rental_unit.share = parse_decimal(row_data.get("Anteilskapital (CHF)"))

        rental_unit.note = str(row_data.get("Zusatzinfo") or "").strip()

        ewid_raw = row_data.get("EWID")
        if ewid_raw:
            try:
                rental_unit.ewid = int(ewid_raw)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse EWID: {ewid_raw}")

        unit_id = row_data.get("Import-ID")
        if unit_id:
            rental_unit.import_id = f"vfn_{unit_id}"

        rental_unit.save()
        return rental_unit

    def _map_rental_type(self, type_raw: str) -> str:
        if not type_raw:
            return "Wohnung"
        type_raw = type_raw.strip()
        if type_raw in self.RENTAL_TYPE_ALIASES:
            return self.RENTAL_TYPE_ALIASES[type_raw]
        valid_types = {choice[0] for choice in RENTAL_UNIT_TYPES}
        if type_raw in valid_types:
            return type_raw
        return "Wohnung"

    @staticmethod
    def _create_or_update_contract(row_data, rental_unit: RentalUnit):
        tenants = []
        for column in ["Import-ID 1 Mieter*in (Person)", "Import-ID 2 Mieter*in (Person)"]:
            tenant_id = str(row_data.get(column)).strip()
            if tenant_id:
                tenant = Address.objects.filter(import_id=f"vfn_{tenant_id}").first()
                if tenant:
                    tenants.append(tenant)
                    logger.debug(f"Found existing tenant by import_id: vfn_{tenant_id}")
                else:
                    raise ValidationError(f"Could not find tenant by import_id: vfn_{tenant_id}")
        if not tenants:
            return None

        unit_id = row_data.get("Import-ID")
        contract = Contract.objects.filter(import_id=f"vfn_{unit_id}").first() if unit_id else None
        if contract:
            logger.debug(f"Found existing contract by import_id: vfn_{unit_id}")
        else:
            # TODO?: Update state and date later with data from Mieterspiegel sheet?
            contract = Contract(
                import_id=f"vfn_{unit_id}", state="unterzeichnet", date=datetime.date.today()
            )
        contract.contractors.set(tenants)
        contract.rental_units.set([rental_unit])
        contract.save()
        return contract

    @staticmethod
    def _get_building_from_row_data(row_data: dict) -> Building:
        building_name = str(row_data.get("Liegenschaft") or "").strip()
        if not building_name:
            raise ValidationError(_("Liegenschaft ist erforderlich"))
        try:
            return Building.objects.get(name=building_name)
        except Building.DoesNotExist:
            raise ValidationError(_("Liegenschaft existiert nicht"))
