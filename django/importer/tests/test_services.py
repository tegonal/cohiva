"""
Tests for importer services.
"""

import tempfile
from pathlib import Path

import openpyxl
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..models import ImportJob, ImportRecord
from ..services import ExcelImporter, process_import_job

User = get_user_model()


class ExcelImporterTest(TestCase):
    """Tests for ExcelImporter service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def create_test_excel_file(self, data):
        """
        Helper to create a test Excel file.

        Args:
            data: List of lists representing rows (first row is headers)

        Returns:
            Path to the created file
        """
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        for row in data:
            worksheet.append(row)

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        workbook.save(temp_file.name)
        temp_file.close()

        return temp_file.name

    def test_process_valid_excel_file(self):
        """Test processing a valid Excel file."""
        # Create test Excel file
        test_data = [
            ["Name", "Email", "Age"],
            ["John Doe", "john@example.com", 30],
            ["Jane Smith", "jane@example.com", 25],
        ]
        excel_path = self.create_test_excel_file(test_data)

        try:
            # Create import job
            with open(excel_path, "rb") as f:
                job = ImportJob.objects.create(
                    created_by=self.user,
                    file=SimpleUploadedFile("test.xlsx", f.read()),
                )

            # Process the import
            importer = ExcelImporter(job)
            results = importer.process()

            # Verify results
            self.assertEqual(results["total_rows"], 2)
            self.assertEqual(results["success_count"], 2)
            self.assertEqual(results["error_count"], 0)

            # Verify job status
            job.refresh_from_db()
            self.assertEqual(job.status, "completed")
            self.assertEqual(job.records_imported, 2)

            # Verify records were created
            self.assertEqual(ImportRecord.objects.filter(job=job).count(), 2)

        finally:
            # Clean up
            Path(excel_path).unlink(missing_ok=True)

    def test_process_empty_excel_file(self):
        """Test processing an empty Excel file."""
        # Create empty Excel file
        excel_path = self.create_test_excel_file([])

        try:
            # Create import job
            with open(excel_path, "rb") as f:
                job = ImportJob.objects.create(
                    created_by=self.user,
                    file=SimpleUploadedFile("test.xlsx", f.read()),
                )

            # Process the import
            importer = ExcelImporter(job)

            with self.assertRaises(Exception):
                importer.process()

            # Verify job status
            job.refresh_from_db()
            self.assertEqual(job.status, "failed")

        finally:
            # Clean up
            Path(excel_path).unlink(missing_ok=True)

    def test_process_import_job_by_id(self):
        """Test processing an import job by ID."""
        # Create test Excel file
        test_data = [
            ["Name", "Value"],
            ["Test 1", 100],
            ["Test 2", 200],
        ]
        excel_path = self.create_test_excel_file(test_data)

        try:
            # Create import job
            with open(excel_path, "rb") as f:
                job = ImportJob.objects.create(
                    created_by=self.user,
                    file=SimpleUploadedFile("test.xlsx", f.read()),
                )

            # Process using the function
            results = process_import_job(job.id)

            # Verify results
            self.assertEqual(results["success_count"], 2)
            self.assertEqual(results["error_count"], 0)

        finally:
            # Clean up
            Path(excel_path).unlink(missing_ok=True)

