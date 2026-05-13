from __future__ import annotations

import datetime
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import Address, Building, Contract, Share

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
                _("Beteiligung mit Import-ID {import_id} existiert bereits.").format(
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
        person_id = row_data.get("Person")
        if not person_id:
            raise ValidationError(_("Person is erforderlich"))

        typ = row_data.get("Typ")
        if not typ:
            raise ValidationError(_("Typ ist erforderlich"))

        date_start = row_data.get("Datum Beginn") or ""
        quantity = parse_int(row_data.get("Anzahl"))
        amount = parse_decimal(row_data.get("Betrag pro Stück"))

        import_id = f"vfn_{typ}_{person_id}_{date_start}_{quantity}_{amount}"
        address = Address.objects.filter(import_id=f"vfn_{person_id}").first()
        if not address:
            raise ValidationError(
                _("Adresse mit ImportID {import_id} nicht gefunden").format(
                    import_id=f"vfn_{person_id}"
                )
            )
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
