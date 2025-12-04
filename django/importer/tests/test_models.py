"""
Tests for importer models.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import ImportJob, ImportRecord

User = get_user_model()


class ImportJobModelTest(TestCase):
    """Tests for ImportJob model."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_import_job(self):
        """Test creating an import job."""
        job = ImportJob.objects.create(
            status="pending",
        )
        self.assertEqual(job.status, "pending")
        self.assertEqual(job.records_imported, 0)

    def test_import_job_string_representation(self):
        """Test the string representation of ImportJob."""
        job = ImportJob.objects.create()
        self.assertIn("Import Job", str(job))
        self.assertIn(job.status, str(job))


class ImportRecordModelTest(TestCase):
    """Tests for ImportRecord model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.job = ImportJob.objects.create()

    def test_create_import_record(self):
        """Test creating an import record."""
        record = ImportRecord.objects.create(
            job=self.job,
            row_number=1,
            data={"name": "Test", "value": 123},
            success=True,
        )
        self.assertEqual(record.job, self.job)
        self.assertEqual(record.row_number, 1)
        self.assertTrue(record.success)

    def test_import_record_string_representation(self):
        """Test the string representation of ImportRecord."""
        record = ImportRecord.objects.create(
            job=self.job,
            row_number=1,
            data={"name": "Test"},
            success=True,
        )
        self.assertIn("Row 1", str(record))
