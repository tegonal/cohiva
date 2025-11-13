"""
Forms for the importer app.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ImportJob


class ImportJobForm(forms.ModelForm):
    """Form for creating import jobs."""

    class Meta:
        model = ImportJob
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={"accept": ".xlsx,.xls"}),
        }

    def clean_file(self):
        """Validate that the uploaded file is an Excel file."""
        file = self.cleaned_data.get("file")
        if file:
            # Check file extension
            if not file.name.lower().endswith((".xlsx", ".xls")):
                raise forms.ValidationError(
                    _("Please upload a valid Excel file (.xlsx or .xls)")
                )
            # Check file size (limit to 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_("File size cannot exceed 10MB"))
        return file

