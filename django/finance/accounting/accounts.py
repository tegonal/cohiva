from dataclasses import dataclass
from enum import Enum


class AccountKeys(Enum):
    _value_: str
    DEFAULT_DEBTOR = "_default_debtor"
    DEFAULT_DEBTOR_MANUAL = "_default_debtor_manual"
    SHARES_DEBTOR_MANUAL = "_shares_debtor_manual"
    DEFAULT_RECEIVABLES = "_default_receivables"
    NK_RECEIVABLES = "_nk_receivables"
    CASH = "_cash"
    RENT_BUSINESS = "_rent_business"
    RENT_PARKING = "_rent_parking"
    RENT_OTHER = "_rent_other"
    NK = "_nk"
    NK_FLAT = "_nk_flat"
    STROM = "_strom"
    RENT_REDUCTION = "_rent_reduction"
    RENT_RESERVATION = "_rent_reservation"
    MIETDEPOT = "_mietdepot"
    SCHLUESSELDEPOT = "_schluesseldepot"
    KIOSK = "_kiosk"
    SPENDE = "_spende"
    OTHER = "_other"
    MEMBER_FEE = "_member_fee"
    MEMBER_FEE_ONETIME = "_member_fee_onetime"
    SHARES_MEMBERS = "_shares_members"
    SHARES_LOAN_NOINTEREST = "_shares_loan_nointerest"
    SHARES_LOAN_INTEREST = "_shares_loan_interest"
    SHARES_DEPOSIT = "_shares_deposit"
    SHARES_CLEARING = "_shares_clearing"
    SHARES_INTEREST = "_shares_interest"
    SHARES_INTEREST_TAX = "_shares_interest_tax"
    INTEREST_LOAN = "_interest_loan"
    INTEREST_DEPOSIT = "_interest_deposit"


class AccountRoles(Enum):
    _value_: int
    DEFAULT = 1
    QR_DEBTOR = 2


@dataclass
class Account:
    name: str
    code: AccountKeys | str  # Account code for financial accounting
    role: AccountRoles = AccountRoles.DEFAULT
    iban: str | None = None  # QR-IBAN for QR-Bills
    account_iban: str | None = None  # Account IBAN if different from QR-IBAN

    @classmethod
    def from_settings(cls, account_key: AccountKeys | str):
        from django.conf import settings

        if account_key not in settings.FINANCIAL_ACCOUNTS:
            return None
        return cls.from_settings_dict(settings.FINANCIAL_ACCOUNTS[account_key])

    @classmethod
    def from_settings_dict(cls, account_settings: dict):
        return Account(
            role=account_settings.get("role", AccountRoles.DEFAULT),
            name=account_settings.get("name"),
            code=account_settings.get("account_code"),
            iban=account_settings.get("iban"),
            account_iban=account_settings.get("account_iban"),
        )
