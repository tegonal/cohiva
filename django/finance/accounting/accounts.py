import re
from dataclasses import dataclass
from enum import Enum


class AccountKey(Enum):
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
    NK_VIRTUAL_1 = "_nk_virtual_1"
    NK_VIRTUAL_2 = "_nk_virtual_2"
    NK_VIRTUAL_3 = "_nk_virtual_3"
    NK_VIRTUAL_4 = "_nk_virtual_4"
    NK_VIRTUAL_5 = "_nk_virtual_5"
    NK_VIRTUAL_6 = "_nk_virtual_6"


class AccountRole(Enum):
    _value_: int
    DEFAULT = 1
    QR_DEBTOR = 2
    NK_VIRTUAL = 3


@dataclass
class Account:
    name: str
    prefix: str  # Account code/prefix for financial accounting
    _code: str | None = None
    building_based: bool = False
    role: AccountRole = AccountRole.DEFAULT
    iban: str | None = None  # QR-IBAN for QR-Bills
    account_iban: str | None = None  # Account IBAN if different from QR-IBAN

    @classmethod
    def from_settings(cls, account_key: AccountKey | str):
        from django.conf import settings

        if account_key not in settings.FINANCIAL_ACCOUNTS:
            return None
        return cls.from_settings_dict(settings.FINANCIAL_ACCOUNTS[account_key])

    @classmethod
    def from_settings_dict(cls, account_settings: dict):
        return Account(
            role=account_settings.get("role", AccountRole.DEFAULT),
            name=account_settings.get("name"),
            prefix=account_settings.get("account_code"),
            building_based=account_settings.get("building_based", False),
            iban=account_settings.get("iban"),
            account_iban=account_settings.get("account_iban"),
        )

    def set_code(self, building=None, rental_units=None, contract=None):
        if self.building_based:
            if (
                building is None
                and rental_units is None
                and contract
                and contract.rental_units
                and contract.rental_units.all().exists()
            ):
                rental_units = contract.rental_units.all()
            if building is None and rental_units and rental_units.first():
                building = rental_units.first().building
            if building and building.accounting_postfix:
                postfix = "%03d" % building.accounting_postfix
                self._code = re.sub(r"(\d+)$", r"\1%s" % postfix, self.prefix)
        self._code = self.prefix

    @property
    def code(self):
        if not self._code and not self.building_based:
            return self.prefix
        return self._code
