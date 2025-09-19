import datetime
import logging
from zoneinfo import ZoneInfo

import select2.fields
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic.edit import CreateView, FormView, UpdateView
from django_tables2 import SingleTableMixin, SingleTableView

from geno.importer import process_transaction_file

from .accounts import (
    AccountInformationMixin,
    get_accounts_for_user,
    get_transactions_queryset_and_balance,
    import_transactions,
    verify_accounts_data_integrity,
)
from .forms import (
    AccountEditForm,
    AccountFilterForm,
    RevenueReportForm,
    TransactionEditForm,
    TransactionFilterForm,
    TransactionUploadForm,
)
from .models import Account, AccountOwner, Transaction
from .tables import AccountTable, RevenueReportTable, SalesByAccountReportTable, TransactionTable

logger = logging.getLogger("credit_accounting")


class TransactionListView(AccountInformationMixin, SingleTableView):
    table_class = TransactionTable
    template_name = "credit_accounting/table_transactions.html"
    # paginate_by = 100

    def default_filter(self):
        if self.accounts and len(self.accounts):
            default_account = self.accounts[0].id
        else:
            default_account = None
        return {
            "search": "",
            "account": default_account,
            #'month': 0,
            #'year': 0,
            "time": "days_90",
            "sign": "all",
            "amount_min": "",
            "amount_max": "",
        }

    def get_queryset(self):
        if not hasattr(self, "filter"):
            self.filter = self.default_filter()
        return get_transactions_queryset_and_balance(self)

    def get_table_kwargs(self):
        return {"balance": self.balance}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Kontoauszug" % self.vendor
        context["form"] = self.form
        return context

    def get(self, request, *args, **kwargs):
        self.accounts = get_accounts_for_user(self.user, self.vendor)
        if not self.accounts and not self.is_admin:
            return redirect("login-required")
        self.filter = self.default_filter()
        if "transaction_filter" in request.session:
            self.filter.update(request.session["transaction_filter"])
        self.form = TransactionFilterForm(
            initial=self.filter, accounts=self.accounts, admin=self.is_admin
        )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.accounts = get_accounts_for_user(self.user, self.vendor)
        self.form = TransactionFilterForm(
            request.POST, accounts=self.accounts, admin=self.is_admin
        )
        self.filter = self.default_filter()
        if self.form.is_valid():
            self.filter.update(self.form.cleaned_data)
            request.session["transaction_filter"] = self.filter
        return super().get(request, *args, **kwargs)


class TransactionCreateView(AccountInformationMixin, CreateView):
    model = Transaction
    form_class = TransactionEditForm
    initial = {"date": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.is_admin:
            form.fields["account"] = select2.fields.ModelChoiceField(
                queryset=Account.objects.filter(active=True).filter(vendor=self.vendor),
                model=None,
                name=None,
                label="Konto",
            )
        else:
            return None
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            self.object.name = "Manuelle Buchung"
            self.object.user = self.user
            self.object.save()
            logger.info(
                "Manual transaction: %s - CHF %s [%s] %s"
                % (
                    self.object.account,
                    self.object.amount,
                    self.object.date,
                    self.object.description,
                )
            )
            messages.success(
                request,
                "Transaktion gespeichert: %s - CHF %s [%s] %s"
                % (
                    self.object.account,
                    self.object.amount,
                    self.object.date,
                    self.object.description,
                ),
            )
            return self.render_to_response(self.get_context_data(form=form))
        else:
            self.object = None
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Transaktion hinzufügen" % self.vendor
        return context


class TransactionUploadView(AccountInformationMixin, FormView):
    template_name = "credit_accounting/transaction_upload.html"
    form_class = TransactionUploadForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            ret = []
            if "file" in request.FILES:
                uploaded_file = request.FILES["file"]
            else:
                messages.error(request, "Konnte Datei nicht hochladen.")
                return self.form_invalid(form)
            transaction_data = process_transaction_file(uploaded_file)
            if transaction_data["error"]:
                messages.error(
                    request, "Konnte Datei nicht verarbeiten: %s" % transaction_data["error"]
                )
                logger.error(
                    f"Transaction upload: Error while processing {uploaded_file}: "
                    f"{transaction_data['error']}"
                )
            elif transaction_data["type"].startswith("camt.053") or transaction_data[
                "type"
            ].startswith("camt.054"):
                ret = import_transactions(transaction_data["data"], self.vendor)
                if len(ret):
                    logger.info(
                        f"Transaction upload: Imported {len(ret)} records from {uploaded_file}."
                    )
            else:
                messages.error(
                    request,
                    "Konnte Datei nicht verarbeiten: Unbekannter typ %s"
                    % transaction_data["type"],
                )
                logger.error(
                    f"Transaction upload: Error while processing {uploaded_file}: "
                    f"Invalid type {transaction_data['type']}"
                )

            import_message = "Import von Buchungen aus %s:" % uploaded_file
            return self.render_to_response(
                self.get_context_data(import_message=import_message, import_items=ret)
            )
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Transaktionen importieren" % self.vendor
        context["item_name"] = "Buchnungen"
        return context


class AccountListView(AccountInformationMixin, SingleTableView):
    table_class = AccountTable
    template_name = "credit_accounting/table_accounts.html"
    paginate_by = 100

    def get_queryset(self):
        if self.is_admin:
            qs = Account.objects.filter(vendor=self.vendor)
            if self.filter["search"]:
                qs = qs.filter(
                    Q(name__icontains=self.filter["search"]) | Q(pin=self.filter["search"])
                )
            return qs
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["now"] = timezone.now()
        context["title"] = "%s Konten" % self.vendor
        context["form"] = self.form
        return context

    def get(self, request, *args, **kwargs):
        ## TODO: Move check to periodic maintainance task (if still needed)
        verify_accounts_data_integrity()
        if "account_filter" in request.session:
            self.filter = request.session["account_filter"]
        else:
            self.filter = {
                "search": "",
            }
        self.form = AccountFilterForm(initial=self.filter)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = AccountFilterForm(request.POST)
        if self.form.is_valid():
            self.filter = self.form.cleaned_data
            request.session["account_filter"] = self.filter
        return super().get(request, *args, **kwargs)


class AccountCreateView(AccountInformationMixin, CreateView):
    model = Account
    form_class = AccountEditForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.vendor = self.vendor
        form.is_update = False
        if self.is_admin:
            pass
        else:
            return None
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            # self.object = form.save()
            self.object = Account(
                name=form.cleaned_data["name"],
                pin=form.cleaned_data["pin"],
                active=form.cleaned_data["active"],
                vendor=self.vendor,
            )
            owner_obj = self.get_account_owner(form.cleaned_data["owner"])
            self.object.save()
            ## Save account owner
            owner = AccountOwner(name=self.object, owner_object=owner_obj)
            owner.save()
            logger.info(f"Created account {self.object.pk}: {self.object} / {owner_obj}")
            messages.success(request, "Konto erstellt: %s / %s" % (self.object, owner_obj))
            return self.render_to_response(self.get_context_data(form=form))
        else:
            self.object = None
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Konto hinzufügen" % self.vendor
        return context


class AccountEditView(AccountInformationMixin, UpdateView):
    model = Account
    form_class = AccountEditForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.vendor = self.vendor
        form.is_update = True
        try:
            self.owner = AccountOwner.objects.get(name=self.object)
            form.initial["owner"] = self.get_account_owner_id(self.owner.owner_object)
        except AccountOwner.DoesNotExist:
            self.owner = None
        if not self.is_admin:
            return None
        return form

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.object.name = form.cleaned_data["name"]
            self.object.pin = form.cleaned_data["pin"]
            self.object.active = form.cleaned_data["active"]
            self.object.vendor = self.vendor

            ## Update account owner
            if not self.owner:
                self.owner = AccountOwner(name=self.object)
            self.owner.owner_object = self.get_account_owner(form.cleaned_data["owner"])
            self.owner.save()
            self.object.save()
            messages.success(
                request, "Konto aktualisiert: %s / %s" % (self.object, self.owner.owner_object)
            )
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Konto bearbeiten: %s" % (self.vendor, self.object.name)
        return context


class QRBillView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        try:
            account = Account.objects.get(pk=kwargs.get("pk"))
        except Account.DoesNotExist:
            raise Http404("Konto nicht gefunden.")
        try:
            pdf_name = account.create_qrbill()
            pdf_file = open(f"/tmp/{pdf_name}", "rb")
            resp = FileResponse(pdf_file, content_type="application/pdf")
            resp["Content-Disposition"] = (
                f'attachment; filename="QR_{account.vendor}_{account.name}.pdf"'
            )
            return resp
        except Exception as e:
            logger.error(f"Could not create QR-bill for account {account.pk}/{account}: {e}")
            return HttpResponse("Fehler: Konnte QR-Rechnung nicht erzeugen.")


class RevenueReportView(AccountInformationMixin, SingleTableMixin, FormView):
    table_class = RevenueReportTable
    form_class = RevenueReportForm
    template_name = "credit_accounting/table_revenue_report.html"
    paginate_by = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_year = 2022
        ## Default filter
        self.filter = {
            "period": f"year_{datetime.datetime.now().year}",
            "manual_start": f"{datetime.date.today().strftime('%d.%m.%Y')} 12:00:00",
            "manual_end": f"{datetime.date.today().strftime('%d.%m.%Y')} 18:00:00",
        }

    def calc_period(self, start=None, end=None):
        result = {}
        qs = Transaction.objects.filter(account__vendor=self.vendor)
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lt=end)
        result["in"] = qs.filter(amount__gt=0).aggregate(sum_=Sum("amount")).get("sum_")
        result["out"] = qs.filter(amount__lt=0).aggregate(sum_=Sum("amount")).get("sum_")
        if not result["in"]:
            result["in"] = 0
        if not result["out"]:
            result["out"] = 0
        result["net"] = result["in"] + result["out"]
        return result

    def get_table_data(self):
        if not self.is_admin:
            return []
        if not hasattr(self, "filter"):
            return []
        if self.filter["period"] == "all_years":
            report_start = datetime.datetime(
                self.start_year, 1, 1, tzinfo=ZoneInfo(settings.TIME_ZONE)
            )
            report_end = datetime.datetime(
                datetime.datetime.now().year, 12, 31, tzinfo=ZoneInfo(settings.TIME_ZONE)
            )
            delta = relativedelta(months=+12)
            date_format = "%Y"
        elif self.filter["period"].startswith("year_"):
            year = int(self.filter["period"][5:])
            if year < 1900 or year > 3000:
                raise RuntimeError("Inavlid filter period: {self.filter['period']}")
            report_start = datetime.datetime(year, 1, 1, tzinfo=ZoneInfo(settings.TIME_ZONE))
            report_end = datetime.datetime(year, 12, 31, tzinfo=ZoneInfo(settings.TIME_ZONE))
            delta = relativedelta(months=+1)
            date_format = "%b %Y"
        elif self.filter["period"] == "manual":
            report_start = datetime.datetime.strptime(
                self.filter["manual_start"], "%d.%m.%Y %H:%M:%S"
            ).replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            report_end = datetime.datetime.strptime(
                self.filter["manual_end"], "%d.%m.%Y %H:%M:%S"
            ).replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            delta = None
            date_format = "%d.%m.%Y %H:%M"
        elif self.filter["period"] == "none":
            return []
        else:
            raise RuntimeError(f"Inavlid filter period: {self.filter['period']}")

        base = self.calc_period(end=report_start)

        table_data = []
        total = {"in": 0, "out": 0, "balance": base["net"]}
        date = report_start
        while date < report_end:
            if delta:
                next_date = date + delta
                date_str = date.strftime(date_format)
            else:
                next_date = report_end
                date_str = f"{date.strftime(date_format)} - {next_date.strftime(date_format)}"
            sums = self.calc_period(date, next_date)
            total["in"] += sums["in"]
            total["out"] += sums["in"]
            total["balance"] += sums["net"]
            table_data.append(
                {
                    "date": date_str,
                    "amount_in": sums["in"],
                    "amount_out": sums["out"],
                    "amount_net": sums["net"],
                    "balance": total["balance"],
                }
            )
            date = next_date
        return table_data

    def get_form(self):
        start = datetime.datetime.strptime(
            self.filter["manual_start"], "%d.%m.%Y %H:%M:%S"
        ).replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
        end = datetime.datetime.strptime(self.filter["manual_end"], "%d.%m.%Y %H:%M:%S").replace(
            tzinfo=ZoneInfo(settings.TIME_ZONE)
        )
        initial = {
            "period": self.filter["period"],
            "start_date": start.date(),
            "start_time": start.time(),
            "end_date": end.date(),
            "end_time": end.time(),
        }
        return RevenueReportForm(start_year=self.start_year, initial=initial)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Umsatz- und Guthabenreport" % (self.vendor)
        return context

    def get(self, request, *args, **kwargs):
        if "report_filter" in request.session:
            self.filter.update(request.session["report_filter"])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = RevenueReportForm(request.POST, start_year=self.start_year)
        if form.is_valid():
            self.filter.update(
                {
                    "period": form.cleaned_data["period"],
                    "manual_start": form.cleaned_data["start_date"].strftime("%d.%m.%Y")
                    + " "
                    + form.cleaned_data["start_time"].strftime("%H:%M:%S"),
                    "manual_end": form.cleaned_data["end_date"].strftime("%d.%m.%Y")
                    + " "
                    + form.cleaned_data["end_time"].strftime("%H:%M:%S"),
                }
            )
            request.session["report_filter"] = self.filter
        else:
            self.filter["period"] = "none"
        return self.render_to_response(self.get_context_data(form=form))


class SalesByAccountReportView(AccountInformationMixin, SingleTableView):
    table_class = SalesByAccountReportTable
    template_name = "credit_accounting/table.html"
    paginate_by = 100

    def get_queryset(self):
        return []

    def calc_period(self, account, year):
        start = datetime.datetime(year, 1, 1, 0, 0, 0, tzinfo=ZoneInfo(settings.TIME_ZONE))
        end = datetime.datetime(year, 12, 31, 23, 59, 59, tzinfo=ZoneInfo(settings.TIME_ZONE))
        qs = (
            Transaction.objects.filter(account=account)
            .filter(date__gte=start)
            .filter(date__lte=end)
        )
        result = qs.filter(amount__lt=0).aggregate(sum_=Sum("amount")).get("sum_")
        if result:
            return result
        else:
            return 0

    def get_table_data(self):
        if not self.is_admin:
            return []

        table_data = []
        year = datetime.datetime.now().year
        for account in Account.objects.filter(vendor=self.vendor):
            table_data.append(
                {
                    "account": str(account),
                    "amount_cur": self.calc_period(account, year),
                    "amount_prev": self.calc_period(account, year - 1),
                    "amount_prev2": self.calc_period(account, year - 2),
                }
            )
        return table_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "%s Verkäufe nach Konto" % (self.vendor)
        return context
