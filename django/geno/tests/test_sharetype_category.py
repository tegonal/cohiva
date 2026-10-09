"""
Tests for ShareType category and flag-based behavior.

These tests verify that the codebase correctly uses ShareType.category
and behavior flags instead of hardcoded name lookups.
"""

from datetime import date

from django.test import TestCase

from geno.models import (
    Address,
    Member,
    Share,
    ShareType,
    ShareTypeCategory,
)


class ShareTypeCategoryTests(TestCase):
    """Tests for ShareType category-based behavior."""

    def test_share_type_category_choices(self):
        """ShareTypeCategory has the expected choices."""
        categories = dict(ShareTypeCategory.choices)
        self.assertIn("share", categories)
        self.assertIn("loan", categories)
        self.assertIn("deposit", categories)
        self.assertIn("mortgage", categories)
        self.assertIn("donation", categories)
        self.assertIn("special_loan", categories)

    def test_share_type_creation_with_category(self):
        """ShareType can be created with a category."""
        st = ShareType.objects.create(
            name="Test Share",
            category=ShareTypeCategory.SHARE,
            membership_type="all",
        )
        self.assertEqual(st.category, ShareTypeCategory.SHARE)
        self.assertEqual(st.membership_type, "all")
        self.assertFalse(st.is_interest_bearing)

    def test_share_type_loan_with_interest(self):
        """Loan share type can be marked as interest-bearing."""
        st = ShareType.objects.create(
            name="Test Loan",
            category=ShareTypeCategory.LOAN,
            is_interest_bearing=True,
            requires_due_date=True,
            standard_interest=2.5,
        )
        self.assertTrue(st.is_interest_bearing)
        self.assertTrue(st.requires_due_date)
        self.assertEqual(st.standard_interest, 2.5)

    def test_share_type_excluded_from_reports(self):
        """ShareType can be excluded from reports."""
        st = ShareType.objects.create(
            name="Test Mortgage",
            category=ShareTypeCategory.MORTGAGE,
            is_excluded_from_reports=True,
            is_excluded_from_mailings=True,
        )
        self.assertTrue(st.is_excluded_from_reports)
        self.assertTrue(st.is_excluded_from_mailings)

    def test_share_type_membership_type_choices(self):
        """ShareType membership_type has the expected choices."""
        st = ShareType.objects.create(
            name="Test Member Share",
            category=ShareTypeCategory.SHARE,
            membership_type="flag_02",
        )
        self.assertEqual(st.membership_type, "flag_02")

    def test_share_type_voluntary_membership(self):
        """Voluntary share type has empty membership_type."""
        st = ShareType.objects.create(
            name="Test Voluntary",
            category=ShareTypeCategory.SHARE,
            membership_type="",
        )
        self.assertEqual(st.membership_type, "")


class ShareTypeBehaviorTests(TestCase):
    """Tests for behavior based on ShareType properties."""

    @classmethod
    def setUpTestData(cls):
        cls.address = Address.objects.create(name="Muster", first_name="Hans")
        cls.member = Member.objects.create(name=cls.address, date_join=date(2020, 1, 1))

        cls.share_type_share = ShareType.objects.create(
            name="Anteilschein",
            category=ShareTypeCategory.SHARE,
            membership_type="all",
        )
        cls.share_type_loan = ShareType.objects.create(
            name="Darlehen verzinst",
            category=ShareTypeCategory.LOAN,
            is_interest_bearing=True,
            requires_due_date=True,
            standard_interest=1.0,
        )
        cls.share_type_deposit = ShareType.objects.create(
            name="Depositenkasse",
            category=ShareTypeCategory.DEPOSIT,
            is_interest_bearing=True,
            standard_interest=0.75,
        )
        cls.share_type_donation = ShareType.objects.create(
            name="Entwicklungsbeitrag",
            category=ShareTypeCategory.DONATION,
        )
        cls.share_type_mortgage = ShareType.objects.create(
            name="Hypothek",
            category=ShareTypeCategory.MORTGAGE,
            is_excluded_from_reports=True,
            is_excluded_from_mailings=True,
        )

    def test_filter_by_category(self):
        """Shares can be filtered by ShareType category."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_share,
            payment_date=date(2021, 1, 1),
            value=1000,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_loan,
            payment_date=date(2021, 1, 1),
            value=5000,
            duration=5,
        )

        shares = Share.objects.filter(share_type__category=ShareTypeCategory.SHARE)
        self.assertEqual(shares.count(), 1)
        self.assertEqual(shares.first().share_type, self.share_type_share)

        loans = Share.objects.filter(share_type__category=ShareTypeCategory.LOAN)
        self.assertEqual(loans.count(), 1)
        self.assertEqual(loans.first().share_type, self.share_type_loan)

    def test_filter_by_is_interest_bearing(self):
        """Shares can be filtered by is_interest_bearing flag."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_share,
            payment_date=date(2021, 1, 1),
            value=1000,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_loan,
            payment_date=date(2021, 1, 1),
            value=5000,
            duration=5,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_deposit,
            payment_date=date(2021, 1, 1),
            value=3000,
        )

        interest_bearing = Share.objects.filter(share_type__is_interest_bearing=True)
        self.assertEqual(interest_bearing.count(), 2)

    def test_filter_by_requires_due_date(self):
        """Shares can be filtered by requires_due_date flag."""
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_loan,
            payment_date=date(2021, 1, 1),
            value=5000,
            duration=5,
        )
        Share.objects.create(
            name=self.address,
            share_type=self.share_type_share,
            payment_date=date(2021, 1, 1),
            value=1000,
        )

        requiring_due_date = Share.objects.filter(share_type__requires_due_date=True)
        self.assertEqual(requiring_due_date.count(), 1)
        self.assertEqual(requiring_due_date.first().share_type, self.share_type_loan)

    def test_filter_by_is_excluded_from_reports(self):
        """ShareTypes can be filtered by is_excluded_from_reports."""
        excluded = ShareType.objects.filter(is_excluded_from_reports=True)
        self.assertEqual(excluded.count(), 1)
        self.assertEqual(excluded.first(), self.share_type_mortgage)

    def test_donation_category(self):
        """Donation share type uses DONATION category."""
        self.assertEqual(self.share_type_donation.category, ShareTypeCategory.DONATION)

    def test_membership_type_flag_matching(self):
        """ShareType membership_type can be matched against member flags."""
        # Create share types with different membership_type values
        st_flag_02 = ShareType.objects.create(
            name="Flag 02 Share",
            category=ShareTypeCategory.SHARE,
            membership_type="flag_02",
        )
        st_not_flag_02 = ShareType.objects.create(
            name="Not Flag 02 Share",
            category=ShareTypeCategory.SHARE,
            membership_type="not_flag_02",
        )
        st_all = ShareType.objects.create(
            name="All Members Share",
            category=ShareTypeCategory.SHARE,
            membership_type="all",
        )

        # Member without flag_02
        self.assertFalse(self.member.flag_02)

        # Check that membership_type values are stored correctly
        self.assertEqual(st_flag_02.membership_type, "flag_02")
        self.assertEqual(st_not_flag_02.membership_type, "not_flag_02")
        self.assertEqual(st_all.membership_type, "all")

    def test_multiple_share_types_per_category(self):
        """Multiple ShareTypes can exist in the same category."""
        st1 = ShareType.objects.create(
            name="Share Type 1",
            category=ShareTypeCategory.SHARE,
            membership_type="all",
        )
        st2 = ShareType.objects.create(
            name="Share Type 2",
            category=ShareTypeCategory.SHARE,
            membership_type="",
        )

        share_types = list(ShareType.objects.filter(category=ShareTypeCategory.SHARE))
        self.assertIn(st1, share_types)
        self.assertIn(st2, share_types)
        self.assertIn(self.share_type_share, share_types)

    def test_share_type_ordering(self):
        """ShareTypes are ordered by display_order and name."""
        st1 = ShareType.objects.create(
            name="Z Last",
            category=ShareTypeCategory.SHARE,
            display_order=1,
        )
        st2 = ShareType.objects.create(
            name="A First",
            category=ShareTypeCategory.SHARE,
            display_order=0,
        )

        share_types = list(ShareType.objects.filter(category=ShareTypeCategory.SHARE))
        # A First should come before Z Last due to display_order
        self.assertLess(share_types.index(st2), share_types.index(st1))
