import datetime

from django.core.management.base import BaseCommand

from finance.accounting import AccountingManager
from geno.billing import get_income_account, get_receivables_account
from geno.models import Invoice


class Command(BaseCommand):
    help = (
        "Recreate transactions in the current book that exist already in a differnt book, "
        "for invoices newer than a specified date."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "start_date", help="Exclude invoices before this date (format: YYYY-MM-DD)"
        )

        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm that the actions should be executed (disable dry-run)",
        )

    def handle(self, *args, **options):
        # start_date = datetime.date(2026, 1, 1)
        try:
            start_date = datetime.datetime.strptime(options["start_date"], "%Y-%m-%d").date()
        except ValueError:
            self.stdout.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))
            return
        # AccountingManager.register_backends_from_settings()
        with AccountingManager() as book:
            invoices = self.get_invoices(book, start_date)
            output = self.recreate_transactions(book, invoices, dry_run=not options["confirm"])
        for line in output:
            self.stdout.write(line)
        if not options["confirm"] and len(output) > 1:
            self.stdout.write(
                self.style.WARNING(
                    "\nDRY RUN: No changes have been made. Use --confirm to execute the actions above (add transactions and update invoice references)."
                )
            )

    def get_invoices(self, book, start_date):
        transaction_ref_prefix = book.build_transaction_id("")
        return Invoice.objects.filter(date__gte=start_date).exclude(
            fin_transaction_ref__startswith=transaction_ref_prefix
        )

    def recreate_transactions(self, book, invoices, dry_run=True):
        output = []
        if not invoices:
            return ["No invoices found that need transaction recreation."]
        output.append("Recreate transactions for the following invoices:")
        for invoice in invoices:
            output.append(f"  - {invoice.date} {invoice} CHF {invoice.amount}")
            if invoice.contract and invoice.person:
                raise RuntimeError("Can't specify address AND contract.")
            account_key = None
            ## Special cases are not handled yet!
            #  rent_account_key:
            #  AccountKey.RENT_BUSINESS
            #  AccountKey.RENT_OTHER
            #  AccountKey.RENT_PARKING
            #  "Nebenkosten "
            #  "Nebenkosten pauschal "
            #  AccountKey.NK_FLAT
            #  AccountKey.RENT_REDUCTION
            #    ...

            account = get_income_account(invoice.invoice_category, account_key, invoice.contract)
            receivables_account = get_receivables_account(
                invoice.invoice_category, invoice.contract
            )

            if invoice.invoice_type == "Invoice":
                acc_debit = receivables_account
                acc_credit = account  # revenue account
            elif invoice.invoice_type == "Payment":
                acc_debit = account  # bank account
                acc_credit = receivables_account
            else:
                raise RuntimeError(f"Invoice type {invoice.invoice_type} is not implemented.")

            if invoice.contract:
                txn_description = "%s [%s]" % (invoice.name, invoice.contract.get_contract_label())
            elif invoice.person:
                txn_description = "%s [%s]" % (invoice.name, invoice.person)
            else:
                raise RuntimeError(f"Invoice without contract or person: {invoice}")

            fin_transaction_ref = book.add_transaction(
                invoice.amount,
                acc_debit,
                acc_credit,
                invoice.date,
                txn_description,
                autosave=False,
            )
            old_fin_transaction_ref = invoice.fin_transaction_ref
            invoice.fin_transaction_ref = fin_transaction_ref
            warnings = []
            if invoice.fin_account != account.code:
                warnings.append(
                    f"Will change invoice fin_account: {invoice.fin_account} => {account.code}"
                )
                invoice.fin_account = account.code
            if invoice.fin_account_receivables != receivables_account.code:
                warnings.append(
                    "Will change invoice fin_account_receivables: "
                    f"{invoice.fin_account_receivables} => {receivables_account.code}"
                )
                invoice.fin_account_receivables = receivables_account.code
            if dry_run:
                text = "Would add"
            else:
                text = "Added"
                try:
                    invoice.save()
                except Exception as e:
                    output.append(f"    - ERROR: Failed to save invoice: {e}")
                    return output
                try:
                    book.save()
                except Exception as e:
                    output.append(f"    - ERROR: Failed to save book: {e}")
                    return output
            output.append(
                f"    - {text} transaction and change reference:"
                f"{old_fin_transaction_ref} => {fin_transaction_ref}"
            )
            if len(warnings) == 1:
                output.append(f"      WARNING: {warnings[0]}")
            elif warnings:
                output.append("      WARNINGS:")
                for warning in warnings:
                    output.append(f"        * {warning}")
        return output
