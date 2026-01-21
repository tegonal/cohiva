"""
Transaction type definitions for Cohiva.

Centralizes transaction type choices to avoid duplication across forms.
Different contexts (manual entry, upload processing, filtering) may need
different subsets of transaction types.
"""

import datetime

from django.conf import settings

import geno.settings as geno_settings


def get_manual_transaction_types():
    """
    Get transaction type choices for manual transaction entry forms.

    Returns:
        list: List of (value, label) tuples for transaction types available
              in manual entry forms (TransactionForm).
    """
    now = datetime.datetime.now()
    transaction_types = []

    if settings.GENO_ID == "HSG":
        transaction_types.append(("as_single", "Einzahlung Anteilschein(e) Einzelmitglied"))
        transaction_types.append(("as_extra", "Einzahlung Anteilschein(e) freiwillig"))
        transaction_types.append(("as_founder", "Einzahlung Anteilschein(e) Gründungsmitlied"))
        transaction_types.append(("development", "Einzahlung Entwicklungsbeitrag"))

    if geno_settings.TRANSACTION_MEMBERFEE_STARTYEAR:
        for year in range(now.year + 1, geno_settings.TRANSACTION_MEMBERFEE_STARTYEAR - 1, -1):
            transaction_types.append((f"fee{year}", f"Mitgliederbeitrag {year}"))

    if settings.GENO_ID == "Warmbaechli" or (settings.DEMO and settings.DEBUG):
        transaction_types.append(("entry_as", "Beitrittsgebühr+Anteilschein(e) (Post)"))
        transaction_types.append(("share_as", "Anteilscheine (Bank)"))
        transaction_types.append(
            ("entry_as_inv", "Beitrittsgebühr 200.- + Anteilscheine (Zahlung Rechnung)")
        )
        transaction_types.append(("share_as_inv", "Anteilscheine (Zahlung Rechnung)"))
        transaction_types.append(
            ("loan_interest_toloan", "Darlehenszins an Darlehen anrechnen (mit Standard-Zinssatz)")
        )
        transaction_types.append(
            (
                "loan_interest_todeposit",
                "Darlehenszins an Depositenkasse gutschreiben (mit Standard-Zinssatz)",
            )
        )

    return transaction_types


def get_upload_transaction_types():
    """
    Get transaction type choices for processing uploaded transactions.

    Returns:
        list: List of (value, label) tuples for transaction types available
              when processing uploaded transaction files (TransactionUploadProcessForm).
    """
    transaction_types = []
    transaction_types.append(("ignore", "=== Ignorieren ==="))
    transaction_types.append(("invoice_payment", "Einzahlung Rechnung"))

    if settings.GENO_ID == "Warmbaechli":
        transaction_types.append(("entry_as", "Beitrittsgebühr 200.- + Anteilscheine (Post)"))
        transaction_types.append(("share_as", "Anteilscheine (Bank)"))
        transaction_types.append(
            ("entry_as_inv", "Beitrittsgebühr 200.- + Anteilscheine (Zahlung Rechnung)")
        )
        transaction_types.append(("share_as_inv", "Anteilscheine (Zahlung Rechnung)"))
        transaction_types.append(("memberfee", "Mitgliederbeitrag 80.- aktuelles Jahr"))

    transaction_types.append(("kiosk_payment", "Einzahlung Kiosk/Getränke"))

    return transaction_types
