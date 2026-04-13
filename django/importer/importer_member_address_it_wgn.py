"""
Member and Address Excel Importer Service.

This module handles the import of member and address data from Excel files
with the specific column structure from the legacy system.
"""

from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geno.models import Address, Member

from .services import ExcelImporter
from .utils import (
    clean_emails,
    clean_phone_number,
    get_or_create_bank_account,
    parse_bank_account_string,
    parse_date,
    split_plzort,
    split_postfach,
    split_street,
)

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

    def _has_existing(self, row_data: dict, sheet: str | None = None) -> bool:
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

    def _process_single_row(self, row_data: dict, sheet: str | None = None):
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

        if sheet is not None:
            raise ValidationError(_("Sheets are not supported for this importer"))

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
        street_name, house_number = split_street(street)
        address.street_name = street_name or ""
        address.house_number = house_number or ""

        # Handle PO Box - Split PF+Nr
        postfach = row_data.get("P_postfach") or ""
        if postfach:
            po_box, po_box_number = split_postfach(postfach)
            address.po_box = po_box
            address.po_box_number = po_box_number or ""
        else:
            address.po_box = False
            address.po_box_number = ""

        # Split ZIP and city
        plzort = row_data.get("P_plzort") or ""
        city_zipcode, city_name = split_plzort(plzort)
        address.city_zipcode = city_zipcode or ""
        address.city_name = city_name or ""

        address.country = row_data.get("P_land") or "CH"

        # Contact fields - Priority: P_telp/P_mobilep for private, P_telg/P_mobileg for office
        # Clean phone numbers to remove extra leading zeros
        p_telp = clean_phone_number(row_data.get("P_telp") or "")
        p_mobilep = clean_phone_number(row_data.get("P_mobilep") or "")
        p_telg = clean_phone_number(row_data.get("P_telg") or "")
        p_mobileg = clean_phone_number(row_data.get("P_mobileg") or "")

        address.telephone = p_telp or p_mobilep
        address.mobile = p_mobilep if p_telp else ""
        address.telephoneOffice = p_telg or p_mobileg
        address.telephoneOffice2 = p_mobileg if p_telg else ""

        address.email = self._get_primary_email(row_data)
        address.email2 = self._get_secondary_email(row_data, address.email)

        # Website
        address.website = row_data.get("P_homepagep") or row_data.get("P_homepageg") or ""

        # Personal information
        address.date_birth = parse_date(row_data.get("P_geburtsdatum"))
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

    @staticmethod
    def _create_or_update_member(row_data: dict, address: Address):
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
        date_join = parse_date(row_data.get("X_heute"))
        if not date_join:
            raise ValidationError(str(_("Eintrittsdatum (X_heute) fehlt oder ist ungültig")))

        member.date_join = date_join

        # Save member
        member.save()

    @staticmethod
    def _process_bank_accounts(row_data: dict, address: Address):
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
            iban, financial_institution = parse_bank_account_string(zs_dd)

            if iban:
                bank_account = get_or_create_bank_account(iban, holder_dd, financial_institution)
                address.bankaccount = bank_account
                address.save()

    @staticmethod
    def _get_primary_email(row_data: dict) -> str:
        """
        Extract primary email from row data.

        Args:
            row_data: dictionary containing the row data

        Returns:
            Email address or empty string
        """
        email = (
            clean_emails(row_data.get("P_emailp", ""))
            or clean_emails(row_data.get("email", ""))
            or clean_emails(row_data.get("P_emailg", ""))
        )
        return email[0] if email else ""

    @staticmethod
    def _get_secondary_email(row_data: dict, primary_email: str) -> str:
        """
        Extract secondary email from row data.

        Args:
            row_data: dictionary containing the row data
            primary_email: The already determined primary email

        Returns:
            Secondary email address or empty string
        """
        if not primary_email:
            return ""
        for email in clean_emails(row_data.get("P_emailg", "")):
            if email != primary_email:
                return email
        for email in clean_emails(row_data.get("P_emailp", "")):
            if email != primary_email:
                return email
        for email in clean_emails(row_data.get("email", "")):
            if email != primary_email:
                return email
        return ""

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
