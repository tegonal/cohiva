from __future__ import annotations

import datetime
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import Address, Building, Contract, Member, Share

from .services import ExcelImporter
from .utils import (
    get_or_create_share_type,
    parse_bool,
    parse_date,
    parse_decimal,
    parse_int,
)

logger = logging.getLogger(__name__)


class ImporterPropertySharesVFN(ExcelImporter):
    """Specialized importer for property Shares that are linked to a contract/rental unit."""

    def _has_existing(self, row_data: dict, sheet: str | None = None) -> bool:
        """
        Check if a Share already exists based on import_id

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        import_info = self._build_import_info(row_data)
        if (
            import_info
            and import_info["import_id"]
            and Share.objects.filter(import_id=import_info["import_id"]).exists()
        ):
            raise ValidationError(
                _("Share with Import-ID {import_id} already exists.").format(
                    import_id=import_info["import_id"]
                ),
            )
        return False

    def _process_single_row(self, row_data: dict, sheet: str | None = None):
        """
        Process a single row and create/update Share records.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If the row data is invalid
        """
        if sheet is not None:
            raise ValidationError(_("Sheets are not supported for this importer"))

        import_info = self._build_import_info(row_data)
        self._create_or_update_share(row_data, import_info["import_id"], import_info["address"])
        logger.info(f"Successfully processed {import_info['import_id']}")

    @staticmethod
    def _build_import_info(row_data: dict) -> dict[str, str | Address]:
        typ = row_data.get("Typ")
        if not typ:
            raise ValidationError(_("Typ is required"))

        date_start = row_data.get("Datum Beginn") or ""
        quantity = parse_int(row_data.get("Anzahl"))
        amount = parse_decimal(row_data.get("Betrag pro Stück"))

        # There are three options to reference the Address that should be linked to the share:
        #  - Address-ID: The id of the Address object in the database
        #  - Member-ID: The id of a Member object in the databank that links to the Address
        #  - Person: An arbitrary ID from a previous import of the person (Address with import id 'vfn_{person_import_id}')
        address_id = row_data.get("Adress-ID")
        member_id = row_data.get("Mitglied-ID")
        person_import_id = row_data.get("Person")
        if address_id:
            import_id = f"vfn_{typ}_a{address_id}_{date_start}_{quantity}_{amount}"
            address = Address.objects.filter(id=address_id).first()
            if not address:
                raise ValidationError(
                    _("Address with ID {address_id} not found").format(address_id=f"{address_id}")
                )
        elif member_id:
            import_id = f"vfn_{typ}_m{member_id}_{date_start}_{quantity}_{amount}"
            member = Member.objects.filter(id=member_id).first()
            if not member:
                raise ValidationError(
                    _("Member with ID {member_id} not found").format(member_id=f"{member_id}")
                )
            address = member.name
            if not address:
                raise ValidationError(
                    _("Address for member with ID {member_id} not found").format(
                        member_id=f"{member_id}"
                    )
                )
        elif person_import_id:
            import_id = f"vfn_{typ}_{person_import_id}_{date_start}_{quantity}_{amount}"
            address = Address.objects.filter(import_id=f"vfn_{person_import_id}").first()
            if not address:
                raise ValidationError(
                    _("Address with ImportID {import_id} not found").format(
                        import_id=f"vfn_{person_import_id}"
                    )
                )
        else:
            raise ValidationError(_("Person, Mitglied-ID, or Adress-ID is required"))
        return {"import_id": import_id, "address": address}

    @staticmethod
    def _create_or_update_share(row_data: dict, import_id: str, address: Address):
        """Create or update a Share record linked to the address."""
        share_type = get_or_create_share_type(row_data.get("Typ"))

        share = None
        if import_id:
            try:
                share = Share.objects.get(import_id=import_id)
            except Share.DoesNotExist:
                pass

        if not share:
            share = Share(name=address, share_type=share_type)

        amount = parse_decimal(row_data.get("Betrag pro Stück"))
        quantity_raw = row_data.get("Anzahl")
        quantity = parse_int(quantity_raw)
        share.quantity = quantity if quantity is not None else 1

        share.value = amount

        state_raw = str(row_data.get("Status") or "").strip().lower()
        if state_raw in ("bezahlt", "paid", "einbezahlt", "eingezahlt", "zurückbezahlt"):
            share.state = "bezahlt"
        else:
            share.state = "gefordert"

        share_date = parse_date(row_data.get("Datum Beginn"))
        if share_date:
            share.date = share_date
        elif not share.pk:
            # Fallback: use today
            share.date = datetime.date.today()

        share.date_end = parse_date(row_data.get("Datum Ende"))
        share.is_pension_fund = parse_bool(row_data.get("WEF-Guthaben (BVG/3. Säule)")) or False

        linked_contract_id = row_data.get("Fixe Zuteilung zu Vertrag")
        if linked_contract_id:
            share.attached_to_contract = Contract.objects.filter(
                import_id=f"vfn_{linked_contract_id}"
            ).first()

        linked_building_name = row_data.get("Zuordnung zu Liegenschaft")
        if linked_building_name:
            share.attached_to_building = Building.objects.filter(name=linked_building_name).first()

        share.note = row_data.get("Zusatzinfo") or ""

        if import_id:
            share.import_id = import_id

        share.save()
