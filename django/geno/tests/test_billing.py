import datetime
import os
from unittest.mock import patch

import geno.billing
import geno.tests.data as geno_testdata
from finance.accounting import Account, AccountingManager, AccountKey
from geno.billing import (
    DuplicateInvoiceError,
    InvoiceCreationError,
    add_invoice_obj,
    build_structured_qrbill_address,
    create_qrbill,
    get_reference_nr,
)
from geno.models import (
    Address,
    Contract,
    Invoice,
    InvoiceCategory,
    Member,
    MemberAttribute,
    MemberAttributeType,
    Share,
    ShareType,
)

from .base import GenoAdminTestCase


def add_invoice_exception_generator(*args, **kwargs):
    if kwargs["month"] == 4:
        raise InvoiceCreationError("Test Exception")


class TestBilling(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)
        cls.share_type_member_share = ShareType.objects.get(name="Anteilschein")
        cls.share_type_loan = ShareType.objects.get(name="Darlehen verzinst")
        cls.share_type_deposit = ShareType.objects.get(name="Depositenkasse")
        cls.member_attribute_2001 = MemberAttributeType.objects.create(
            name="Mitgliederbeitrag 2001"
        )

    @patch(
        "geno.billing.create_monthly_invoices",
        return_value=(2, ["Invoice1", "Invoice2"], [], ["Message"]),
    )
    def test_create_invoices_one_contract(self, mock_monthly_invoices):
        ret = geno.billing.create_invoices()
        self.assertEqual(mock_monthly_invoices.call_count, 1)
        self.assertEqual(ret[0]["objects"][0]["items"][0], "Message")
        self.assertEqual(ret[-1]["info"], "2 Rechnungen für 1 Vertrag")

    @patch("geno.billing.create_monthly_invoices", return_value=(2, [], [], []))
    def test_create_invoices_multiple_contracts(self, mock_monthly_invoices):
        Contract.objects.create(date=datetime.date(2001, 1, 1), state="unterzeichnet")
        ret = geno.billing.create_invoices()
        self.assertEqual(mock_monthly_invoices.call_count, 2)
        self.assertEqual(ret[-1]["info"], "4 Rechnungen für 2 Verträge")

    @patch(
        "geno.billing.create_monthly_invoices", return_value=("String", [], [], ["Unused Message"])
    )
    def test_create_invoices_return_string(self, mock_monthly_invoices):
        Contract.objects.create(date=datetime.date(2001, 1, 1), state="unterzeichnet")
        ret = geno.billing.create_invoices()
        self.assertEqual(mock_monthly_invoices.call_count, 1)
        self.assertEqual(ret, "String")

    def test_create_invoices_empty_contract_count(self):
        messages = geno.billing.create_invoices(reference_date=datetime.date(2001, 6, 1))
        self.assertEqual(messages[-1]["info"], "3 Rechnungen für 1 Vertrag")
        contract = Contract.objects.create(date=datetime.date(2001, 1, 1), state="unterzeichnet")
        messages2 = geno.billing.create_invoices(reference_date=datetime.date(2001, 6, 1))
        self.assertEqual(messages2[-1]["info"], "3 Rechnungen für 1 Vertrag")
        contract.rental_units.set([self.rentalunits[3]])
        contract.contractors.set([self.addresses[3]])
        messages3 = geno.billing.create_invoices(reference_date=datetime.date(2001, 6, 1))
        self.assertEqual(messages3[-1]["info"], "9 Rechnungen für 2 Verträge")

    def test_create_invoices_contract_without_address(self):
        contract = Contract.objects.create(date=datetime.date(2001, 1, 1), state="unterzeichnet")
        contract.rental_units.set([self.rentalunits[3]])
        messages = geno.billing.create_invoices(reference_date=datetime.date(2001, 6, 1))
        self.assertIn("Vertrag hat keine Vertragspartner/Adresse", messages[0]["info"])
        self.assertEqual(messages[1]["info"], "VERARBEITUNG ABGEBROCHEN!")
        self.assertEqual(messages[1]["variant"], "error")
        self.assertEqual(messages[-1]["info"], "3 Rechnungen für 1 Vertrag")

    @patch("geno.billing.add_invoice", wraps=add_invoice_exception_generator)
    def test_create_invoices_stop_on_exception(self, mock_add_invoice):
        contract = Contract.objects.create(date=datetime.date(2001, 1, 1), state="unterzeichnet")
        contract.rental_units.set([self.rentalunits[3]])
        contract.contractors.set([self.addresses[3]])
        messages = geno.billing.create_invoices(reference_date=datetime.date(2001, 6, 1))
        self.assertIn("Test Exception", messages[0]["info"])
        self.assertEqual(messages[-1]["info"], "VERARBEITUNG ABGEBROCHEN!")

    def test_create_invoices_with_linked_billing_contract(self):
        contract = Contract.objects.create(
            date=datetime.date(2001, 1, 1),
            state="unterzeichnet",
            billing_contract=self.contracts[0],
        )
        contract.rental_units.set([self.rentalunits[3]])
        contract.contractors.set([self.addresses[3]])
        messages = geno.billing.create_invoices(reference_date=datetime.date(2001, 6, 1))
        self.assertEqual(messages[-1]["info"], "9 Rechnungen für 2 Verträge")
        self.assertEqual(messages[-1]["variant"], "info")
        self.assertEqual(
            messages[1]["objects"][1]["label"], "Platzhalter-Monatsrechnungen hinzugefügt"
        )
        self.assertIn(
            "6.2001: G002 Gewerbe (Musterweg 1) "
            "[WBG Test, Ernst Bitterer] (Rechnungs-Vertrag: 001a Wohnung (Musterweg 1)/001b "
            "Wohnung (Musterweg 1) [Anna Muster/Hans Muster])",
            messages[1]["objects"][1]["items"],
        )

    @patch("geno.billing.add_invoice")
    def test_create_monthly_invoices_none(self, mock_add_invoice):
        with AccountingManager(book_type_id="dum") as book:
            contract = self.contracts[0]
            date = datetime.date(2001, 3, 1)
            inv_cat = InvoiceCategory.objects.get(
                reference_id=10
            )  # name="Mietzins wiederkehrend")
            options = {
                "download_only": None,
                "single_contract": None,
                "dry_run": True,
            }
            count, regular_invoices, placeholder_invoices, email_messages = (
                geno.billing.create_monthly_invoices(book, contract, date, inv_cat, options)
            )
            mock_add_invoice.assert_not_called()
            self.assertEqual(count, 0)
            self.assertEqual(len(email_messages), 0)
            self.assertEqual(len(regular_invoices), 0)
            self.assertEqual(len(placeholder_invoices), 0)

    @patch("geno.billing.add_invoice")
    def test_create_monthly_invoices_one_month(self, mock_add_invoice):
        with AccountingManager(book_type_id="dum") as book:
            contract = self.contracts[0]
            date = datetime.date(2001, 4, 1)
            inv_cat = InvoiceCategory.objects.get(
                reference_id=10
            )  # name="Mietzins wiederkehrend")
            options = {
                "download_only": None,
                "single_contract": None,
                "dry_run": True,
            }
            count, regular_invoices, placeholder_invoices, email_messages = (
                geno.billing.create_monthly_invoices(book, contract, date, inv_cat, options)
            )
            self.assertEqual(mock_add_invoice.call_count, 2)
            self.assertEqual(count, 1)
            self.assertEqual(len(email_messages), 1)
            self.assertIn("Vorschau", email_messages[0])
            self.assertEqual(len(placeholder_invoices), 0)
            contract_string = "001a/001b für 001a Wohnung (Musterweg 1)/001b Wohnung (Musterweg 1) [Anna Muster/Hans Muster]"
            self.assertEqual(
                regular_invoices[0],
                f"Nettomiete 04.2001 für {contract_string}",
            )
            self.assertEqual(
                regular_invoices[1],
                f"Nebenkosten 04.2001 für {contract_string}",
            )

    @patch("geno.billing.add_invoice")
    def test_create_monthly_invoices_multiple_month(self, mock_add_invoice):
        with AccountingManager(book_type_id="dum") as book:
            contract = self.contracts[0]
            date = datetime.date(2001, 6, 1)
            inv_cat = InvoiceCategory.objects.get(
                reference_id=10
            )  # name="Mietzins wiederkehrend")
            options = {
                "download_only": None,
                "single_contract": None,
                "dry_run": True,
            }
            count, regular_invoices, placeholder_invoices, email_messages = (
                geno.billing.create_monthly_invoices(book, contract, date, inv_cat, options)
            )
            self.assertEqual(mock_add_invoice.call_count, 3 * 2)
            self.assertEqual(count, 3)
            self.assertEqual(len(regular_invoices), 3 * 2)
            self.assertEqual(len(placeholder_invoices), 0)
            self.assertEqual(len(email_messages), 3)

    def test_add_transaction_shares_200(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_shares(book, date, 200, adr)
            share = Share.objects.get(name=adr, date=date, state="bezahlt", value=200)
            self.assertEqual(share.share_type, self.share_type_member_share)
            self.assertEqual(share.quantity, 1)
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(tr.date, date)
            self.assertEqual(tr.description, "1 Anteilschein Muster, Hans")
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.SHARES_MEMBERS):
                    self.assertEqual(split.amount, -200)
                elif split.account == Account.from_settings(AccountKey.SHARES_DEBTOR_MANUAL):
                    self.assertEqual(split.amount, 200)
                else:
                    raise ValueError("Wrong account")

    def test_add_transaction_shares_400(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_shares(book, date, 400, adr)
            share = Share.objects.get(name=adr, date=date, state="bezahlt", value=200)
            self.assertEqual(share.share_type, self.share_type_member_share)
            self.assertEqual(share.quantity, 2)
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(tr.description, "2 Anteilscheine Muster, Hans")
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.SHARES_MEMBERS):
                    self.assertEqual(split.amount, -400)
                elif split.account == Account.from_settings(AccountKey.SHARES_DEBTOR_MANUAL):
                    self.assertEqual(split.amount, 400)
                else:
                    raise ValueError("Wrong account")

    def test_add_transaction_shares_400_clearing(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_shares(book, date, 400, adr, use_clearing=True)
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(tr.description, "2 Anteilscheine Muster, Hans")
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.SHARES_MEMBERS):
                    self.assertEqual(split.amount, -400)
                elif split.account == Account.from_settings(AccountKey.SHARES_CLEARING):
                    self.assertEqual(split.amount, 400)
                else:
                    raise ValueError(f"Wrong account: {split.account}")

    def test_add_transaction_shares_invalid(self):
        with self.assertRaises(ValueError, msg="Share is not a multiple of 200.-!"):
            geno.billing.add_transaction_shares(None, None, 100, None)

    def test_add_transaction_shares_entry_200(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_shares_entry(book, date, 200, adr)
            with self.assertRaises(Share.DoesNotExist):
                Share.objects.get(name=adr, date=date, state="bezahlt", value=200)
            attr = MemberAttribute.objects.get(
                member=Member.objects.get(name=adr),
                date=date,
                attribute_type=self.member_attribute_2001,
            )
            self.assertEqual(attr.value, "Bezahlt (mit Eintritt)")
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(tr.date, date)
            self.assertEqual(tr.description, "0 Anteilscheine und Beitrittsgebühr, Muster, Hans")
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.MEMBER_FEE_ONETIME):
                    self.assertEqual(split.amount, -200)
                elif split.account == Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL):
                    self.assertEqual(split.amount, 200)
                else:
                    raise ValueError(f"Wrong account: {split.account}")

    def test_add_transaction_shares_entry_400(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_shares_entry(book, date, 400, adr)
            share = Share.objects.get(name=adr, date=date, state="bezahlt", value=200)
            self.assertEqual(share.share_type, self.share_type_member_share)
            self.assertEqual(share.quantity, 1)
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            self.assertEqual(tr.description, "1 Anteilschein und Beitrittsgebühr, Muster, Hans")
            for split in tr.splits:
                if split.account in (
                    Account.from_settings(AccountKey.MEMBER_FEE_ONETIME),
                    Account.from_settings(AccountKey.SHARES_MEMBERS),
                ):
                    self.assertEqual(split.amount, -200)
                elif split.account == Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL):
                    self.assertEqual(split.amount, 400)
                else:
                    raise ValueError(f"Wrong account: {split.account}")

    def test_add_transaction_shares_entry_400_clearing(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_shares_entry(book, date, 400, adr, use_clearing=True)
            book.save()
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            for split in tr.splits:
                if split.account in (
                    Account.from_settings(AccountKey.MEMBER_FEE_ONETIME),
                    Account.from_settings(AccountKey.SHARES_MEMBERS),
                ):
                    self.assertEqual(split.amount, -200)
                elif split.account == Account.from_settings(AccountKey.SHARES_CLEARING):
                    self.assertEqual(split.amount, 400)
                else:
                    raise ValueError(f"Wrong account: {split.account}")

    def test_add_transaction_shares_entry_invalid(self):
        with self.assertRaises(ValueError, msg="Betrag ist kein Vielfaches von 200: 100"):
            geno.billing.add_transaction_shares_entry(None, None, 100, None)

    def test_add_transaction_interest_loan(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_interest(book, date, 50, adr, book_to="loan")
            book.save()
            share = Share.objects.get(
                name=adr, date=date, state="bezahlt", value=50, is_interest_credit=True, quantity=1
            )
            self.assertEqual(share.share_type, self.share_type_loan)
            self.assertEqual(share.note, "Anrechnung Darlehenszins an Darlehen")
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.SHARES_LOAN_INTEREST):
                    self.assertEqual(split.amount, -50)
                elif split.account == Account.from_settings(AccountKey.SHARES_INTEREST):
                    self.assertEqual(split.amount, 50)
                else:
                    raise ValueError(f"Wrong account: {split.account}")
            self.assertEqual(tr.description, f"{share.note}, Muster, Hans")

    def test_add_transaction_interest_deposit(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2001, 4, 1)
            adr = self.addresses[0]
            book._db = {}
            geno.billing.add_transaction_interest(book, date, 50, adr, book_to="deposit")
            book.save()
            share = Share.objects.get(
                name=adr, date=date, state="bezahlt", value=50, is_interest_credit=True, quantity=1
            )
            self.assertEqual(share.share_type, self.share_type_deposit)
            self.assertEqual(share.note, "Anrechnung Darlehenszins an Depositenkasse")
            tr = book.get_transaction(book.build_transaction_id(list(book._db.keys())[0]))
            for split in tr.splits:
                if split.account == Account.from_settings(AccountKey.SHARES_DEPOSIT):
                    self.assertEqual(split.amount, -50)
                elif split.account == Account.from_settings(AccountKey.SHARES_INTEREST):
                    self.assertEqual(split.amount, 50)
                else:
                    raise ValueError(f"Wrong account: {split.account}")

    def test_add_invoice_obj_with_address(self):
        with AccountingManager(book_type_id="dum") as book:
            date = datetime.date(2000, 1, 1)
            account = Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL)
            receivables_account = Account.from_settings(AccountKey.SHARES_INTEREST)
            add_invoice_obj(
                book,
                "Invoice",
                self.invoicecategories[0],
                "Test-Description",
                self.addresses[0],
                account,
                receivables_account,
                date,
                100,
            )
            invoice = Invoice.objects.first()
            self.assertEqual(invoice.name, "Test-Description")
            self.assertEqual(invoice.person, self.addresses[0])
            self.assertEqual(invoice.date, date)
            self.assertEqual(invoice.fin_account, account.code)
            self.assertEqual(invoice.fin_account_receivables, receivables_account.code)
            tr = book.get_transaction(invoice.fin_transaction_ref)
            self.assertEqual(tr.description, "Test-Description [Muster, Hans]")
            for split in tr.splits:
                if split.account == account:
                    self.assertEqual(split.amount, -100)
                elif split.account == receivables_account:
                    self.assertEqual(split.amount, 100)
                else:
                    raise ValueError("Wrong account")

    def test_add_invoice_obj_invalid_type(self):
        with AccountingManager(book_type_id="dum") as book:
            with self.assertRaisesMessage(
                InvoiceCreationError, "Invoice type InvalidType is not implemented."
            ):
                add_invoice_obj(
                    book,
                    "InvalidType",
                    self.invoicecategories[0],
                    "Test-Description",
                    self.addresses[0],
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                )

    def test_add_invoice_object_duplicate_transaction_id(self):
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            add_invoice_obj(
                book,
                "Invoice",
                self.invoicecategories[0],
                "Test-Description",
                self.addresses[0],
                Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                Account.from_settings(AccountKey.SHARES_INTEREST),
                datetime.date.today(),
                100,
                transaction_id="unique_test_id",
            )
            with self.assertRaisesMessage(
                DuplicateInvoiceError,
                "Invoice with transaction ID unique_test_id exists already.",
            ):
                add_invoice_obj(
                    book,
                    "Invoice",
                    self.invoicecategories[0],
                    "Test-Description",
                    self.addresses[0],
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                    transaction_id="unique_test_id",
                )
            self.assertEqual(Invoice.objects.count(), 1)
            self.assertEqual(list(book._db.values())[0]["saved"], True)

    def test_add_invoice_obj_missing_contract_or_person(self):
        with AccountingManager(book_type_id="dum") as book:
            with self.assertRaisesMessage(
                InvoiceCreationError,
                "add_invoice_obj: need contract OR person.",
            ):
                add_invoice_obj(
                    book,
                    "Invoice",
                    self.invoicecategories[0],
                    "Test-Description",
                    None,  # person
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                )

    def test_add_invoice_obj_transaction_error(self):
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            with self.assertRaisesMessage(
                InvoiceCreationError,
                "Could not create invoice or transaction: ",
            ):
                add_invoice_obj(
                    None,  # book
                    "Invoice",
                    self.invoicecategories[0],
                    "Test-Description",
                    self.addresses[0],
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                )
            self.assertEqual(Invoice.objects.count(), 0)
            self.assertEqual(len(book._db), 0)

    @patch("geno.models.Invoice.save")
    def test_add_invoice_obj_invoice_save_error(self, mock_invoice_save):
        mock_invoice_save.side_effect = Exception("Boom!")
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            with self.assertRaisesMessage(
                InvoiceCreationError,
                "Could not save the invoice: Boom!",
            ):
                add_invoice_obj(
                    book,
                    "Invoice",
                    self.invoicecategories[0],
                    "Test-Description",
                    self.addresses[0],
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                )
            self.assertEqual(Invoice.objects.count(), 0)
            self.assertEqual(list(book._db.values())[0]["saved"], False)

    @patch("finance.accounting.DummyBook.save")
    def test_add_invoice_obj_transaction_save_error_and_rollback(self, mock_book_save):
        mock_book_save.side_effect = Exception("Boom!")
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            with self.assertRaisesMessage(
                InvoiceCreationError,
                "Could not save the transaction: Boom!",
            ):
                add_invoice_obj(
                    book,
                    "Invoice",
                    self.invoicecategories[0],
                    "Test-Description",
                    self.addresses[0],
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                )
            self.assertEqual(Invoice.objects.count(), 0)
            self.assertEqual(list(book._db.values())[0]["saved"], False)

    @patch("geno.models.Invoice.delete")
    @patch("finance.accounting.DummyBook.save")
    def test_add_invoice_obj_transaction_save_error_and_failed_rollback(
        self, mock_book_save, mock_delete_save
    ):
        mock_book_save.side_effect = Exception("Boom!")
        mock_delete_save.side_effect = Exception("Boom2!")
        with AccountingManager(book_type_id="dum") as book:
            book._db = {}
            with self.assertRaisesMessage(
                InvoiceCreationError,
                "Could not save the transaction: Boom! AND THE ROLLBACK FAILED: Boom2!",
            ):
                add_invoice_obj(
                    book,
                    "Invoice",
                    self.invoicecategories[0],
                    "Test-Description",
                    self.addresses[0],
                    Account.from_settings(AccountKey.DEFAULT_DEBTOR_MANUAL),
                    Account.from_settings(AccountKey.SHARES_INTEREST),
                    datetime.date.today(),
                    100,
                )
            self.assertEqual(Invoice.objects.count(), 1)
            self.assertEqual(list(book._db.values())[0]["saved"], False)


class TestQRBill(GenoAdminTestCase):
    def test_build_structured_qrbill_address(self):
        ret = build_structured_qrbill_address({"return": "same if dict"})
        self.assertEqual(ret, {"return": "same if dict"})
        with self.assertRaises(TypeError):
            build_structured_qrbill_address(None)
        adr = Address(
            organization="Org",
            first_name="Hans",
            name="Muster",
            street_name="Musterweg",
            house_number="1",
            city_name="Test",
            city_zipcode="12345",
            country="Schweiz",
        )
        ret = build_structured_qrbill_address(adr)
        self.assertEqual(
            ret,
            {
                "name": "Org",
                "street": adr.street_name,
                "house_num": adr.house_number,
                "pcode": adr.city_zipcode,
                "city": adr.city_name,
                "country": "CH",
            },
        )
        adr.organization = None
        ret = build_structured_qrbill_address(adr)
        self.assertEqual(
            ret,
            {
                "name": "Hans Muster",
                "street": adr.street_name,
                "house_num": adr.house_number,
                "pcode": adr.city_zipcode,
                "city": adr.city_name,
                "country": "CH",
            },
        )

        adr.country = "Deutschland"
        ret = build_structured_qrbill_address(adr)
        self.assertEqual(
            ret,
            {
                "name": "Hans Muster",
                "street": adr.street_name,
                "house_num": adr.house_number,
                "pcode": adr.city_zipcode,
                "city": adr.city_name,
                "country": "DE",
            },
        )

    def test_create_qrbill_address(self):
        ref_number = "999"
        context = {}
        adr = Address(
            organization="Org",
            first_name="Hans",
            name="Muster",
            street_name="Musterweg",
            house_number="1",
            city_name="Berlin",
            city_zipcode="12345",
            country="Deutschland",
        )
        output_filename = "test_create_qrbill.pdf"
        outfile = f"/tmp/{output_filename}"
        if os.path.isfile(outfile):
            os.remove(outfile)
        msg, nsent, recipient = create_qrbill(
            ref_number, adr, context, output_filename, render=True
        )
        self.assertEqual(
            msg[0],
            "Konnte QR-Rechnung nicht erstellen: render_qrbill(): "
            "'qr_amount' not found in context.",
        )

        context["qr_amount"] = "99.99"
        context["qr_extra_info"] = "Extrainfo"
        msg, nsent, recipient = create_qrbill(
            ref_number, adr, context, output_filename, render=True
        )
        self.assertEqual(
            msg[0], "Konnte QR-Rechnung nicht erstellen: The reference number is invalid"
        )

        ref_number = get_reference_nr(self.invoicecategories[0], 999)
        msg, nsent, recipient = create_qrbill(
            ref_number, adr, context, output_filename, render=True
        )
        self.assertEqual(msg, [])
        self.assertEqual(nsent, 0)
        self.assertEqual(recipient, None)
        self.assertInPDF(outfile, "Zahlbar durch\nOrg\nMusterweg 1\nDE-12345 Berlin")
