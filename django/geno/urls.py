from django.urls import path, re_path

from . import views as geno_views

app_name = "geno"
urlpatterns = [
    re_path(r"^import/([a-z_-]+)/?$", geno_views.import_generic),
    re_path(r"^export/([a-z_-]+)/?$", geno_views.export_generic, name="generic-export"),
    re_path(r"^documents/([a-z_-]+)/([0-9]+)/([a-z_-]+)/?$", geno_views.documents),
    path("share/overview/", geno_views.ShareOverviewView.as_view(), name="share_overview"),
    path("share/overview/plot/", geno_views.share_overview_boxplot),
    path("share/export/", geno_views.share_export, name="share-export"),
    path(
        "share/confirm/",
        geno_views.ShareConfirmationLetterView.as_view(),
        name="share-confirmation-letter",
    ),
    path(
        "share/duedate_reminder/",
        geno_views.ShareReminderLetterView.as_view(),
        name="share-reminder-letter",
    ),
    re_path(
        r"^share/statement/(?P<date>[a-z0-9_-]+)/(?P<address>[0-9]+)/?$",
        geno_views.share_statement,
    ),
    re_path(r"^share/statement/(?P<date>[a-z0-9_-]+)/?$", geno_views.share_statement),
    path("share/mailing/", geno_views.share_mailing),
    path("share/interest/", geno_views.ShareInterestView.as_view(), name="share-interest"),
    path(
        "share/interest/download/",
        geno_views.ShareInterestView.as_view(action="download"),
        name="share-interest-download",
    ),
    path(
        "share/interest/transactions/",
        geno_views.ShareInterestView.as_view(action="create_transactions"),
        name="share-interest-create-transactions",
    ),
    path("share/check/", geno_views.share_check),
    path("member/overview/", geno_views.MemberOverviewView.as_view(), name="member_overview"),
    path("member/overview/plot/", geno_views.member_overview_plot),
    path("member/list/", geno_views.member_list),
    path("member/list_admin/", geno_views.member_list_admin),
    path(
        "member/check_mailinglists/",
        geno_views.CheckMailinglistsView.as_view(),
        name="check-mailinglists",
    ),
    path("member/check_payments/", geno_views.check_payments),
    path("member/send_mail/", geno_views.MailWizardView.as_view(), name="mail-wizard-start"),
    path(
        "member/send_mail/select/",
        geno_views.MailWizardSelectView.as_view(),
        name="mail-wizard-select",
    ),
    path(
        "member/send_mail/action/",
        geno_views.MailWizardActionView.as_view(),
        name="mail-wizard-action",
    ),
    path(
        "member/confirm/memberletter/",
        geno_views.MemberLetterView.as_view(doctype="memberletter"),
        name="member-confirmation-letter",
    ),
    path(
        "member/confirm/memberfinanz/",
        geno_views.MemberLetterView.as_view(doctype="memberfinanz"),
        name="member-finance-letter",
    ),
    path("address/export/", geno_views.address_export, name="address_export"),
    path("maintenance/", geno_views.run_maintenance_tasks),
    path("maintenance/check_portal_users/", geno_views.check_portal_users),
    path("maintenance/check_duplicate_invoices/", geno_views.check_duplicate_invoices),
    path(
        "transaction_upload/",
        geno_views.TransactionUploadView.as_view(),
        name="transaction-upload",
    ),
    path("transaction_upload/process/", geno_views.transaction_upload_process),
    path(
        "transaction_upload/testdata/",
        geno_views.transaction_testdata,
        name="transaction-testdata",
    ),
    path(
        "transaction_invoice/",
        geno_views.TransactionInvoiceView.as_view(),
        name="transaction-invoice",
    ),
    path("transaction/", geno_views.TransactionManualView.as_view(), name="transaction-manual"),
    path("invoice/", geno_views.InvoiceView.as_view(), name="invoice-manual"),
    path("invoice/form", geno_views.invoice_form, name="invoice-batch-form"),
    path("invoice/auto/", geno_views.InvoiceBatchView.as_view(), name="invoice-batch"),
    re_path(
        r"^invoice/download/(?P<key_type>[a-z_-]+)/(?P<key>[0-9]+)/?$",
        geno_views.InvoiceBatchView.as_view(action="download"),
        name="invoice-download",
    ),
    path("debtor/", geno_views.DebtorView.as_view(action="overview"), name="debtor-list"),
    re_path(
        r"^debtor/detail/(?P<key_type>[cp])/(?P<key>[0-9]+)/?$",
        geno_views.DebtorView.as_view(action="detail"),
        name="debtor-detail",
    ),
    path("contract/create/", geno_views.create_contracts),
    path("contract/create_letter/", geno_views.create_contracts, {"letter": True}),
    path(
        "contract/create_documents/check/",
        geno_views.create_documents_deprecated,
        {"default_doctype": "contract_check"},
    ),
    path("rental/resident_list", geno_views.ResidentListView.as_view(), name="resident-list"),
    path("rental/tenants/", geno_views.rental_unit_list_tenants, name="resident-list-tenants"),
    path("rental/units/", geno_views.rental_unit_list_units, name="resident-list-units"),
    path(
        "rental/units/mailbox/", geno_views.rental_unit_list_create_documents, {"doc": "mailbox"}
    ),
    path(
        "rental/units/protocol/", geno_views.rental_unit_list_create_documents, {"doc": "protocol"}
    ),
    path("odt2pdf/", geno_views.odt2pdf_form),
    path("webstamp/", geno_views.webstamp_form),
    path("oauth_client/", geno_views.oauth_client_test, {"action": "start"}),
    path("oauth_client/login", geno_views.oauth_client_test, {"action": "login"}),
    path("oauth_client/callback/", geno_views.oauth_client_test, {"action": "callback"}),
    path("oauth_client/test/", geno_views.oauth_client_test, {"action": "access"}),
    path("preview/", geno_views.preview_template),
]
