"""
Tests for importer admin interface.

Note: The importer app only uses Django Admin for managing imports.
All functionality is tested through the admin interface.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import ImportJob

User = get_user_model()


class ImporterAdminTest(TestCase):
    """Tests for importer admin interface."""

    def setUp(self):
        """Set up test client and admin user."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        self.client.login(username="admin", password="adminpass123")

    def test_admin_import_job_list(self):
        """Test that import job list is accessible in admin."""
        response = self.client.get(reverse("admin:importer_importjob_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_admin_import_job_add(self):
        """Test that import job add page is accessible in admin."""
        response = self.client.get(reverse("admin:importer_importjob_add"))
        self.assertEqual(response.status_code, 200)

    def test_admin_import_job_change(self):
        """Test that import job change page is accessible in admin."""
        job = ImportJob.objects.create(status="pending")
        response = self.client.get(reverse("admin:importer_importjob_change", args=[job.id]))
        self.assertEqual(response.status_code, 200)
