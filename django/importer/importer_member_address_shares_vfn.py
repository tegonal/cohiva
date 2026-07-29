from __future__ import annotations

import datetime
import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from cohiva.utils.countries import get_default_country_code, normalize_country_code
from geno.models import Address, Member, Share

from .services import ExcelImporter
from .utils import (
    clean_phone_number,
    get_field_by_prefix,
    get_or_create_bank_account,
    get_or_create_share_type,
    parse_bool,
    parse_date,
    parse_decimal,
    parse_int,
)

logger = logging.getLogger(__name__)


class ImporterMemberAddressSharesVFN(ExcelImporter):
    """Specialized importer for Member, Address, and Share data from VFN files."""

    TITLE_MAPPING = {
        "Herr": "Herr",
        "Frau": "Frau",
        "Familie": "Paar",
        "Paar": "Paar",
        "Firma": "Org",
        "Organisation": "Org",
        "Divers": "Divers",
    }

    DEFAULT_SHARE_TYPE_NAME = "Anteilschein"

    def _has_existing(self, row_data: dict, sheet: str | None = None) -> bool:
        """
        Check if an Address already exists based on import_id or email.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        person_id = row_data.get("ImportID")
        import_id = f"vfn_{person_id}" if person_id else None

        if import_id and Address.objects.filter(import_id=import_id).exists():
            raise ValidationError(
                _("Adresse mit ImportID %(import_id)s existiert bereits."),
                params={"import_id": import_id},
            )

        email = self._get_emails(row_data)
        if email and Address.objects.filter(email=email[0]).exists():
            raise ValidationError(
                _("Adresse mit E-Mail %(email)s existiert bereits."),
                params={"email": email[0]},
            )

        return False

    def _process_single_row(self, row_data: dict, sheet: str | None = None):
        """
        Process a single row and create/update Address, Member, and Share records.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If the row data is invalid
        """
        if (
            not row_data.get("Nachname")
            and not row_data.get("Vorname")
            and not row_data.get("Organisation")
        ):
            raise ValidationError(
                _("Mindestens Vor- oder Nachname oder Organisation erforderlich")
            )

        if sheet is not None:
            raise ValidationError(_("Sheets are not supported for this importer"))

        address = self._create_or_update_address(row_data)

        if row_data.get("Eintritt [Mitglied]"):
            self._create_or_update_member(row_data, address)

        if row_data.get("Anzahl [Beteiligungen]") or row_data.get(
            "Betrag pro Stück [Beteiligungen]"
        ):
            self._create_or_update_share(row_data, address)

        logger.info(f"Successfully processed {address}")

    def _create_or_update_address(self, row_data: dict) -> Address:
        person_id = row_data.get("ImportID")
        import_id = f"vfn_{person_id}" if person_id else None

        address = None
        if import_id:
            try:
                address = Address.objects.get(import_id=import_id)
            except Address.DoesNotExist:
                pass

        if not address:
            email = self._get_emails(row_data)
            if email:
                try:
                    address = Address.objects.get(email=email[0])
                except Address.DoesNotExist:
                    pass

        if not address:
            address = Address()

        address.organization = row_data.get("Organisation") or ""
        address.name = row_data.get("Nachname") or ""
        address.first_name = row_data.get("Vorname") or ""

        title_raw = row_data.get("Anrede") or ""
        address.title = self._map_title(title_raw, bool(address.organization))

        address.extra = row_data.get("Adresszusatz") or ""
        address.street_name = row_data.get("Strasse") or ""
        address.house_number = row_data.get("Hausnummer") or ""
        address.po_box = parse_bool(row_data.get("Postfach")) or False
        address.po_box_number = row_data.get("Postfach Nr.") or ""

        # PLZ may come as integer from Excel (e.g. 3011)
        plz = str(row_data.get("PLZ") or "").strip()
        address.city_zipcode = plz
        address.city_name = row_data.get("Ort") or ""
        address.country = (
            normalize_country_code(row_data.get("Land")) or get_default_country_code()
        )

        address.telephone = clean_phone_number(row_data.get("Telefon") or "")
        address.mobile = clean_phone_number(row_data.get("2. Telefon") or "")
        address.telephoneOffice = clean_phone_number(row_data.get("Telefon Geschäft"))

        emails = self._get_emails(row_data)
        if emails:
            address.email = emails[0]
            if len(emails) > 1:
                address.email2 = emails[1]

        address.ahv_number = row_data.get("AHV-Nr.") or ""
        address.date_birth = parse_date(row_data.get("Geburtsdatum"))
        address.hometown = row_data.get("Heimatort") or ""

        if import_id:
            address.import_id = import_id

        address.save()

        iban = str(row_data.get("Kontoverbindung") or "").strip().upper().replace(" ", "")
        if iban:
            bank_account = get_or_create_bank_account(iban)
            if bank_account:
                address.bankaccount = bank_account
                address.save()

        return address

    @staticmethod
    def _create_or_update_member(row_data: dict, address: Address):
        try:
            member = Member.objects.get(name=address)
        except Member.DoesNotExist:
            member = Member(name=address)

        date_join = parse_date(row_data.get("Eintritt [Mitglied]"))
        if not date_join:
            raise ValidationError(_("Eintrittsdatum fehlt oder ist ungültig"))

        member.date_join = date_join
        member.date_leave = parse_date(row_data.get("Austritt [Mitglied]"))
        member.flag_01 = parse_bool(get_field_by_prefix(row_data, "Flag 1")) or False
        member.flag_02 = parse_bool(get_field_by_prefix(row_data, "Flag 2")) or False
        member.flag_03 = parse_bool(get_field_by_prefix(row_data, "Flag 3")) or False
        member.flag_04 = parse_bool(get_field_by_prefix(row_data, "Flag 4")) or False
        member.flag_05 = parse_bool(get_field_by_prefix(row_data, "Flag 5")) or False
        member.notes = row_data.get("Bemerkungen [Mitglied]") or ""
        member.save()

    def _create_or_update_share(self, row_data: dict, address: Address):
        """Create or update a Share record linked to the address."""
        share_type = get_or_create_share_type(self.DEFAULT_SHARE_TYPE_NAME)

        person_id = row_data.get("ImportID")
        import_id = f"vfn_{person_id}" if person_id else None

        share = None
        if import_id:
            try:
                share = Share.objects.get(import_id=import_id)
            except Share.DoesNotExist:
                pass

        if not share:
            share = Share(name=address, share_type=share_type)

        quantity_raw = row_data.get("Anzahl [Beteiligungen]")
        quantity = parse_int(quantity_raw)
        share.quantity = quantity if quantity is not None else 1

        value_raw = row_data.get("Betrag pro Stück [Beteiligungen]")
        value = parse_decimal(value_raw)
        share.value = value if value is not None else Decimal("0.00")

        state_raw = str(row_data.get("Status [Beteiligungen]") or "").strip().lower()
        if state_raw in ("bezahlt", "paid", "einbezahlt", "eingezahlt", "zurückbezahlt"):
            share.payment_state = "bezahlt"
        else:
            share.payment_state = "gefordert"

        share_date = parse_date(row_data.get("Datum Beginn [Beteiligungen]"))
        if share_date:
            share.payment_date = share_date
        elif not share.pk:
            # Fallback: use today
            share.payment_date = datetime.date.today()

        share.repayment_date = parse_date(row_data.get("Datum Ende [Beteiligungen]"))

        share.identifier = row_data.get("Beteiligungs-ID") or ""
        share.identifier_external = row_data.get("Beteiligungs-ID extern") or ""
        share.note = row_data.get("Zusatzinfo [Beteiligungen]") or ""

        if import_id:
            share.import_id = import_id

        share.save()

    @staticmethod
    def _get_emails(row_data: dict) -> list[str]:
        ret = []
        raw = str(row_data.get("Email") or "").strip().lower()
        if "@" in raw:
            ret.append(raw)
        raw = str(row_data.get("2. Email") or "").strip().lower()
        if "@" in raw:
            ret.append(raw)
        return ret

    def _map_title(self, title_raw: str, is_organization: bool) -> str:
        if is_organization:
            return "Org"
        if not title_raw:
            return ""
        return self.TITLE_MAPPING.get(title_raw.strip(), "")
