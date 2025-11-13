"""
Management command to process pending member/address imports.
"""

from django.core.management.base import BaseCommand, CommandError

from importer.models import ImportJob
from importer.services import process_member_address_import


class Command(BaseCommand):
    """Process pending member/address import jobs."""

    help = "Process pending member/address import jobs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--job-id",
            type=int,
            help="Process a specific import job by ID",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all pending import jobs",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        job_id = options.get("job_id")
        process_all = options.get("all")

        if job_id:
            # Process specific job
            try:
                job = ImportJob.objects.get(id=job_id)
                self.stdout.write(f"Processing import job {job_id}...")

                results = process_member_address_import(job_id)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully processed job {job_id}: "
                        f"{results['success_count']} records imported, "
                        f"{results['error_count']} errors"
                    )
                )

                if results["error_count"] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Errors occurred in {results['error_count']} rows. "
                            "Check the admin interface for details."
                        )
                    )

            except ImportJob.DoesNotExist:
                raise CommandError(f"Import job {job_id} does not exist")
            except Exception as e:
                raise CommandError(f"Error processing job {job_id}: {str(e)}")

        elif process_all:
            # Process all pending jobs
            pending_jobs = ImportJob.objects.filter(status="pending")
            count = pending_jobs.count()

            if count == 0:
                self.stdout.write(self.style.WARNING("No pending import jobs found"))
                return

            self.stdout.write(f"Found {count} pending import job(s)")

            success_total = 0
            error_total = 0
            failed_jobs = []

            for job in pending_jobs:
                try:
                    self.stdout.write(f"Processing job {job.id}...")
                    results = process_member_address_import(job.id)
                    success_total += results["success_count"]
                    error_total += results["error_count"]

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Job {job.id}: {results['success_count']} records, "
                            f"{results['error_count']} errors"
                        )
                    )
                except Exception as e:
                    failed_jobs.append((job.id, str(e)))
                    self.stdout.write(self.style.ERROR(f"  ✗ Job {job.id} failed: {str(e)}"))

            # Summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Processed {count} jobs: {success_total} total records imported"
                )
            )

            if error_total > 0:
                self.stdout.write(self.style.WARNING(f"Total errors: {error_total}"))

            if failed_jobs:
                self.stdout.write(
                    self.style.ERROR(f"Failed jobs: {', '.join([str(j[0]) for j in failed_jobs])}")
                )

        else:
            # No arguments provided
            self.stdout.write(
                self.style.WARNING("Please specify --job-id <ID> or --all to process imports")
            )

            # Show pending jobs
            pending_jobs = ImportJob.objects.filter(status="pending")
            count = pending_jobs.count()

            if count > 0:
                self.stdout.write(f"\nFound {count} pending import job(s):")
                for job in pending_jobs[:10]:
                    self.stdout.write(
                        f"  - Job {job.id}: {job.file.name} "
                        f"(created {job.created_at.strftime('%Y-%m-%d %H:%M')})"
                    )
                if count > 10:
                    self.stdout.write(f"  ... and {count - 10} more")
