"""
Building and RentalUnit Excel Importer for VFN data.

This module handles the import of building and rental unit data from the
VFN Excel file: Liegenschaften Mietobjekte Cohiva.xlsx

Expected columns (one row per rental unit):
  Liegenschaft ID, Liegenschaft Name, Strasse, PLZ, Ort, EGID,
  Einheit ID, Einheit Nummer, Einheit Bezeichnung, Typ,
  Etage, Zimmer, Fläche, NK Akonto, Nettomiete, EWID
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import RENTAL_UNIT_TYPES, Building, RentalUnit

from .services import ExcelImporter

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

    def _has_existing(self, row_data: dict) -> bool:
        """
        Check if a RentalUnit already exists based on import_id or name+building.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        unit_id = row_data.get("Einheit ID")
        import_id = f"vfn_{self.import_job.id}_{unit_id}" if unit_id else None

        if import_id and RentalUnit.objects.filter(import_id=import_id).exists():
            raise ValidationError(
                _("Mietobjekt mit Import-ID %(import_id)s existiert bereits."),
                params={"import_id": import_id},
            )

        unit_name = str(row_data.get("Einheit Nummer") or "").strip()
        building_name = str(row_data.get("Liegenschaft Name") or "").strip()
        if (
            unit_name
            and building_name
            and RentalUnit.objects.filter(name=unit_name, building__name=building_name).exists()
        ):
            raise ValidationError(
                _("Mietobjekt %(unit_name)s in Liegenschaft %(building_name)s existiert bereits."),
                params={"unit_name": unit_name, "building_name": building_name},
            )

        return False

    def _process_single_row(self, row_data: dict):
        """
        Process a single row and create/update Building and RentalUnit records.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If the row data is invalid
        """
        building = self._create_or_update_building(row_data)
        rental_unit = self._create_or_update_rental_unit(row_data, building)
        logger.info(f"Successfully processed {rental_unit} in {building}")

    def _create_or_update_building(self, row_data: dict) -> Building:
        """Create or update a Building from row data."""
        building_name = str(row_data.get("Liegenschaft Name") or "").strip()
        if not building_name:
            raise ValidationError(_("Liegenschaft Name ist erforderlich"))

        try:
            building = Building.objects.get(name=building_name)
            logger.debug(f"Found existing building: {building_name}")
        except Building.DoesNotExist:
            building = Building(name=building_name)
            logger.debug(f"Creating new building: {building_name}")

        street = str(row_data.get("Strasse") or "").strip()
        street_name, house_number = self._split_street(street)
        building.street_name = street_name or ""
        building.house_number = house_number or ""

        plz = str(row_data.get("PLZ") or "").strip()
        # PLZ may arrive as integer from Excel
        building.city_zipcode = plz
        building.city_name = str(row_data.get("Ort") or "").strip()
        building.country = "CH"

        egid_raw = row_data.get("EGID")
        if egid_raw:
            try:
                building.egid = int(egid_raw)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse EGID: {egid_raw}")

        building.save()
        return building

    def _create_or_update_rental_unit(self, row_data: dict, building: Building) -> RentalUnit:
        """Create or update a RentalUnit from row data."""
        unit_number = str(row_data.get("Einheit Nummer") or "").strip()
        if not unit_number:
            raise ValidationError(_("Einheit Nummer ist erforderlich"))

        try:
            rental_unit = RentalUnit.objects.get(name=unit_number, building=building)
            logger.debug(f"Found existing rental unit: {unit_number}")
        except RentalUnit.DoesNotExist:
            rental_unit = RentalUnit(name=unit_number, building=building)
            logger.debug(f"Creating new rental unit: {unit_number}")

        rental_unit.label = str(row_data.get("Einheit Bezeichnung") or "").strip()

        type_raw = str(row_data.get("Typ") or "").strip()
        rental_unit.rental_type = self._map_rental_type(type_raw)

        rental_unit.floor = str(row_data.get("Etage") or "").strip()
        rental_unit.rooms = self._parse_decimal(row_data.get("Zimmer"))
        rental_unit.area = self._parse_decimal(row_data.get("Fläche"))
        rental_unit.nk = self._parse_decimal(row_data.get("NK Akonto"))

        netto = self._parse_decimal(row_data.get("Nettomiete"))
        if netto:
            rental_unit.rent_netto = netto

        ewid_raw = row_data.get("EWID")
        if ewid_raw:
            try:
                rental_unit.ewid = int(ewid_raw)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse EWID: {ewid_raw}")

        unit_id = row_data.get("Einheit ID")
        if unit_id:
            rental_unit.import_id = f"vfn_{self.import_job.id}_{unit_id}"

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

    def _split_street(self, street: str) -> tuple:
        if not street:
            return ("", "")
        street = street.strip()
        parts = street.rsplit(" ", 1)
        if len(parts) == 2 and any(c.isdigit() for c in parts[1]):
            return (parts[0].strip(), parts[1].strip())
        return (street, "")

    def _parse_decimal(self, value) -> Decimal | None:
        if value is None or value == "":
            return None
        try:
            if isinstance(value, (Decimal, int, float)):
                return Decimal(str(value))
            if isinstance(value, str):
                value = value.strip().replace("'", "").replace(",", ".")
                if not value:
                    return None
                return Decimal(value)
        except (InvalidOperation, ValueError):
            logger.warning(f"Could not parse decimal: {value}")
        return None

    def _parse_date(self, date_val) -> datetime.date | None:
        if not date_val:
            return None
        if isinstance(date_val, datetime):
            return date_val.date()
        if hasattr(date_val, "date"):
            return date_val.date()
        if isinstance(date_val, str):
            date_val = date_val.strip()
            if not date_val:
                return None
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
                try:
                    return datetime.strptime(date_val, fmt).date()
                except ValueError:
                    continue
        logger.warning(f"Could not parse date: {date_val}")
        return None
