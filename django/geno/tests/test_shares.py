import datetime
from decimal import ROUND_HALF_UP, Decimal
from unittest.mock import ANY, patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError

import geno.shares
from finance.accounting import Account, AccountingManager, AccountKey

from ..models import Address, Building, Contract, Share, ShareType
from .base import GenoAdminTestCase, MockDate


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
        today = datetime.date.today()
        contract = Contract.objects.create(date=today)
        building = Building.objects.create()
        address = Address.objects.create()
        sharetype = ShareType.objects.create()

        # Check model constraint
        constraint_name = "geno_share_attached_to_building_or_contract"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Share.objects.create(
                name=address,
                payment_date=today,
                share_type=sharetype,
                value=200,
                attached_to_contract=contract,
                attached_to_building=building,
            )

        # Check form validation
        with self.assertRaises(ValidationError):
            share = Share(
                name=address,
                payment_date=today,
                share_type=sharetype,
                value=200,
                attached_to_contract=contract,
                attached_to_building=building,
            )
            share.clean()

    def test_share_bezahlt_no_repayment_date(self):
        share = Share(
            name=self.addresses[0],
            share_type=self.loan,
            payment_date=datetime.date(2020, 1, 1),
            value=1000,
        )
        self.assertIn("bezahlt", str(share))

    def test_share_bezahlt_future_repayment_date(self):
        share = Share(
            name=self.addresses[0],
            share_type=self.loan,
            payment_date=datetime.date(2020, 1, 1),
            repayment_date=datetime.date(2099, 12, 31),
            value=1000,
        )
        self.assertIn("bezahlt", str(share))

    def test_share_past_repayment_date(self):
        share = Share(
            name=self.addresses[0],
            share_type=self.loan,
            payment_date=datetime.date(2020, 1, 1),
            repayment_date=datetime.date(2021, 12, 31),
            value=1000,
        )
        self.assertIn("zurückgezahlt", str(share))
        self.assertNotIn("bezahlt", str(share))

    def test_share_future_payment_date(self):
        share = Share(
            name=self.addresses[0],
            share_type=self.loan,
            payment_date=datetime.date(2030, 1, 1),
            value=1000,
        )
        self.assertIn("gefordert", str(share))

    @patch("geno.shares.create_interest_transactions_execute")
    def test_create_interest_transactions(self, mock_execute):
        ret = geno.shares.create_interest_transactions()
        mock_execute.assert_called_once_with(self.end_of_prev_year)
        self.assertEqual(ret, [])

    @patch("geno.shares.create_interest_transactions_execute")
    def test_create_interest_transactions_with_warning(self, mock_execute):
        Share.objects.create(
            name=self.addresses[1],
            payment_date=self.end_of_prev_year,
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
        Share.objects.all().update(repayment_date=datetime.date(2000, 1, 1))
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
        Share.objects.all().update(repayment_date=datetime.date(2000, 1, 1))
        share_date = datetime.date(datetime.datetime.now().year - 1, 1, 1)
        adr = self.addresses[0]
        Share.objects.create(
            name=adr,
            share_type=self.loan,
            payment_date=share_date,
            value=10000,
        )
        Share.objects.create(
            name=adr,
            share_type=self.loan_special,
            payment_date=share_date,
            value=20000,
        )
        Share.objects.create(
            name=adr,
            share_type=self.deposit,
            payment_date=share_date,
            value=5000,
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
            name=adr,
            share_type=self.deposit,
            is_interest_credit=True,
        )
        self.assertEqual(deposit_interest_share.payment_date, self.end_of_prev_year)
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


class ShareStateTests(GenoAdminTestCase):
    """
    Tests for Share.state based on payment_date and repayment_date.
    We mock 'django.utils.timezone.now' so the tests are deterministic.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TODAY = datetime.date(2025, 1, 15)
        cls.YESTERDAY = cls.TODAY - datetime.timedelta(days=1)
        cls.TOMORROW = cls.TODAY + datetime.timedelta(days=1)
        cls.LAST_WEEK = cls.TODAY - datetime.timedelta(days=7)
        cls.NEXT_WEEK = cls.TODAY + datetime.timedelta(days=7)
        cls.STATE_REQUESTED = "gefordert"
        cls.STATE_PAID = "bezahlt"
        cls.STATE_REPAID = "zurückgezahlt"

    def _create_share(self, **kwargs):
        return Share.objects.create(
            name=self.addresses[0], share_type=self.sharetypes[0], value=200, **kwargs
        )

    @patch("geno.models.datetime.date", MockDate)
    def _assert_state(self, share, expected_state):
        """Helper that patches datetime.date.today() so that Share.payment_state sees fixed 'today'"""
        self.assertEqual(share.payment_state, expected_state)

    # --------------------------------------------------------------------- #
    # REQUESTED
    # --------------------------------------------------------------------- #
    def test_state_requested_when_payment_date_is_null(self):
        """Only effective_from is set -> no payment has been made."""
        share = self._create_share(
            payment_date=None,
            effective_from=self.TOMORROW,
        )
        self._assert_state(share, self.STATE_REQUESTED)

    def test_state_requested_when_payment_date_is_in_future(self):
        """Payment is scheduled but has not happened yet."""
        share = self._create_share(
            payment_date=self.TOMORROW,
            effective_from=self.YESTERDAY,
        )
        self._assert_state(share, self.STATE_REQUESTED)

    def test_state_requested_both_dates_null(self):
        """Only effective_from is provided (satisfying the non-null rule)."""
        share = self._create_share(
            payment_date=None,
            repayment_date=None,
            effective_from=self.TODAY,
            effective_until=self.NEXT_WEEK,
        )
        self._assert_state(share, self.STATE_REQUESTED)

    # --------------------------------------------------------------------- #
    # PAID
    # --------------------------------------------------------------------- #
    def test_state_paid_when_payment_in_past(self):
        share = self._create_share(
            payment_date=self.YESTERDAY,
            repayment_date=None,
        )
        self._assert_state(share, self.STATE_PAID)

    def test_state_paid_when_payment_is_today(self):
        share = self._create_share(
            payment_date=self.TODAY,
            repayment_date=self.TOMORROW,
        )
        self._assert_state(share, self.STATE_PAID)

    def test_state_paid_not_repaid_yet(self):
        share = self._create_share(
            payment_date=self.LAST_WEEK,
            repayment_date=self.TOMORROW,
        )
        self._assert_state(share, self.STATE_PAID)

    # --------------------------------------------------------------------- #
    # REPAID
    # --------------------------------------------------------------------- #
    def test_state_repaid_when_repayment_in_past(self):
        share = self._create_share(
            payment_date=self.LAST_WEEK,
            repayment_date=self.YESTERDAY,
        )
        self._assert_state(share, self.STATE_REPAID)

    def test_state_repaid_when_repayment_is_today(self):
        share = self._create_share(
            payment_date=self.YESTERDAY,
            repayment_date=self.TODAY,
        )
        self._assert_state(share, self.STATE_REPAID)

    def test_state_repaid_takes_precedence_over_paid(self):
        """If both conditions met on the same day, repaid wins."""
        share = self._create_share(
            payment_date=self.TODAY,
            repayment_date=self.TODAY,
        )
        self._assert_state(share, self.STATE_REPAID)

    def test_state_repaid_even_without_payment_date(self):
        """
        Edge case: repayment_date exists in the past but payment_date is None.
        According to the literal logic 'there was a repayment in the past' ->
        state should still be repaid.
        """
        share = self._create_share(
            payment_date=None,
            effective_from=self.LAST_WEEK,
            repayment_date=self.YESTERDAY,
        )
        self._assert_state(share, self.STATE_REPAID)


class GetActiveSharesTests(GenoAdminTestCase):
    """
    Tests for Share.get_active(date=reference_date) and
    Share.get_active_in_period(period_start=..., period_end=...).

    Effective boundaries:
        start = effective_from or payment_date
        end   = effective_until or repayment_date
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.D1 = datetime.date(2020, 1, 1)  # far past
        cls.D2 = datetime.date(2020, 6, 10)  # past
        cls.D3 = datetime.date(2020, 6, 15)  # present (reference only)
        cls.D4 = datetime.date(2020, 6, 20)  # future
        cls.D5 = datetime.date(2020, 12, 31)  # far future
        ## Remove the default test shares, we don't need them here
        Share.objects.all().delete()

    def _create_share(self, **kwargs):
        return Share.objects.create(
            name=self.addresses[0], share_type=self.sharetypes[0], value=200, **kwargs
        )

    # --------------------------------------------------------------------- #
    # SINGLE DATE
    # --------------------------------------------------------------------- #
    def test_single_date_active_inside_period(self):
        share = self._create_share(
            effective_from=self.D2,
            effective_until=self.D4,
        )
        result = Share.get_active(date=self.D3)
        self.assertIn(share, result)

    def test_single_date_active_on_start_boundary(self):
        share = self._create_share(
            effective_from=self.D3,
            effective_until=self.D4,
        )
        result = Share.get_active(date=self.D3)
        self.assertIn(share, result)

    def test_single_date_active_on_end_boundary_is_excluded(self):
        share = self._create_share(
            effective_from=self.D2,
            effective_until=self.D3,
        )
        result = Share.get_active(date=self.D3)
        self.assertNotIn(share, result)

    def test_single_date_active_on_end_boundary_is_excluded_with_later_repayment_date(self):
        share = self._create_share(
            effective_from=self.D2,
            effective_until=self.D3,
            repayment_date=self.D4,
        )
        result = Share.get_active(date=self.D3)
        self.assertNotIn(share, result)

    def test_single_date_inactive_before_start(self):
        share = self._create_share(
            effective_from=self.D4,
            effective_until=self.D5,
        )
        result = Share.get_active(date=self.D3)
        self.assertNotIn(share, result)

    def test_single_date_inactive_after_end(self):
        share = self._create_share(
            effective_from=self.D1,
            effective_until=self.D2,
        )
        result = Share.get_active(date=self.D3)
        self.assertNotIn(share, result)

    def test_single_date_active_open_ended(self):
        share = self._create_share(
            effective_from=self.D3,
            effective_until=None,
            repayment_date=None,
        )
        result = Share.get_active(date=self.D5)
        self.assertIn(share, result)

    def test_single_date_inactive_open_ended_before_start(self):
        share = self._create_share(
            effective_from=self.D4,
            effective_until=None,
        )
        result = Share.get_active(date=self.D3)
        self.assertNotIn(share, result)

    def test_single_date_uses_payment_date_fallback(self):
        """effective_from is null, so payment_date drives the start boundary."""
        share = self._create_share(
            payment_date=self.D2,
            effective_from=None,
            repayment_date=self.D4,
            effective_until=None,
        )
        result = Share.get_active(date=self.D3)
        self.assertIn(share, result)

    def test_single_date_uses_repayment_date_fallback(self):
        """effective_until is null, so repayment_date drives the end boundary."""
        share = self._create_share(
            effective_from=self.D2,
            effective_until=None,
            repayment_date=self.D4,
        )
        result = Share.get_active(date=self.D3)
        self.assertIn(share, result)

    def test_single_date_ignores_payment_dates_when_effective_is_set(self):
        """when effective dates are set the payment/repayment dates should have no effect."""
        share = self._create_share(
            payment_date=self.D1,
            effective_from=self.D2,
            effective_until=self.D4,
            repayment_date=self.D5,
        )
        result = Share.get_active(date=self.D1 + datetime.timedelta(days=1))
        self.assertNotIn(share, result)
        result = Share.get_active(date=self.D4 + datetime.timedelta(days=1))
        self.assertNotIn(share, result)

    # --------------------------------------------------------------------- #
    # DATE RANGE - overlap variations
    # --------------------------------------------------------------------- #
    def test_range_share_fully_contains_reference(self):
        share = self._create_share(effective_from=self.D1, effective_until=self.D5)
        result = Share.get_active_in_period(period_start=self.D2, period_end=self.D4)
        self.assertIn(share, result)

    def test_range_reference_fully_contains_share(self):
        share = self._create_share(effective_from=self.D2, effective_until=self.D4)
        result = Share.get_active_in_period(period_start=self.D1, period_end=self.D5)
        self.assertIn(share, result)

    def test_range_reference_overlaps_start_of_share(self):
        share = self._create_share(effective_from=self.D3, effective_until=self.D5)
        result = Share.get_active_in_period(period_start=self.D1, period_end=self.D3)
        self.assertIn(share, result)

    def test_range_reference_does_not_overlap_start_of_share_when_end_is_exclusive(self):
        share = self._create_share(effective_from=self.D3, effective_until=self.D5)
        result = Share.get_active_in_period(
            period_start=self.D1, period_end=self.D3, exclude_period_end=True
        )
        self.assertNotIn(share, result)

    def test_range_reference_overlaps_start_of_share_when_end_is_exclusive(self):
        share = self._create_share(effective_from=self.D3, effective_until=self.D5)
        result = Share.get_active_in_period(
            period_start=self.D1,
            period_end=self.D3 + datetime.timedelta(days=1),
            exclude_period_end=True,
        )
        self.assertIn(share, result)

    def test_range_reference_overlaps_end_of_share(self):
        share = self._create_share(effective_from=self.D1, effective_until=self.D3)
        result = Share.get_active_in_period(period_start=self.D3, period_end=self.D5)
        self.assertIn(share, result)

    def test_range_no_overlap_reference_before_share(self):
        share = self._create_share(effective_from=self.D3, effective_until=self.D5)
        result = Share.get_active_in_period(period_start=self.D1, period_end=self.D2)
        self.assertNotIn(share, result)

    def test_range_no_overlap_reference_after_share(self):
        share = self._create_share(effective_from=self.D1, effective_until=self.D2)
        result = Share.get_active_in_period(period_start=self.D3, period_end=self.D5)
        self.assertNotIn(share, result)

    def test_range_no_overlap_adjacent_days(self):
        """Share ends D2, reference starts D3 -> no common day."""
        share = self._create_share(effective_from=self.D1, effective_until=self.D2)
        result = Share.get_active_in_period(period_start=self.D3, period_end=self.D4)
        self.assertNotIn(share, result)

    def test_range_active_open_ended(self):
        share = self._create_share(effective_from=self.D4, effective_until=None)
        result = Share.get_active_in_period(period_start=self.D5, period_end=self.D5)
        self.assertIn(share, result)

    def test_range_inactive_open_ended_before_start(self):
        share = self._create_share(effective_from=self.D4, effective_until=None)
        result = Share.get_active_in_period(period_start=self.D1, period_end=self.D2)
        self.assertNotIn(share, result)

    def test_range_single_day_share_inside_range(self):
        share = self._create_share(effective_from=self.D3, effective_until=self.D3)
        result = Share.get_active_in_period(period_start=self.D2, period_end=self.D4)
        self.assertIn(share, result)

    def test_range_single_day_reference_overlaps(self):
        share = self._create_share(effective_from=self.D2, effective_until=self.D4)
        result = Share.get_active_in_period(period_start=self.D3, period_end=self.D3)
        self.assertIn(share, result)

    # --------------------------------------------------------------------- #
    # DATE RANGE - precedence of effective_* over payment/repayment
    # --------------------------------------------------------------------- #
    def test_range_effective_from_takes_precedence_over_payment_date(self):
        """
        If effective_from is earlier than payment_date, the share is active
        for the whole effective period, not just from the payment date.
        """
        share = self._create_share(
            effective_from=self.D1,  # earlier
            payment_date=self.D4,  # later
            effective_until=self.D5,
            repayment_date=None,
        )
        result = Share.get_active_in_period(period_start=self.D2, period_end=self.D2)
        self.assertIn(share, result)

    def test_range_effective_until_takes_precedence_over_repayment_date(self):
        """
        If effective_until is later than repayment_date, the share remains
        active until effective_until.
        """
        share = self._create_share(
            effective_from=self.D1,
            payment_date=self.D1,
            effective_until=self.D5,  # later
            repayment_date=self.D2,  # earlier
        )
        # Reference falls between repayment_date and effective_until
        result = Share.get_active_in_period(period_start=self.D3, period_end=self.D3)
        self.assertIn(share, result)

    def test_range_payment_fallback_when_effective_null(self):
        """When effective dates are absent, payment/repayment are used."""
        share = self._create_share(
            effective_from=None,
            payment_date=self.D2,
            effective_until=None,
            repayment_date=self.D4,
        )
        result = Share.get_active_in_period(period_start=self.D3, period_end=self.D3)
        self.assertIn(share, result)

    # =====================================================================
    # MIXED / BULK SCENARIOS – many shares, only some match
    # =====================================================================

    def test_range_returns_empty_when_no_shares_overlap(self):
        """DB contains only inactive shares → queryset should be empty."""
        s1 = self._create_share(
            effective_from=self.D1,
            effective_until=self.D2,
        )
        s2 = self._create_share(
            payment_date=self.D4,
            effective_from=None,
            repayment_date=None,
            effective_until=None,
        )
        result = list(Share.get_active(date=self.D3))
        self.assertNotIn(s1, result)
        self.assertNotIn(s2, result)
        self.assertEqual(len(result), 0)

    def test_range_excludes_neighbors_but_keeps_active(self):
        """
        One expired share, one active share, one future share.
        Only the active one should be returned.
        """
        expired = self._create_share(
            effective_from=self.D1,
            effective_until=self.D2,
        )
        active = self._create_share(
            effective_from=self.D2,
            effective_until=self.D4,
        )
        future = self._create_share(
            effective_from=self.D4,
            effective_until=self.D5,
        )
        result = list(Share.get_active(date=self.D3))
        self.assertNotIn(expired, result)
        self.assertIn(active, result)
        self.assertNotIn(future, result)
        self.assertEqual(len(result), 1)

    def test_range_excluded_when_effective_dates_create_gap(self):
        """
        Two back-to-back shares. The first ends exactly on D2.
        Querying from D3 onwards should exclude the first.
        """
        first = self._create_share(
            effective_from=self.D1,
            effective_until=self.D2,
        )
        second = self._create_share(
            effective_from=self.D3,
            effective_until=self.D5,
        )
        result = list(Share.get_active_in_period(period_start=self.D3, period_end=self.D4))
        self.assertNotIn(first, result)
        self.assertIn(second, result)
