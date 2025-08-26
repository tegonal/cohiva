from django.urls import path
from django.views.generic.base import TemplateView

# from . import views as reservation_views
from .views import (
    AccountCreateView,
    AccountEditView,
    AccountListView,
    QRBillView,
    RevenueReportView,
    SalesByAccountReportView,
    TransactionCreateView,
    TransactionListView,
    TransactionUploadView,
)

# app_name = 'reservation'
urlpatterns = [
    path("", TransactionListView.as_view(), name="transaction-list"),
    path("add/", TransactionCreateView.as_view(), name="transaction-create"),
    path("upload/", TransactionUploadView.as_view(), name="transaction-upload"),
    path("accounts/", AccountListView.as_view(), name="account-list"),
    path("accounts/add/", AccountCreateView.as_view(), name="account-create"),
    path("accounts/edit/<int:pk>/", AccountEditView.as_view(), name="account-edit"),
    path("accounts/qrbill/<int:pk>/", QRBillView.as_view(), name="account-qrbill"),
    path(
        "login_required/",
        TemplateView.as_view(
            template_name="credit_accounting/login_required.html",
            extra_context={"title": "Nichts gefunden"},
        ),
        name="login-required",
    ),
    path("report/", RevenueReportView.as_view(), name="report-revenue"),
    path(
        "report/salesbyaccount/", SalesByAccountReportView.as_view(), name="report-salesbyaccount"
    ),
]
