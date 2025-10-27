from django.contrib import admin

from geno.admin import GenoBaseAdmin

from .models import Account, AccountOwner, Transaction, UserAccountSetting, Vendor, VendorAdmin


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
    my_search_fields = ["name", "comment"]
    search_fields = my_search_fields


admin.site.register(Vendor, VendorAdm)


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
    my_search_fields = ["name__name", "name__first_name", "vendor__name", "comment"]
    search_fields = my_search_fields


admin.site.register(VendorAdmin, VendorAdminAdmin)


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
    my_search_fields = ["name", "vendor__name", "comment"]
    search_fields = my_search_fields


admin.site.register(Account, AccountAdmin)


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
    my_search_fields = ["name__name", "comment"]
    search_fields = my_search_fields


admin.site.register(AccountOwner, AccountOwnerAdmin)


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
    my_search_fields = ["name", "account__name", "description", "comment"]
    search_fields = my_search_fields


admin.site.register(Transaction, TransactionAdmin)


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
    my_search_fields = ["name", "account_name", "comment"]
    search_fields = my_search_fields


admin.site.register(UserAccountSetting, UserAccountSettingAdmin)
