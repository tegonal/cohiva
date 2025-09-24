from django.urls import path, re_path

from . import views as geno_views

app_name = "geno"
urlpatterns = [
    re_path(r"^import/([a-z_-]+)/?$", geno_views.import_generic),
    re_path(r"^export/([a-z_-]+)/?$", geno_views.export_generic),
    re_path(r"^documents/([a-z_-]+)/([0-9]+)/([a-z_-]+)/?$", geno_views.documents),
    # path("share/overview/", geno_views.share_overview, name="share_overview"),
    # path("share/overview/", login_required(geno_views.ShareOverviewView.as_view()), name="share_overview"),
    path("share/overview/", geno_views.ShareOverviewView.as_view(), name="share_overview"),
    path("share/overview/plot/", geno_views.share_overview_boxplot),
    path("share/export/", geno_views.share_export),
    path("share/confirm/", geno_views.share_confirm),
    re_path(
        r"^share/statement/(?P<date>[a-z0-9_-]+)/(?P<address>[0-9]+)/?$",
        geno_views.share_statement,
    ),
    re_path(r"^share/statement/(?P<date>[a-z0-9_-]+)/?$", geno_views.share_statement),
    path("share/mailing/", geno_views.share_mailing),
    path("share/interest/download/", geno_views.share_interest_download),
    path("share/interest/transactions/", geno_views.share_interest_transactions),
    path("share/check/", geno_views.share_check),
    path("share/duedate_reminder/", geno_views.share_duedate_reminder),
    path("member/overview/", geno_views.member_overview),
    path("member/overview/plot/", geno_views.member_overview_plot),
    path("member/list/", geno_views.member_list),
    path("member/list_admin/", geno_views.member_list_admin),
    # path("member/check_mailinglists/", geno_views.check_mailinglists, name="check_mailinglists"),
    # path("member/check_mailinglists/", login_required(geno_views.CheckMailinglistsView.as_view()), name="check_mailinglists"),
    path("member/check_payments/", geno_views.check_payments),
    path("member/send_mail/", geno_views.send_member_mail),
    path("member/send_mail/select/", geno_views.send_member_mail_select),
    path("member/send_mail/action/", geno_views.send_member_mail_action),
    path("member/send_mail/contract/", geno_views.send_contract_mail),
    re_path(r"^member/confirm/([a-z_-]+)/?$", geno_views.member_confirm),
    path("address/export/", geno_views.address_export, name="address_export"),
    path("maintenance/", geno_views.run_maintenance_tasks),
    path("maintenance/check_portal_users/", geno_views.check_portal_users),
    path("maintenance/check_duplicate_invoices/", geno_views.check_duplicate_invoices),
    path("transaction/", geno_views.transaction),
    path("transaction_upload/", geno_views.transaction_upload),
    path("transaction_upload/process/", geno_views.transaction_upload_process),
    path("transaction_testdata/", geno_views.transaction_testdata),
    path("transaction_invoice/", geno_views.transaction_invoice),
    path("invoice/", geno_views.invoice_manual),
    path("invoice/auto/", geno_views.invoice),
    re_path(
        r"^invoice/download/(?P<key_type>[a-z_-]+)/(?P<key>[0-9]+)/?$",
        geno_views.invoice,
        {"action": "download"},
    ),
    path("invoice/overview/", geno_views.invoice, {"action": "overview"}),
    path(
        "invoice/overview/all/", geno_views.invoice, {"action": "overview", "consolidate": False}
    ),
    re_path(
        r"^invoice/detail/(?P<key_type>[cp])/(?P<key>[0-9]+)/?$",
        geno_views.invoice,
        {"action": "detail"},
    ),
    re_path(
        r"^invoice/detail/(?P<key_type>[cp])/(?P<key>[0-9]+)/all/?$",
        geno_views.invoice,
        {"action": "detail", "consolidate": False},
    ),
    path("contract/create/", geno_views.create_contracts),
    path("contract/create_letter/", geno_views.create_contracts, {"letter": True}),
    path(
        "contract/create_documents/check/",
        geno_views.create_documents,
        {"default_doctype": "contract_check"},
    ),
    path("rental/tenants/", geno_views.rental_unit_list_tenants),
    path("rental/units/", geno_views.rental_unit_list_units),
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
