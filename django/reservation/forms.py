from django import forms


class ReportLogEntryInlineFormset(forms.models.BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        obj.user = self.request.user

        if commit:
            obj.save()

        return obj
