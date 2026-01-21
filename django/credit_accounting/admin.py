from django.contrib import admin

from geno.admin import GenoBaseAdmin

from .models import Account, AccountOwner, Transaction, UserAccountSetting, Vendor, VendorAdmin


@admin.register(Vendor)
class VendorAdm(GenoBaseAdmin):
    model = Vendor
    fields = [
        "name",
        "vendor_type",
        "qr_iban",
        "qr_address",
        "api_secret",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "vendor_type", "active"]
    list_filter = ["active", "vendor_type"]
    search_fields = ["name", "comment"]


@admin.register(VendorAdmin)
class VendorAdminAdmin(GenoBaseAdmin):
    model = VendorAdmin
    fields = [
        "name",
        "vendor",
        "role",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "vendor", "role", "active"]
    list_filter = ["active", "role"]
    search_fields = ["name__name", "name__first_name", "vendor__name", "comment"]
    autocomplete_fields = ["name", "vendor"]


@admin.register(Account)
class AccountAdmin(GenoBaseAdmin):
    model = Account
    fields = [
        "name",
        "pin",
        "vendor",
        "balance",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["balance", "ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "vendor", "balance", "pin", "active"]
    list_filter = ["active", "vendor"]
    search_fields = ["name", "vendor__name", "comment"]
    autocomplete_fields = ["vendor"]


@admin.register(AccountOwner)
class AccountOwnerAdmin(GenoBaseAdmin):
    model = AccountOwner
    fields = [
        "name",
        ("owner_id", "owner_type"),
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "owner_object", "comment"]
    list_filter = ["owner_type"]
    search_fields = ["name__name", "comment"]
    autocomplete_fields = ["name"]


@admin.register(Transaction)
class TransactionAdmin(GenoBaseAdmin):
    model = Transaction
    fields = [
        "name",
        "account",
        "amount",
        "date",
        "description",
        "user",
        "transaction_id",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["transaction_id", "ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "account", "date", "amount"]
    list_filter = ["name", "account", "date", "user"]
    search_fields = ["name", "account__name", "description", "comment"]
    autocomplete_fields = ["account", "user"]


@admin.register(UserAccountSetting)
class UserAccountSettingAdmin(GenoBaseAdmin):
    model = UserAccountSetting
    fields = [
        "name",
        "account",
        "user",
        "value",
        "active",
        "comment",
        "ts_created",
        "ts_modified",
        "links",
        "backlinks",
    ]
    readonly_fields = ["ts_created", "ts_modified", "links", "backlinks"]
    list_display = ["name", "account", "user", "value"]
    list_filter = ["name", "active"]
    search_fields = ["name", "account__name", "comment"]
    autocomplete_fields = ["account", "user"]
