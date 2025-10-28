import datetime
from dataclasses import dataclass
from decimal import Decimal

from finance.accounting.accounts import Account


@dataclass
class Transaction:
    splits: list["Split"]
    date: datetime.date | datetime.datetime | str
    description: str = ""
    currency: str = "CHF"

    def __str__(self):
        ret = f"{self.date} {self.currency}"
        if len(self.splits) > 1:
            ret += (
                f" {self.currency} {self.splits[0].amount}"
                f" {self.splits[0].account} => {self.splits[1].account}"
            )
            if len(self.splits) == 3:
                ret += " (+ 1 weitere Buchung)"
            elif len(self.splits) > 3:
                ret += f" (+ {len(self.splits) - 2} weitere Buchungen)"
        if self.description:
            ret += f" {self.description}"
        return ret

    def __repr__(self):
        return f"Transaction(date={self.date}, description='{self.description}')"


@dataclass
class Split:
    account: Account
    amount: Decimal | float | str
