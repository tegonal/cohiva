"""
Member, Address, and Share Excel Importer for VFN data.

This module handles the import of member, address, and share data from the
VFN Excel file: Adressen_GenossenschafterInnen_260314_Cohiva.xlsm

Expected columns:
  ID, Anrede, Titel, Vorname, Nachname, Firma, Kontaktperson,
  Strasse, PLZ, Ort, Land, Telefon, Mobile, Email,
  Eintrittsdatum, Genossenschaftsanteile Anzahl, Genossenschaftsanteile Wert,
  Genossenschaftsanteile Status, Genossenschaftsanteile Datum, IBAN, Kontoinhaber, Bank
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import Address, BankAccount, Member, Share, ShareType

from .services import ExcelImporter

logger = logging.getLogger(__name__)


class ImporterMemberAddressSharesVFN(ExcelImporter):
    """
    Specialized importer for Member, Address, and Share data from VFN files.

    Handles Excel files (Adressen_GenossenschafterInnen_260314_Cohiva.xlsm)
    with the following column structure:
    ID, Anrede, Titel, Vorname, Nachname, Firma, Kontaktperson,
    Strasse, PLZ, Ort, Land, Telefon, Mobile, Email,
    Eintrittsdatum, Genossenschaftsanteile Anzahl, Genossenschaftsanteile Wert,
    Genossenschaftsanteile Status, Genossenschaftsanteile Datum, IBAN, Kontoinhaber, Bank
    """

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

    def _has_existing(self, row_data: dict) -> bool:
        """
        Check if an Address already exists based on import_id or email.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        person_id = row_data.get("ID")
        import_id = f"vfn_{self.import_job.id}_{person_id}" if person_id else None

        if import_id and Address.objects.filter(import_id=import_id).exists():
            raise ValidationError(
                _("Adresse mit Import-ID %(import_id)s existiert bereits."),
                params={"import_id": import_id},
            )

        email = self._get_email(row_data)
        if email and Address.objects.filter(email=email).exists():
            raise ValidationError(
                _("Adresse mit E-Mail %(email)s existiert bereits."),
                params={"email": email},
            )

        return False

    def _process_single_row(self, row_data: dict):
        """
        Process a single row and create/update Address, Member, and Share records.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If the row data is invalid
        """
        if not row_data.get("Nachname") and not row_data.get("Vorname") and not row_data.get("Firma"):
            raise ValidationError(_("Mindestens Vor- oder Nachname oder Firma erforderlich"))

        is_organization = bool(row_data.get("Firma"))
        address = self._create_or_update_address(row_data, is_organization)

        if row_data.get("Eintrittsdatum"):
            self._create_or_update_member(row_data, address)

        if row_data.get("Genossenschaftsanteile Anzahl") or row_data.get("Genossenschaftsanteile Wert"):
            self._create_or_update_share(row_data, address)

        logger.info(f"Successfully processed {address}")

    def _create_or_update_address(self, row_data: dict, is_organization: bool) -> Address:
        person_id = row_data.get("ID")
        import_id = f"vfn_{self.import_job.id}_{person_id}" if person_id else None

        address = None
        if import_id:
            try:
                address = Address.objects.get(import_id=import_id)
            except Address.DoesNotExist:
                pass

        if not address:
            email = self._get_email(row_data)
            if email:
                try:
                    address = Address.objects.get(email=email)
                except Address.DoesNotExist:
                    pass

        if not address:
            address = Address()

        if is_organization:
            address.organization = row_data.get("Firma") or ""
            address.name = row_data.get("Kontaktperson") or row_data.get("Nachname") or ""
            address.first_name = row_data.get("Vorname") or ""
        else:
            address.organization = ""
            address.name = row_data.get("Nachname") or ""
            address.first_name = row_data.get("Vorname") or ""

        title_raw = row_data.get("Anrede") or ""
        address.title = self._map_title(title_raw, is_organization)

        street = row_data.get("Strasse") or ""
        street_name, house_number = self._split_street(street)
        address.street_name = street_name or ""
        address.house_number = house_number or ""

        plz = str(row_data.get("PLZ") or "").strip()
        # PLZ may come as integer from Excel (e.g. 3011)
        address.city_zipcode = plz
        address.city_name = row_data.get("Ort") or ""
        address.country = row_data.get("Land") or "CH"

        address.telephone = self._clean_phone(row_data.get("Telefon") or "")
        address.mobile = self._clean_phone(row_data.get("Mobile") or "")

        address.email = self._get_email(row_data)

        if import_id:
            address.import_id = import_id

        address.save()

        iban = str(row_data.get("IBAN") or "").strip().upper().replace(" ", "")
        if iban:
            holder = str(row_data.get("Kontoinhaber") or "").strip()
            institution = str(row_data.get("Bank") or "").strip()
            bank_account = self._get_or_create_bank_account(iban, holder, institution)
            if bank_account:
                address.bankaccount = bank_account
                address.save()

        return address

    def _create_or_update_member(self, row_data: dict, address: Address):
        try:
            member = Member.objects.get(name=address)
        except Member.DoesNotExist:
            member = Member(name=address)

        date_join = self._parse_date(row_data.get("Eintrittsdatum"))
        if not date_join:
            raise ValidationError(_("Eintrittsdatum fehlt oder ist ungültig"))

        member.date_join = date_join
        member.save()

    def _create_or_update_share(self, row_data: dict, address: Address):
        """Create or update a Share record linked to the address."""
        share_type = self._get_or_create_share_type()

        person_id = row_data.get("ID")
        import_id = f"vfn_{self.import_job.id}_share_{person_id}" if person_id else None

        share = None
        if import_id:
            # Import ID is stored in Share.note as a fallback since Share has no import_id field
            existing = Share.objects.filter(name=address, share_type=share_type).first()
            if existing:
                share = existing

        if not share:
            share = Share(name=address, share_type=share_type)

        quantity_raw = row_data.get("Genossenschaftsanteile Anzahl")
        quantity = self._parse_int(quantity_raw)
        share.quantity = quantity if quantity is not None else 1

        value_raw = row_data.get("Genossenschaftsanteile Wert")
        value = self._parse_decimal(value_raw)
        share.value = value if value is not None else Decimal("0.00")

        state_raw = str(row_data.get("Genossenschaftsanteile Status") or "").strip().lower()
        if state_raw in ("bezahlt", "paid"):
            share.state = "bezahlt"
        else:
            share.state = "gefordert"

        share_date = self._parse_date(row_data.get("Genossenschaftsanteile Datum"))
        if share_date:
            share.date = share_date
        elif not share.pk:
            # Fallback: use entry date
            entry_date = self._parse_date(row_data.get("Eintrittsdatum"))
            if entry_date:
                share.date = entry_date
            else:
                from datetime import date as date_cls
                share.date = date_cls.today()

        if import_id:
            share.note = import_id

        share.save()

    def _get_or_create_share_type(self) -> ShareType:
        """Get or create the default share type."""
        share_type, _ = ShareType.objects.get_or_create(
            name=self.DEFAULT_SHARE_TYPE_NAME,
            defaults={
                "description": "Genossenschaftsanteil",
                "standard_interest": Decimal("0.00"),
            },
        )
        return share_type

    def _get_or_create_bank_account(
        self, iban: str, account_holder: str = "", financial_institution: str = ""
    ) -> BankAccount | None:
        if not iban:
            return None
        try:
            bank_account = BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            bank_account = BankAccount(iban=iban)
        if account_holder:
            bank_account.account_holders = account_holder
        if financial_institution:
            bank_account.financial_institution = financial_institution
        bank_account.save()
        return bank_account

    def _get_email(self, row_data: dict) -> str:
        raw = str(row_data.get("Email") or "").strip().lower()
        if "@" in raw:
            return raw
        return ""

    def _map_title(self, title_raw: str, is_organization: bool) -> str:
        if is_organization:
            return "Org"
        if not title_raw:
            return ""
        return self.TITLE_MAPPING.get(title_raw.strip(), "")

    def _split_street(self, street: str) -> tuple:
        if not street:
            return ("", "")
        street = street.strip()
        parts = street.rsplit(" ", 1)
        if len(parts) == 2 and any(c.isdigit() for c in parts[1]):
            return (parts[0].strip(), parts[1].strip())
        return (street, "")

    def _clean_phone(self, phone: str) -> str:
        import re
        if not phone:
            return ""
        phone = str(phone).strip()
        digits = re.sub(r"[\s\-./()]", "", phone)
        if re.match(r"^00\d{2}", digits):
            digits = digits[1:]
            if len(digits) >= 10:
                return f"{digits[:3]} {digits[3:6]} {digits[6:8]} {digits[8:]}"
        return phone

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
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(date_val, fmt).date()
                except ValueError:
                    continue
        logger.warning(f"Could not parse date: {date_val}")
        return None

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

    def _parse_int(self, value) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse int: {value}")
            return None
