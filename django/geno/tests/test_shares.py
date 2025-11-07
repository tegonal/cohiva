import datetime
from decimal import ROUND_HALF_UP, Decimal
from unittest.mock import ANY, patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

import geno.shares
from finance.accounting import Account, AccountingManager, AccountKey

from ..models import Address, Building, Contract, Share, ShareType
from .base import GenoAdminTestCase


class ShareTest(GenoAdminTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.end_of_prev_year = datetime.date(datetime.datetime.now().year - 1, 12, 31)
        cls.loan = ShareType.objects.get(name="Darlehen verzinst")
        cls.loan_special = ShareType.objects.get(name="Darlehen spezial")
        cls.deposit = ShareType.objects.get(name="Depositenkasse")
        cls.tax_rate = 0.35

    def test_share_overview(self):
        response = self.client.get("/geno/share/overview/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("CHF 40&#x27;500.00", response.content.decode())

    def test_share_detail_selectedContractAndBuilding(self):
        now = timezone.now()
        contract = Contract.objects.create(date=now)
        building = Building.objects.create()
        address = Address.objects.create()
        sharetype = ShareType.objects.create()

        # Check model constraint
        constraint_name = "geno_share_attached_to_building_or_contract"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Share.objects.create(
                name=address,
                date=now,
                share_type=sharetype,
                value=200,
                attached_to_contract=contract,
                attached_to_building=building,
            )

        # Check form validation
        with self.assertRaises(ValidationError):
            share = Share(
                name=address,
                date=now,
                share_type=sharetype,
                value=200,
                attached_to_contract=contract,
                attached_to_building=building,
            )
            share.clean()

    @patch("geno.shares.create_interest_transactions_execute")
    def test_create_interest_transactions(self, mock_execute):
        ret = geno.shares.create_interest_transactions()
        mock_execute.assert_called_once_with(self.end_of_prev_year)
        self.assertEqual(ret, [])

    @patch("geno.shares.create_interest_transactions_execute")
    def test_create_interest_transactions_with_warning(self, mock_execute):
        Share.objects.create(
            name=self.addresses[1],
            date=self.end_of_prev_year,
            is_interest_credit=True,
            value=100,
            share_type=self.loan,
        )
        ret = geno.shares.create_interest_transactions()
        mock_execute.assert_called_once_with(self.end_of_prev_year)
        self.assertEqual(
            ret,
            [
                {
                    "info": (
                        "WARNUNG: Es sieht so aus als ob die Zinsbuchungen schon ausgeführt "
                        "wurden (1 Zins-Beteiligungen gefunden). Bitte überprüfen!"
                    )
                }
            ],
        )

    @patch("geno.shares.add_interest_transaction")
    def test_interest_transactions_execute_none(self, mock_add_transaction):
        Share.objects.all().update(date_end=datetime.date(2000, 1, 1))
        ret = geno.shares.create_interest_transactions_execute(self.end_of_prev_year)
        mock_add_transaction.assert_not_called()
        self.assertEqual(
            ret,
            [
                {"info": "Transaktionen in Buchhaltung GESPEICHERT!"},
                {"info": "Zins-Beteiligungen GESPEICHERT!"},
            ],
        )

    @patch("geno.shares.add_interest_transaction")
    def test_interest_transactions_execute_one_of_each_type(self, mock_add_transaction):
        Share.objects.all().update(date_end=datetime.date(2000, 1, 1))
        share_date = datetime.date(datetime.datetime.now().year - 1, 1, 1)
        adr = self.addresses[0]
        Share.objects.create(
            name=adr,
            share_type=self.loan,
            date=share_date,
            value=10000,
            state="bezahlt",
        )
        Share.objects.create(
            name=adr,
            share_type=self.loan_special,
            date=share_date,
            value=20000,
            state="bezahlt",
        )
        Share.objects.create(
            name=adr,
            share_type=self.deposit,
            date=share_date,
            value=5000,
            state="bezahlt",
        )
        ret = geno.shares.create_interest_transactions_execute(self.end_of_prev_year)
        self.assertEqual(mock_add_transaction.call_count, 3)
        mock_add_transaction.assert_any_call(
            ANY,
            self.end_of_prev_year,
            adr,
            "Darlehen",
            1.0,
            0.01 * 10000,
            ANY,
            ANY,
            Account.from_settings(AccountKey.INTEREST_LOAN),
            Account.from_settings(AccountKey.SHARES_INTEREST),
            Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
        )
        mock_add_transaction.assert_any_call(
            ANY,
            self.end_of_prev_year,
            adr,
            "Darlehen",
            1.5,
            0.015 * 20000,
            ANY,
            ANY,
            Account.from_settings(AccountKey.INTEREST_LOAN),
            Account.from_settings(AccountKey.SHARES_INTEREST),
            Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
        )
        mock_add_transaction.assert_any_call(
            ANY,
            self.end_of_prev_year,
            adr,
            "Depositenkasse",
            0.75,
            0.0075 * 5000,
            ANY,
            ANY,
            Account.from_settings(AccountKey.INTEREST_DEPOSIT),
            Account.from_settings(AccountKey.SHARES_DEPOSIT),
            Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
        )
        deposit_interest_share = Share.objects.get(
            name=adr, share_type=self.deposit, is_interest_credit=True, state="bezahlt"
        )
        self.assertEqual(deposit_interest_share.date, self.end_of_prev_year)
        self.assertEqual(deposit_interest_share.quantity, 1)
        interest = 5000 * 0.0075
        tax = Decimal(self.tax_rate * interest)
        tax = tax.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
        self.assertEqual(deposit_interest_share.value, Decimal(interest) - tax)
        self.assertEqual(
            deposit_interest_share.note,
            f"Bruttozinsen 0.75% Depositenkasse {self.end_of_prev_year.year}",
        )
        self.assertEqual(ret[-2], {"info": "Transaktionen in Buchhaltung GESPEICHERT!"})
        self.assertEqual(ret[-1], {"info": "Zins-Beteiligungen GESPEICHERT!"})

    def test_add_interest_transaction_with_tax(self):
        interest = 0.005 * 100_000
        tax = Decimal(self.tax_rate * interest)
        pay = Decimal(interest) - tax
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            ret = geno.shares.add_interest_transaction(
                book,
                self.end_of_prev_year,
                self.addresses[0],
                "Test-Name",
                0.5,
                interest,
                tax,
                pay,
                Account.from_settings(AccountKey.INTEREST_DEPOSIT),
                Account.from_settings(AccountKey.SHARES_DEPOSIT),
                Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
            )
            self.assertEqual(ret, "Zinsgutschrift Test-Name: 500.00 (VSt. 175.00 -> Netto 325.00)")
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(len(tr.splits), 3)
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.INTEREST_DEPOSIT):
                    self.assertEqual(split.amount, 500)
                elif split.account == Account.from_settings(AccountKey.SHARES_DEPOSIT):
                    self.assertEqual(split.amount, -325)
                elif split.account == Account.from_settings(AccountKey.SHARES_INTEREST_TAX):
                    self.assertEqual(split.amount, -175)
                else:
                    raise ValueError("Unknown account")
            self.assertEqual(tr.date, self.end_of_prev_year)
            self.assertEqual(
                tr.description,
                f"Zins 0.50% auf Test-Name {self.end_of_prev_year.year} Muster, Hans",
            )

    def test_add_interest_transaction_without_tax(self):
        interest = 0.005 * 10_000
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            ret = geno.shares.add_interest_transaction(
                book,
                self.end_of_prev_year,
                self.addresses[0],
                "Test-Name2",
                0.5,
                interest,
                0,
                interest,
                Account.from_settings(AccountKey.INTEREST_DEPOSIT),
                Account.from_settings(AccountKey.SHARES_DEPOSIT),
                Account.from_settings(AccountKey.SHARES_INTEREST_TAX),
            )
            self.assertEqual(ret, "Zinsgutschrift Test-Name2: 50.00")
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(len(tr.splits), 2)
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.INTEREST_DEPOSIT):
                    self.assertEqual(split.amount, 50)
                elif split.account == Account.from_settings(AccountKey.SHARES_DEPOSIT):
                    self.assertEqual(split.amount, -50)
                else:
                    raise ValueError("Unknown account")
            self.assertEqual(tr.date, self.end_of_prev_year)
            self.assertEqual(
                tr.description,
                f"Zins 0.50% auf Test-Name2 {self.end_of_prev_year.year} Muster, Hans",
            )
