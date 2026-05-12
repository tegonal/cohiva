from __future__ import annotations

import datetime
import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import Address, Contract, Share

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

    def _process_single_row(self, row_data: dict, sheet: str | None = None):
        """
        Process a single row and create/update Share records.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If the row data is invalid
        """
        if not row_data.get("Person 1") and not row_data.get("Person 2"):
            raise ValidationError(_("Mindestens eine Peronen-ID erforderlich"))

        if sheet is not None:
            raise ValidationError(_("Sheets are not supported for this importer"))

        typ = row_data.get("Typ")
        if not typ:
            raise ValidationError(_("Typ ist erforderlich"))

        p1 = row_data.get("Person 1", "")
        p2 = row_data.get("Person 2", "")
        if p1 and p2:
            # Split share in two equal shares
            amount = parse_decimal(row_data.get("Betrag pro Stück")) / 2
        else:
            amount = parse_decimal(row_data.get("Betrag pro Stück"))

        date_start = row_data.get("Datum Beginn", "").replace(".", "")
        ru = row_data.get("Zuordnung zu Liegenschaft (Mietobjekt)", "").replace(" ", "_")
        if p1:
            import_id1 = f"vfn_{typ}_{p1}_{date_start}_{amount}_{ru}"
            address = Address.objects.filter(import_id=f"vfn_{p1}").first()
            self._create_or_update_share(row_data, import_id1, address, amount)
            logger.info(f"Successfully processed {import_id1}")
        if p2:
            import_id2 = f"vfn_{typ}_{p2}_{date_start}_{amount}_{ru}"
            address = Address.objects.filter(import_id=f"vfn_{p2}").first()
            self._create_or_update_share(row_data, import_id2, address, amount)
            logger.info(f"Successfully processed {import_id2}")

    @staticmethod
    def _create_or_update_share(row_data: dict, import_id: str, address: Address, amount: Decimal):
        """Create or update a Share record linked to the address."""
        share_type = get_or_create_share_type(row_data.get("Typ"))

        share = None
        if import_id:
            try:
                share = Share.objects.get(import_id=import_id)
            except share.DoesNotExist:
                pass

        if not share:
            share = Share(name=address, share_type=share_type)

        quantity_raw = row_data.get("Anzahl")
        quantity = parse_int(quantity_raw)
        share.quantity = quantity if quantity is not None else 1

        share.value = amount

        state_raw = str(row_data.get("Genossenschaftsanteile Status") or "").strip().lower()
        if state_raw in ("bezahlt", "paid", "einbezahlt", "zurückbezahlt"):
            share.state = "bezahlt"
        else:
            share.state = "gefordert"

        share_date = parse_date(row_data.get("Datum Begin"))
        if share_date:
            share.date = share_date
        elif not share.pk:
            # Fallback: use today
            share.date = datetime.date.today()

        share.date_end = parse_date(row_data.get("Datum Ende"))
        share.is_pension_fund = parse_bool(row_data.get("WEF-Guthaben (BVG/3. Säule)"))

        linked_contract_id = row_data.get("Fixe zuteilung zu Vertrag")
        if linked_contract_id:
            share.attached_to_contract = Contract.objects.filter(
                import_id=f"vfn_{linked_contract_id}"
            ).first()

        share.notes = row_data.get("Zusatzinfo") or ""

        if import_id:
            share.import_id = import_id

        share.save()
