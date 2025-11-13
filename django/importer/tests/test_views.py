"""
Tests for importer views.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import ImportJob

User = get_user_model()


class ImporterViewsTest(TestCase):
    """Tests for importer views."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_upload_view_get(self):
        """Test GET request to upload view."""
        response = self.client.get(reverse("importer:upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload Excel File")

    def test_upload_view_requires_login(self):
        """Test that upload view requires login."""
        self.client.logout()
        response = self.client.get(reverse("importer:upload"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_import_job_detail_view(self):
        """Test import job detail view."""
        job = ImportJob.objects.create(created_by=self.user, status="completed")
        response = self.client.get(reverse("importer:detail", args=[job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import Job Details")
# Tests module for importer app

