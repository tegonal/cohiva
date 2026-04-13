"""Common utility functions used by the specific import services."""

import datetime
import logging
import re
from decimal import Decimal, InvalidOperation

from geno.models import BankAccount

logger = logging.getLogger(__name__)


def get_field_by_prefix(row_data: dict, prefix: str):
    for key, value in row_data.items():
        if key.startswith(prefix):
            return value
    return None


def get_or_create_bank_account(
    iban: str, account_holder: str = "", financial_institution: str = ""
) -> BankAccount | None:
    """
    Get or create a BankAccount instance.

    Args:
        iban: IBAN
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


def parse_bank_account_string(bank_string: str) -> tuple:
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
        return "", ""

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

    return iban, financial_institution


def parse_address_string(address_str: str) -> dict | None:
    """
    Parse a combined address string into components.

    Args:
        address_str: Address string like "Teststrasse 42, 3011 Bern"

    Returns:
        dictionary with address components or None
    """
    if not address_str:
        return None

    result = {"street_name": "", "house_number": "", "zipcode": "", "city": ""}

    # Split by comma
    parts = [p.strip() for p in address_str.split(",")]

    if len(parts) >= 1:
        # First part is street
        street_name, house_number = split_street(parts[0])
        result["street_name"] = street_name
        result["house_number"] = house_number

    if len(parts) >= 2:
        # Second part is PLZ + city
        plzort = parts[1]
        plz_parts = plzort.split(None, 1)
        if len(plz_parts) == 2 and plz_parts[0].isdigit():
            result["zipcode"] = plz_parts[0]
            result["city"] = plz_parts[1]
        else:
            result["city"] = plzort

    return result


def parse_date(date_str) -> datetime.date | None:
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
    if isinstance(date_str, datetime.datetime):
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
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

    logger.warning(f"Could not parse date: {date_str}")
    return None


def parse_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not parse int: {value}")
        return None


def parse_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (Decimal, int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            value = (
                value.replace("'", "")
                .replace(",", ".")
                .replace("CHF", "")
                .replace("Fr.", "")
                .strip()
            )
            if not value:
                return None
            return Decimal(value)
    except (InvalidOperation, ValueError):
        logger.warning(f"Could not parse decimal: {value}")
    return None


def split_street(street: str) -> tuple:
    """
    Split street into street name and house number.

    Args:
        street: Full street string

    Returns:
        Tuple of (street_name, house_number)
    """
    if not street:
        return "", ""

    street = street.strip()

    # Try to split on last space if it looks like a number
    parts = street.rsplit(" ", 1)
    if len(parts) == 2:
        street_name, potential_number = parts
        # Check if the last part contains digits
        if any(char.isdigit() for char in potential_number):
            return (street_name.strip(), potential_number.strip())

    # If no clear split, return all as street name
    return street, ""


def split_postfach(postfach: str) -> tuple:
    """
    Split Postfach into boolean indicator and number.

    Args:
        postfach: PO Box string (e.g., "Postfach 1234" or "1234")

    Returns:
        Tuple of (po_box_bool, po_box_number)
    """
    if not postfach:
        return False, ""

    postfach = postfach.strip()

    # Remove common prefixes like "Postfach", "PF", etc.
    import re

    postfach_cleaned = re.sub(r"^(Postfach|postfach|PF|Pf|pf)\s*", "", postfach)

    # Extract number
    number_match = re.search(r"\d+", postfach_cleaned)
    if number_match:
        return True, number_match.group()

    # If we have text but no clear number, still mark as PO Box
    if postfach_cleaned:
        return True, postfach_cleaned

    return True, ""


def split_plzort(plzort: str) -> tuple:
    """
    Split PLZ/Ort into zipcode and city name.

    Args:
        plzort: Combined PLZ and Ort string

    Returns:
        Tuple of (zipcode, city_name)
    """
    if not plzort:
        return "", ""

    plzort = plzort.strip()

    # Try to split on the first space
    parts = plzort.split(" ", 1)
    if len(parts) == 2:
        plz, ort = parts
        # Check if the first part is numeric (Swiss postal codes are 4 digits)
        if plz.isdigit():
            return plz.strip(), ort.strip()

    # If no clear split, assume it's all city name
    return "", plzort


def clean_phone_number(phone: str) -> str:
    """
    Clean phone number by removing extra leading zeros.

    Swiss phone numbers follow the pattern: 0XX YYY ZZ AA
    If there's an additional leading 0, strip it.

    Args:
        phone: Phone number string

    Returns:
        Cleaned phone number
    """

    if not phone:
        return ""

    phone = phone.strip()

    # Remove all whitespace and common separators for analysis
    phone_digits = re.sub(r"[\s\-./()]", "", phone)

    # Check if it matches the Swiss pattern with an extra leading zero: 00XX...
    # Swiss numbers start with 0XX (where XX is 2 digits), so 00XX is invalid
    if re.match(r"^00\d{2}", phone_digits):
        # Remove the first 0
        phone_digits = phone_digits[1:]

        # Try to reconstruct with an original formatting style
        # If original had spaces, try to maintain similar formatting
        if " " in phone or "-" in phone or "/" in phone or "." in phone:
            # Format as: 0XX YYY ZZ AA (standard Swiss format)
            if len(phone_digits) >= 10:
                return f"{phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:8]} {phone_digits[8:]}"
            else:
                return phone_digits
        return phone_digits

    return phone


def clean_emails(email: str) -> list[str]:
    """Split multiple emails separated by semicolon and remove invalid ones."""
    if not email or not isinstance(email, str):
        return []
    email_addresses = email.split(";")
    map(lambda x: x.strip().lower(), email_addresses)
    return list(filter(lambda x: "@" in x, email_addresses))
