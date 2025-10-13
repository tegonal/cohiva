import datetime

import select2.fields
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from geno.models import Address, Contract

from .accounts import get_transaction_time_filter_options
from .models import Account, Transaction


class TransactionEditForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["account", "date", "amount", "description"]
        widgets = {
            "date": forms.DateTimeInput(format="%d.%m.%Y %H:%M", attrs={"class": "datepicker"})
        }


class TransactionFilterForm(forms.Form):
    search_widget = forms.TextInput(
        attrs={
            "size": "40",
            "autofocus": True,
        }
    )

    search = forms.CharField(label="Suche", required=False, widget=search_widget)
    time = forms.ChoiceField(
        choices=get_transaction_time_filter_options(), label="Zeitraum", required=False
    )
    sign_options = [
        ("all", "Alle Buchungen"),
        ("plus", "Gutschriften"),
        ("minus", "Lastschriften"),
    ]
    sign = forms.ChoiceField(choices=sign_options, label="Typ", required=False)
    amount_min = forms.FloatField(label="Betrag min.", required=False)
    amount_max = forms.FloatField(label="Betrag max.", required=False)

    def __init__(self, *args, **kwargs):
        accounts = kwargs.pop("accounts", [])
        admin = kwargs.pop("admin", False)
        super().__init__(*args, **kwargs)
        account_options = [(account.id, str(account)) for account in accounts]
        if admin:
            account_options.append(("_all_", "== ALLE =="))
        self.fields["account"] = select2.fields.ChoiceField(choices=account_options, label="Konto")
        self.fields["account"].widget.choices = iter(account_options)


class TransactionUploadForm(forms.Form):
    file = forms.FileField(required=False)


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "pin", "active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        owner_options = []
        for c in sorted(
            Contract.objects.filter(Q(date_end=None) | Q(date_end__gt=datetime.date.today())),
            key=str,
        ):
            owner_options.append(("c_%s" % c.id, str(c)))
        for a in Address.objects.filter(active=True).exclude(user=None):
            owner_options.append(("a_%s" % a.id, str(a)))
        self.fields["owner"] = select2.fields.ChoiceField(
            choices=owner_options, label="Verknüpft mit"
        )
        self.fields["owner"].widget.choices = iter(owner_options)

    def clean(self):
        cleaned_data = super().clean()
        if not self.is_update:
            if (
                Account.objects.filter(pin=cleaned_data.get("pin"))
                .filter(vendor=self.vendor)
                .exists()
            ):
                raise ValidationError("Es existiert bereits ein Konto mit diesem PIN.")
            if (
                Account.objects.filter(name=cleaned_data.get("name"))
                .filter(vendor=self.vendor)
                .exists()
            ):
                raise ValidationError("Es existiert bereits ein Konto mit diesem Namen.")
        return cleaned_data


class AccountFilterForm(forms.Form):
    search_widget = forms.TextInput(
        attrs={
            "size": "40",
            "autofocus": True,
        }
    )
    search = forms.CharField(label="Suche", required=False, widget=search_widget)


class RevenueReportForm(forms.Form):
    def __init__(self, *args, start_year=2022, **kwargs):
        super().__init__(*args, **kwargs)
        period_options = [("all_years", "Alle Jahre"), ("manual", "Manuelle Eingabe")]
        for year in range(start_year, datetime.datetime.now().year + 1):
            period_options.insert(0, (f"year_{year}", f"Jahr {year}"))
        self.fields["period"] = select2.fields.ChoiceField(
            choices=period_options, label="Zeitraum"
        )
        self.fields["period"].widget.choices = iter(period_options)

    start_date = forms.DateField(
        label="Start Datum", widget=forms.TextInput(attrs={"class": "datepicker"})
    )
    start_time = forms.TimeField(label="Start Zeit")
    end_date = forms.DateField(
        label="End Datum", widget=forms.TextInput(attrs={"class": "datepicker"})
    )
    end_time = forms.TimeField(label="Start Zeit")
