"""
Member and Address Excel Importer Service.

This module handles the import of member and address data from Excel files
with the specific column structure from the legacy system.
"""

from __future__ import annotations

import logging
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import Address, BankAccount, Member

from .services import ExcelImporter

logger = logging.getLogger(__name__)


class ImporterMemberAddressITWGN(ExcelImporter):
    """
    Specialized importer for Member and Address data.

    Handles Excel files with the following structure:
    email, ____Person, X_heute, P_nr, ____Adressangaben, P_ansprechperson, P_co,
    P_strasse, P_postfach, P_plzort, P_geschlecht, P_anrede, P_land, P_titel,
    P_briefanrede, ____Kontakt, P_nachname, P_vorname, P_telp, P_telg, P_faxp,
    P_faxg, P_mobilep, P_mobileg, P_emailp, P_emailg, P_homepagep, P_homepageg,
    ____Persönliches, P_beruf, P_arbeitgeber, P_heimatort, P_geburtsort,
    P_geburtsdatum, P_portalregcode, P_portalurllogin, ____Zahlstellen, ZS_dd,
    ZS_kontoinhaberdd, ZS_lsv, ZS_kontoinhaberlsv, ZS_auszahlungnk,
    ZS_kontoinhaberauszahlungnk, ZS_auszahlungverzinsung,
    ZS_kontoinhaberauszahlungverzinsung, ZS_auszahlungmanuell,
    ZS_kontoinhaberauszahlungmanuell
    """

    # Field mapping configuration
    TITLE_MAPPING = {
        "Herr": "Herr",
        "Frau": "Frau",
        "Familie": "Paar",
        "Paar": "Paar",
        "Firma": "Org",
        "Organisation": "Org",
        "Divers": "Divers",
    }

    def _has_existing(self, row_data: dict) -> bool:
        """
        Check if an Address already exists based on import_id or email.

        Args:
            row_data: dictionary containing the row data from Excel
        Raises:
            ValidationError: If a record already exists
        """
        person_number = row_data.get("P_nr")
        import_id = f"legacy_{self.import_job.id}_{person_number}" if person_number else None

        # Check by import_id
        if import_id:
            if Address.objects.filter(import_id=import_id).exists():
                raise ValidationError(
                    _("Adresse mit Import-ID %(import_id)s existiert bereits."),
                    params={"import_id": import_id},
                )

        # Check by email
        email = self._get_primary_email(row_data)
        if email:
            if Address.objects.filter(email=email).exists():
                raise ValidationError(
                    _("Adresse mit E-Mail %(email)s existiert bereits."),
                    params={"email": email},
                )

        return False

    def _process_single_row(self, row_data: dict):
        """
        Process a single row and create/update Address and Member records.

        Args:
            row_data: dictionary containing the row data from Excel

        Raises:
            ValidationError: If the row data is invalid
        """

        # Validate required fields
        if not row_data.get("P_nachname") and not row_data.get("P_vorname"):
            raise ValidationError(_("Mindestens Vor- oder Nachname erforderlich"))

        # Check if this is an organization
        is_organization = bool(row_data.get("P_ansprechperson"))

        # Create or update Address
        address = self._create_or_update_address(row_data, is_organization)

        # Create Member if date_join is available (X_heute field)
        if row_data.get("X_heute"):
            self._create_or_update_member(row_data, address)

        logger.info(f"Successfully processed {address}")

    def _create_or_update_address(self, row_data: dict, is_organization: bool) -> Address:
        """
        Create or update an Address record from row data.

        Args:
            row_data: dictionary containing the row data
            is_organization: Whether this is an organization

        Returns:
            Address instance
        """
        # Get P_nr and build import_id from it
        # Format: legacy_{importjob_id}_{person_number}
        person_number = row_data.get("P_nr")
        import_id = f"legacy_{self.import_job.id}_{person_number}" if person_number else None

        # Try to find existing address by import_id or email
        address = None
        if import_id:
            try:
                address = Address.objects.get(import_id=import_id)
                logger.debug(f"Found existing address by import_id: {import_id}")
            except Address.DoesNotExist:
                pass

        if not address:
            # Try to find by email
            email = self._get_primary_email(row_data)
            if email:
                try:
                    address = Address.objects.get(email=email)
                    logger.debug(f"Found existing address by email: {email}")
                except Address.DoesNotExist:
                    pass

        # If not found, create new
        if not address:
            address = Address()
            logger.debug("Creating new address")

        # Map basic fields - Ensure all have defaults
        if is_organization:
            address.organization = row_data.get("P_nachname") or ""
            address.name = row_data.get("P_ansprechperson") or ""
            address.first_name = row_data.get("P_vorname") or ""
        else:
            address.organization = ""
            address.name = row_data.get("P_nachname") or ""
            address.first_name = row_data.get("P_vorname") or ""

        # Map title (P_anrede / P_geschlecht)
        title_raw = row_data.get("P_anrede") or row_data.get("P_geschlecht", "")
        address.title = self._map_title(title_raw, is_organization)

        # Address fields - Ensure all have defaults
        address.extra = row_data.get("P_co") or ""

        # Split street and house number
        street = row_data.get("P_strasse") or ""
        street_name, house_number = self._split_street(street)
        address.street_name = street_name or ""
        address.house_number = house_number or ""

        # Handle PO Box - Split PF+Nr
        postfach = row_data.get("P_postfach") or ""
        if postfach:
            po_box, po_box_number = self._split_postfach(postfach)
            address.po_box = po_box
            address.po_box_number = po_box_number or ""
        else:
            address.po_box = False
            address.po_box_number = ""

        # Split ZIP and city
        plzort = row_data.get("P_plzort") or ""
        city_zipcode, city_name = self._split_plzort(plzort)
        address.city_zipcode = city_zipcode or ""
        address.city_name = city_name or ""

        address.country = row_data.get("P_land") or "Schweiz"

        # Contact fields - Priority: P_telp/P_mobilep for private, P_telg/P_mobileg for office
        # Clean phone numbers to remove extra leading zeros
        p_telp = self._clean_phone_number(row_data.get("P_telp") or "")
        p_mobilep = self._clean_phone_number(row_data.get("P_mobilep") or "")
        p_telg = self._clean_phone_number(row_data.get("P_telg") or "")
        p_mobileg = self._clean_phone_number(row_data.get("P_mobileg") or "")

        address.telephone = p_telp or p_mobilep
        address.mobile = p_mobilep if p_telp else ""
        address.telephoneOffice = p_telg or p_mobileg
        address.telephoneOffice2 = p_mobileg if p_telg else ""

        # Email fields - Priority: P_emailp/P_emailg (fall back to 'email' column)
        p_emailp = row_data.get("P_emailp") or ""
        p_emailg = row_data.get("P_emailg") or ""
        email_fallback = row_data.get("email") or ""

        address.email = p_emailp or email_fallback or p_emailg
        address.email2 = p_emailg if (p_emailp or email_fallback) else ""

        # Website
        address.website = row_data.get("P_homepagep") or row_data.get("P_homepageg") or ""

        # Personal information
        address.date_birth = self._parse_date(row_data.get("P_geburtsdatum"))
        address.hometown = row_data.get("P_heimatort") or ""

        # Occupation: Combine P_beruf + P_arbeitgeber
        beruf = row_data.get("P_beruf") or ""
        arbeitgeber = row_data.get("P_arbeitgeber") or ""
        if beruf and arbeitgeber:
            address.occupation = f"{beruf}, {arbeitgeber}"
        elif beruf:
            address.occupation = beruf
        elif arbeitgeber:
            address.occupation = arbeitgeber
        else:
            address.occupation = ""

        # import_id (P_nr as legacy_{P_nr})
        if import_id:
            address.import_id = import_id

        # Save address
        address.save()

        # Handle bank accounts if present
        self._process_bank_accounts(row_data, address)

        return address

    def _create_or_update_member(self, row_data: dict, address: Address):
        """
        Create or update a Member record.

        Args:
            row_data: dictionary containing the row data
            address: Associated Address instance
        """
        # Try to find existing member
        try:
            member = Member.objects.get(name=address)
            logger.debug(f"Found existing member for address: {address}")
        except Member.DoesNotExist:
            member = Member(name=address)
            logger.debug(f"Creating new member for address: {address}")

        # Parse join date from X_heute
        date_join = self._parse_date(row_data.get("X_heute"))
        if not date_join:
            raise ValidationError(str(_("Eintrittsdatum (X_heute) fehlt oder ist ungültig")))

        member.date_join = date_join

        # Save member
        member.save()

    def _process_bank_accounts(self, row_data: dict, address: Address):
        """
        Process bank account information and link to address.

        Args:
            row_data: dictionary containing the row data
            address: Associated Address instance
        """
        # Primary bank account (DD - Direct Debit)
        # ZS_dd often looks like "PostFinance AG, 3030 Bern, Clearing-Nr. 9000, Konto-Nr. CH6309000000123456789"
        zs_dd = row_data.get("ZS_dd", "")
        holder_dd = row_data.get("ZS_kontoinhaberdd", "")

        if zs_dd:
            # Parse the bank account string
            iban, financial_institution = self._parse_bank_account_string(zs_dd)

            if iban:
                bank_account = self._get_or_create_bank_account(
                    iban, holder_dd, financial_institution
                )
                address.bankaccount = bank_account
                address.save()

    def _parse_bank_account_string(self, bank_string: str) -> tuple:
        """
        Parse bank account string to extract IBAN and financial institution.

        Example input: "PostFinance AG, 3030 Bern, Clearing-Nr. 9000, Konto-Nr. CH6309000000123456789"

        Args:
            bank_string: Complex bank account string

        Returns:
            Tuple of (iban, financial_institution)
        """
        import re

        if not bank_string:
            return ("", "")

        bank_string = bank_string.strip()

        # Extract IBAN (Swiss IBAN: CH followed by 2 digits and up to 17 alphanumeric characters, may have spaces)
        # Pattern allows for optional spaces between characters
        iban_pattern = r"CH\s*\d{2}[\s\dA-Z]{1,23}"
        iban_match = re.search(iban_pattern, bank_string, re.IGNORECASE)
        if iban_match:
            # Remove all spaces and uppercase
            iban = re.sub(r"\s+", "", iban_match.group()).upper()
        else:
            iban = ""

        # Extract financial institution (usually the first part before first comma)
        financial_institution = ""
        parts = bank_string.split(",")
        if parts:
            first_part = parts[0].strip()
            # Remove common patterns like "Konto-Nr.", "Clearing-Nr." etc.
            if not re.search(r"(Konto|Clearing|IBAN)", first_part, re.IGNORECASE):
                financial_institution = first_part

        return (iban, financial_institution)

    def _get_or_create_bank_account(
        self, iban: str, account_holder: str = "", financial_institution: str = ""
    ) -> BankAccount | None:
        """
        Get or create a BankAccount instance.

        Args:
            iban: IBAN number
            account_holder: Account holder name
            financial_institution: Name of the bank/financial institution

        Returns:
            BankAccount instance or None
        """
        if not iban:
            return None

        iban = iban.strip().upper()

        try:
            bank_account = BankAccount.objects.get(iban=iban)
        except BankAccount.DoesNotExist:
            bank_account = BankAccount(iban=iban)

        if account_holder:
            bank_account.account_holders = account_holder.strip()

        if financial_institution:
            bank_account.financial_institution = financial_institution.strip()

        bank_account.save()
        return bank_account

    def _get_primary_email(self, row_data: dict) -> str:
        """
        Extract primary email from row data.

        Args:
            row_data: dictionary containing the row data

        Returns:
            Email address or empty string
        """
        email = row_data.get("P_emailp", "") or row_data.get("email", "")
        return email.strip().lower() if email else ""

    def _map_title(self, title_raw: str, is_organization: bool) -> str:
        """
        Map title from Excel to Address model choices.

        Args:
            title_raw: Raw title string from Excel
            is_organization: Whether this is an organization

        Returns:
            Mapped title value
        """
        if is_organization:
            return "Org"

        if not title_raw:
            return ""

        title_raw = title_raw.strip()
        return self.TITLE_MAPPING.get(title_raw, "")

    def _split_street(self, street: str) -> tuple:
        """
        Split street into street name and house number.

        Args:
            street: Full street string

        Returns:
            Tuple of (street_name, house_number)
        """
        if not street:
            return ("", "")

        street = street.strip()

        # Try to split on last space if it looks like a number
        parts = street.rsplit(" ", 1)
        if len(parts) == 2:
            street_name, potential_number = parts
            # Check if the last part contains digits
            if any(char.isdigit() for char in potential_number):
                return (street_name.strip(), potential_number.strip())

        # If no clear split, return all as street name
        return (street, "")

    def _split_postfach(self, postfach: str) -> tuple:
        """
        Split Postfach into boolean indicator and number.

        Args:
            postfach: PO Box string (e.g., "Postfach 1234" or "1234")

        Returns:
            Tuple of (po_box_bool, po_box_number)
        """
        if not postfach:
            return (False, "")

        postfach = postfach.strip()

        # Remove common prefixes like "Postfach", "PF", etc.
        import re

        postfach_cleaned = re.sub(r"^(Postfach|postfach|PF|Pf|pf)\s*", "", postfach)

        # Extract number
        number_match = re.search(r"\d+", postfach_cleaned)
        if number_match:
            return (True, number_match.group())

        # If we have text but no clear number, still mark as PO Box
        if postfach_cleaned:
            return (True, postfach_cleaned)

        return (True, "")

    def _split_plzort(self, plzort: str) -> tuple:
        """
        Split PLZ/Ort into zipcode and city name.

        Args:
            plzort: Combined PLZ and Ort string

        Returns:
            Tuple of (zipcode, city_name)
        """
        if not plzort:
            return ("", "")

        plzort = plzort.strip()

        # Try to split on first space
        parts = plzort.split(" ", 1)
        if len(parts) == 2:
            plz, ort = parts
            # Check if first part is numeric (Swiss postal codes are 4 digits)
            if plz.isdigit():
                return (plz.strip(), ort.strip())

        # If no clear split, assume it's all city name
        return ("", plzort)

    def _clean_phone_number(self, phone: str) -> str:
        """
        Clean phone number by removing extra leading zeros.

        Swiss phone numbers follow the pattern: 0XX YYY ZZ AA
        If there's an additional leading 0, strip it.

        Args:
            phone: Phone number string

        Returns:
            Cleaned phone number
        """
        import re

        if not phone:
            return ""

        phone = phone.strip()

        # Remove all whitespace and common separators for analysis
        phone_digits = re.sub(r"[\s\-./()]", "", phone)

        # Check if it matches Swiss pattern with extra leading zero: 00XX...
        # Swiss numbers start with 0XX (where XX is 2 digits), so 00XX is invalid
        if re.match(r"^00\d{2}", phone_digits):
            # Remove the first 0
            phone_digits = phone_digits[1:]

            # Try to reconstruct with original formatting style
            # If original had spaces, try to maintain similar formatting
            if " " in phone or "-" in phone or "/" in phone or "." in phone:
                # Format as: 0XX YYY ZZ AA (standard Swiss format)
                if len(phone_digits) >= 10:
                    return f"{phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:8]} {phone_digits[8:]}"
                else:
                    return phone_digits
            return phone_digits

        return phone

    def _parse_date(self, date_str) -> datetime.date | None:
        """
        Parse date from various formats.

        Args:
            date_str: Date string or datetime object

        Returns:
            datetime.date object or None
        """
        if not date_str:
            return None

        # If already a date/datetime object
        if isinstance(date_str, datetime):
            return date_str.date()
        if hasattr(date_str, "date"):
            return date_str.date()

        # Try parsing string formats
        if isinstance(date_str, str):
            date_str = date_str.strip()
            if not date_str:
                return None

            # Common date formats
            formats = [
                "%Y-%m-%d",
                "%d.%m.%Y",
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%Y/%m/%d",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

        logger.warning(f"Could not parse date: {date_str}")
        return None
