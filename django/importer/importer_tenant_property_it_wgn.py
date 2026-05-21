"""
Tenant and Property Excel Importer Service.

This module handles the import of tenant, building, rental unit, and contract data
from Excel files with the specific column structure from the legacy system.
"""

from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import RENTAL_UNIT_TYPES, Address, Building, Contract, RentalUnit

from .services import ExcelImporter
from .utils import parse_address_string, parse_date, parse_decimal, split_street

logger = logging.getLogger(__name__)


class ImporterTenantPropertyITWGN(ExcelImporter):
    """
    Specialized importer for Tenant and Property data (Buildings, RentalUnits, Contracts).

    Handles Excel files with property and tenant information.
    """

    def _has_existing(self, row_data: dict, sheet: str | None = None) -> bool:
        """
        Check if an RentalUnit already exists based on import_id.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        unit_id = row_data.get("Id", "")
        import_id = f"legacy_{self.import_job.id}_{unit_id}"

        # Check by import_id
        if import_id:
            if RentalUnit.objects.filter(import_id=import_id).exists():
                raise ValidationError(
                    _("Mietobjekt mit Import-ID %(import_id)s existiert bereits."),
                    params={"import_id": import_id},
                )

        # Check by name and building
        unit_name = row_data.get("Nummer")
        building_name = row_data.get("Liegenschaft Bezeichnung")
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

    def _process_single_row(self, row_data: dict, sheet: str | None = None):
        """
        Process a single row and create/update Building, RentalUnit, and Contract records.

        Args:
            row_data: dictionary containing the row data from Excel

        Raises:
            ValidationError: If the row data is invalid
        """
        if sheet is not None:
            raise ValidationError(_("Sheets are not supported for this importer"))

        # Create or get Building
        building = self._create_or_update_building(row_data)

        # Create or update RentalUnit
        rental_unit = self._create_or_update_rental_unit(row_data, building)

        # Create or update Contract if tenant data exists
        if self._has_tenant_data(row_data):
            self._create_or_update_contract(row_data, rental_unit)
            logger.info(f"Successfully processed {rental_unit} with contract")
        else:
            logger.info(f"Successfully processed {rental_unit} (no contract)")

    @staticmethod
    def _has_tenant_data(row_data: dict) -> bool:
        """Check if row has tenant/contract data."""
        # Mieter Nummer 9999 is a special marker for "Leerstand" (vacancy)
        mieter_nummer = row_data.get("Mieter Nummer", "")
        if str(mieter_nummer).strip() == "9999":
            return False

        return bool(
            row_data.get("Mieter Person Person Name Vorname")
            or row_data.get("Verhaeltnis Gueltigvon")
        )

    @staticmethod
    def _create_or_update_building(row_data: dict) -> Building:
        """
        Create or update a Building record from row data.

        Args:
            row_data: dictionary containing the row data

        Returns:
            Building instance
        """
        # Use "Liegenschaft Bezeichnung" or "Liegenschaft Bezeichnungsname"
        building_name = (
            row_data.get("Liegenschaft Bezeichnung")
            or row_data.get("Liegenschaft Bezeichnungsname")
            or ""
        ).strip()
        if not building_name:
            raise ValidationError("Liegenschaft Bezeichnung ist erforderlich")

        # Try to find existing building
        try:
            building = Building.objects.get(name=building_name)
            logger.debug(f"Found existing building: {building_name}")
        except Building.DoesNotExist:
            building = Building(name=building_name)
            logger.debug(f"Creating new building: {building_name}")

        # Map fields - no separate description field in Excel
        # building.description stays as is if updating

        # Parse address fields
        street = row_data.get("Liegenschaft Strasse", "") or ""
        street_name, house_number = split_street(street)
        building.street_name = street_name or ""
        building.house_number = house_number or ""

        building.city_zipcode = row_data.get("Liegenschaft Postleitzahl", "") or ""
        building.city_name = row_data.get("Liegenschaft Ort", "") or ""
        building.country = "CH"  # Default

        # EGID (Eidgenössischer Gebäudeidentifikator)
        egid_str = row_data.get("Liegenschaft Gebaeudeideidg", "")
        if egid_str:
            try:
                building.egid = int(egid_str)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse EGID: {egid_str}")

        building.save()
        return building

    def _create_or_update_rental_unit(self, row_data: dict, building: Building) -> RentalUnit:
        """
        Create or update a RentalUnit record from row data.

        Args:
            row_data: dictionary containing the row data
            building: Associated Building instance

        Returns:
            RentalUnit instance
        """
        unit_number = str(row_data.get("Nummer", "")).strip()
        if not unit_number:
            raise ValidationError("Nummer (RentalUnit name) ist erforderlich")

        # Try to find existing rental unit
        try:
            rental_unit = RentalUnit.objects.get(name=unit_number, building=building)
            logger.debug(f"Found existing rental unit: {unit_number} in {building}")
        except RentalUnit.DoesNotExist:
            rental_unit = RentalUnit(name=unit_number, building=building)
            logger.debug(f"Creating new rental unit: {unit_number} in {building}")

        # Map fields
        rental_unit.label = row_data.get("Bezeichnung", "") or ""

        # Map rental type
        type_raw = (row_data.get("Objekttyp Bezeichnung", "") or "").strip()
        rental_unit.rental_type = self._map_rental_type(type_raw)

        rental_unit.floor = row_data.get("Etage Nummer", "") or ""

        # Numeric fields
        rental_unit.rooms = parse_decimal(row_data.get("Zimmerzahl Anzahl"))
        rental_unit.area = parse_decimal(row_data.get("Nutzflaeche"))
        rental_unit.nk = parse_decimal(row_data.get("Akonti"))

        # Parse rent - "Nettomiete" or "Brutto"
        netto = parse_decimal(row_data.get("Nettomiete"))
        brutto = parse_decimal(row_data.get("Brutto"))

        if netto:
            rental_unit.rent_netto = netto
        elif brutto and rental_unit.nk:
            # Calculate netto from brutto if we have NK
            rental_unit.rent_netto = brutto - rental_unit.nk
        elif brutto:
            rental_unit.rent_netto = brutto

        # Additional info
        position = row_data.get("Position", "")
        if position:
            rental_unit.note = position

        # Status - check for "Leerstand" indicator
        mieter_nummer = row_data.get("Mieter Nummer", "")
        if mieter_nummer == "9999":
            rental_unit.status = "Leerstand"
        else:
            rental_unit.status = "Vermietet" if self._has_tenant_data(row_data) else "Verfügbar"

        # EWID (Eidgenössischer Wohnungsidentifikator)
        ewid_str = row_data.get("Wohnung Id Eidg", "")
        if ewid_str:
            try:
                rental_unit.ewid = int(ewid_str)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse EWID: {ewid_str}")

        # Internal number
        internal_nr_str = row_data.get("Wohnung Nummer Administrativ") or row_data.get(
            "Wohnung Nummer Physisch", ""
        )
        if internal_nr_str:
            try:
                rental_unit.internal_nr = int(internal_nr_str)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse internal_nr: {internal_nr_str}")

        # Import ID
        unit_id = row_data.get("Id", "")
        if unit_id:
            rental_unit.import_id = f"legacy_{self.import_job.id}_{unit_id}"

        rental_unit.save()
        return rental_unit

    def _create_or_update_contract(self, row_data: dict, rental_unit: RentalUnit) -> Contract:
        """
        Create or update a Contract record from row data.

        Args:
            row_data: dictionary containing the row data
            rental_unit: Associated RentalUnit instance

        Returns:
            Contract instance
        """
        # Parse contract date (start)
        date_str = row_data.get("Verhaeltnis Gueltigvon", "")
        contract_date = parse_date(date_str)
        if not contract_date:
            raise ValidationError(str(_("Verhältnis Gültig-von ist erforderlich für Verträge")))

        # Parse contract end date
        date_end_str = row_data.get("Verhaeltnis Gueltigbis", "")
        contract_date_end = parse_date(date_end_str) if date_end_str else None

        # Build import_id
        mieter_nummer = row_data.get("Mieter Nummer", "")
        import_id = None
        if mieter_nummer and mieter_nummer != "9999":
            import_id = f"legacy_{self.import_job.id}_contract_{mieter_nummer}"

        # Try to find existing contract
        contract = None
        if import_id:
            try:
                contract = Contract.objects.get(import_id=import_id)
                logger.debug(f"Found existing contract by import_id: {import_id}")
            except Contract.DoesNotExist:
                pass

        # If not found, create new
        if not contract:
            contract = Contract(date=contract_date)
            if import_id:
                contract.import_id = import_id
            logger.debug("Creating new contract")
        else:
            contract.date = contract_date

        # Set end date if available
        if contract_date_end:
            contract.date_end = contract_date_end

        # Parse and create/find contractor address
        contractor = self._get_or_create_contractor_address(row_data)

        # Save contract first to enable M2M relationships
        contract.save()

        # Link contractor
        if contractor:
            contract.contractors.add(contractor)
            if not contract.main_contact:
                contract.main_contact = contractor

        # Link rental unit
        contract.rental_units.add(rental_unit)

        # Mietzinsvorbehalt (negativ)
        pauschalen = parse_decimal(row_data.get("Pauschalen"))
        if pauschalen:
            rent_reservation = -1 * pauschalen
            if contract.rent_reservation:
                contract.rent_reservation += rent_reservation
            else:
                contract.rent_reservation = rent_reservation

        # Additional fields
        mieter_bezeichnung = row_data.get("Mieter Bezeichnung", "")
        if mieter_bezeichnung:
            contract.note = mieter_bezeichnung

        # State - default to "unterzeichnet" if we have a contract
        # If end date is set and in the past, mark as "gekuendigt"
        if not contract.state:
            if contract_date_end:
                from datetime import date as date_class

                if contract_date_end < date_class.today():
                    contract.state = "gekuendigt"
                else:
                    contract.state = "unterzeichnet"
            else:
                contract.state = "unterzeichnet"

        contract.save()
        return contract

    def _get_or_create_contractor_address(self, row_data: dict) -> Address | None:
        """
        Get or create an Address for the contractor from row data.

        Args:
            row_data: dictionary containing the row data

        Returns:
            Address instance or None
        """
        # Parse name from "Mieter Person Person Name Vorname"
        name_str = (row_data.get("Mieter Person Person Name Vorname", "") or "").strip()
        if not name_str:
            return None

        # Try to split into first and last name
        name_parts = name_str.split()
        if len(name_parts) >= 2:
            last_name = name_parts[0]
            first_name = " ".join(name_parts[1:])
        else:
            first_name = ""
            last_name = name_str

        # Parse address info from "Mieter Person Person Adresse"
        address_str = (row_data.get("Mieter Person Person Adresse", "") or "").strip()

        # Build import_id for address
        person_id = row_data.get("Mieter Person Person Id", "")
        import_id = None
        if person_id:
            import_id = f"legacy_{self.import_job.id}_contractor_{person_id}"

        # Try to find existing address
        if import_id:
            try:
                address = Address.objects.get(import_id=import_id)
                logger.debug(f"Found existing contractor address by import_id: {import_id}")
                return address
            except Address.DoesNotExist:
                pass

        # Try to find by name
        if first_name and last_name:
            try:
                address = Address.objects.get(first_name=first_name, name=last_name)
                logger.debug(
                    f"Found existing contractor address by name: {first_name} {last_name}"
                )
                # Update import_id if found
                if import_id and not address.import_id:
                    address.import_id = import_id
                    address.save()
                return address
            except Address.DoesNotExist:
                pass
            except Address.MultipleObjectsReturned:
                logger.warning(f"Multiple addresses found for: {first_name} {last_name}")

        # Create new address
        address = Address()
        address.first_name = first_name
        address.name = last_name

        if import_id:
            address.import_id = import_id

        # Parse address string if available
        if address_str:
            # Try to extract street, zip, city from address string
            # Format might be: "Strasse Nr, PLZ Ort" or similar
            address_parts = parse_address_string(address_str)
            if address_parts:
                address.street_name = address_parts.get("street_name", "")
                address.house_number = address_parts.get("house_number", "")
                address.city_zipcode = address_parts.get("zipcode", "")
                address.city_name = address_parts.get("city", "")

        address.country = "CH"  # Default
        address.save()

        logger.debug(f"Created new contractor address: {address}")
        return address

    @staticmethod
    def _map_rental_type(type_raw: str) -> str:
        """
        Map rental type from Excel to RentalUnit model choices.

        Args:
            type_raw: Raw rental type string from Excel

        Returns:
            Mapped rental type value
        """
        if not type_raw:
            return "Wohnung"  # Default

        type_raw = type_raw.strip()

        # Create a mapping dict from RENTAL_UNIT_TYPES with common aliases
        type_mapping = {choice[0]: choice[0] for choice in RENTAL_UNIT_TYPES}

        # Add common aliases
        aliases = {
            "Hobbyraum": "Hobby",
            "Zimmer": "Jokerzimmer",
            "Abstellplatz": "Parkplatz",
        }

        # First check if the type exists directly in RENTAL_UNIT_TYPES
        if type_raw in type_mapping:
            return type_raw

        # Then check aliases
        if type_raw in aliases:
            return aliases[type_raw]

        # Default fallback
        return "Wohnung"
