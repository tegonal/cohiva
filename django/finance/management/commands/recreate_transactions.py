import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from finance.accounting import Account, AccountingManager
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
        accounts_summary = {}
        for invoice in invoices:
            warnings = []
            output.append(f"  - {invoice.date} {invoice} CHF {invoice.amount}")
            if invoice.contract and invoice.person:
                raise RuntimeError("Can't specify address AND contract.")

            old_fin_account = invoice.fin_account
            old_fin_account_receivables = invoice.fin_account_receivables
            ## Optional mapping to new account numbers, if configured in settings
            if hasattr(settings, "FINANCIAL_ACCOUNTING_OLD_ACCOUNT_MAPPING"):
                if old_fin_account in settings.FINANCIAL_ACCOUNTING_OLD_ACCOUNT_MAPPING:
                    invoice.fin_account = str(
                        settings.FINANCIAL_ACCOUNTING_OLD_ACCOUNT_MAPPING[old_fin_account]
                    )
                if (
                    old_fin_account_receivables
                    in settings.FINANCIAL_ACCOUNTING_OLD_ACCOUNT_MAPPING
                ):
                    invoice.fin_account_receivables = str(
                        settings.FINANCIAL_ACCOUNTING_OLD_ACCOUNT_MAPPING[
                            old_fin_account_receivables
                        ]
                    )

            if invoice.invoice_type == "Invoice":
                acc_debit = Account(
                    name="Recreate-Inv-Debit", prefix=invoice.fin_account_receivables
                )
                acc_credit = Account(name="Recreate-Inv-Credit", prefix=invoice.fin_account)
            elif invoice.invoice_type == "Payment":
                acc_debit = Account(name="Recreate-Pay-Credit", prefix=invoice.fin_account)
                acc_credit = Account(
                    name="Recreate-Pay-Debit", prefix=invoice.fin_account_receivables
                )
            else:
                raise RuntimeError(f"Invoice type {invoice.invoice_type} is not implemented.")

            if invoice.fin_account not in accounts_summary:
                accounts_summary[invoice.fin_account] = []
            if (
                invoice.fin_account != old_fin_account
                and old_fin_account not in accounts_summary[invoice.fin_account]
            ):
                accounts_summary[invoice.fin_account].append(old_fin_account)
            if invoice.fin_account_receivables not in accounts_summary:
                accounts_summary[invoice.fin_account_receivables] = []
            if (
                invoice.fin_account_receivables != old_fin_account_receivables
                and old_fin_account_receivables
                not in accounts_summary[invoice.fin_account_receivables]
            ):
                accounts_summary[invoice.fin_account_receivables].append(
                    old_fin_account_receivables
                )

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
        if accounts_summary:
            output.append("")
            output.append("Summary of new accounts that need to exist")
            output.append("(and the old account numbers, if mapped)")
            output.append("=============================================")
            for account_code in sorted(accounts_summary.keys()):
                old = accounts_summary[account_code]
                if old:
                    output.append(f"  {account_code} <= {', '.join(old)}")
                else:
                    output.append(f"  {account_code}")
        return output
