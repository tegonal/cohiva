import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from django.template.loader import render_to_string

from geno.billing import get_reference_nr, render_qrbill
from geno.models import Address, GenoBase

logger = logging.getLogger("credit_accounting")


class Vendor(GenoBase):
    name = models.CharField("Name", max_length=100, unique=True)
    VENDOR_TYPE_CHOICES = (("default", "Standard"),)
    vendor_type = models.CharField(
        "Typ", max_length=50, choices=VENDOR_TYPE_CHOICES, default="default"
    )
    qr_address = models.ForeignKey(
        Address, verbose_name="Adresse für QR-Rechnung", on_delete=models.SET_NULL, null=True
    )
    qr_iban = models.CharField(
        "QR-IBAN Nummer für QR-Rechnung",
        max_length=21,
        blank=True,
        help_text="Format: CHnnnnnnnnnnnnnnnnnnn",
    )
    api_secret = models.CharField("Secret für API-Anbindung", max_length=50, blank=True)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Verkaufsstelle"
        verbose_name_plural = "Verkaufsstellen"


class VendorAdmin(GenoBase):
    name = models.ForeignKey(Address, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, verbose_name="Verkaufsstelle", on_delete=models.CASCADE)
    VENDORADMIN_ROLE_CHOICES = (("admin", "Administrator:in"),)
    role = models.CharField(
        "Typ", max_length=50, choices=VENDORADMIN_ROLE_CHOICES, default="admin"
    )
    active = models.BooleanField("Aktiv", default=True)

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    class Meta:
        verbose_name = "Verkaufsstellenadmin"
        verbose_name_plural = "Verkaufsstellenadmins"


class Account(GenoBase):
    name = models.CharField("Name", max_length=100)
    pin = models.CharField("PIN", max_length=20)
    vendor = models.ForeignKey(Vendor, verbose_name="Verkaufsstelle", on_delete=models.CASCADE)
    balance = models.DecimalField("Kontostand", max_digits=10, decimal_places=2, default=0.00)
    active = models.BooleanField("Aktiv", default=True)

    def get_active_users(self):
        users = []
        for owner in self.account_owners.all():
            if owner.owner_type == ContentType.objects.get(app_label="geno", model="address"):
                adr = owner.owner_object
                if adr.active and adr.user not in users:
                    users.append(adr.user)
            elif owner.owner_type == ContentType.objects.get(app_label="geno", model="contract"):
                for adr in owner.owner_object.contractors.all():
                    if adr.active and adr.user not in users:
                        users.append(adr.user)
        return users

    def update_balance(self, amount_delta):
        old_balance = self.balance
        if isinstance(self.balance, float):
            self.balance += float(amount_delta)
        else:
            ## Decimal
            self.balance += amount_delta
        self.save()

        ## Check for threshold triggers
        for threshold_setting in UserAccountSetting.objects.filter(
            account=self, active=True, name="notification_balance_below_amount"
        ):
            try:
                threshold = Decimal(threshold_setting.value)
            except Exception:
                logger.warning(
                    f"Invalid threshold value for account {self} / user {threshold_setting.user}: "
                    f"{threshold_setting.value}. Removing setting."
                )
                threshold_setting.delete()
                continue

            logger.debug(
                f"Checking threshold for account {self} / user {threshold_setting.user}: "
                f"old_balance={old_balance}, balance={self.balance}, threshold={threshold}"
            )
            if old_balance >= threshold and self.balance < threshold:
                if threshold_setting.user in self.get_active_users():
                    try:
                        self.notify_user(
                            "notification_balance_below_amount",
                            threshold_setting.user,
                            {"threshold": threshold},
                        )
                        logger.debug(
                            f"Sent user notification for account {self} / "
                            f"user {threshold_setting.user}."
                        )
                    except Exception as e:
                        logger.error(
                            f"Could not send user notification for account {self} / "
                            f"user {threshold_setting.user}: {e}."
                        )
                else:
                    logger.warning(
                        f"Not sending notification for account {self} / "
                        f"user {threshold_setting.user}: User is not active owner of this "
                        f"account. Removing setting (value={threshold})."
                    )
                    threshold_setting.delete()

    def create_qrbill(self):
        context = {}
        owner = self.account_owners.first()
        if self.vendor.qr_address:
            default_address = {
                "street": self.vendor.qr_address.street_name,
                "house_num": self.vendor.qr_address.house_number,
                "pcode": self.vendor.qr_address.city_zipcode,
                "city": self.vendor.qr_address.city_name,
                "country": self.vendor.qr_address.country,
            }
        else:
            default_address = {}
        if owner and isinstance(owner.owner_object, Address):
            context["qr_debtor"] = owner.owner_object
        else:
            context["qr_debtor"] = {**default_address, "name": self.name}
        if self.vendor.qr_address:
            context["qr_creditor"] = self.vendor.qr_address
        else:
            context["qr_creditor"] = {**default_address, "name": self.vendor.name}
        context["qr_account"] = self.vendor.qr_iban
        context["qr_ref_number"] = get_reference_nr(
            "app", self.pk, extra_id1=1, app_name="credit_accounting"
        )
        context["qr_amount"] = None
        context["qr_extra_info"] = f"Einzahlung {self.vendor} für {self}"
        output_pdf_file = f"qrbill_credit_accounting_{self.pk}.pdf"
        render_qrbill(
            None,
            context,
            output_pdf_file,
            base_pdf_file=(
                f"{settings.BASE_DIR}/credit_accounting/templates/credit_accounting/"
                f"{self.vendor}_Einzahlung.pdf"
            ),
        )
        return output_pdf_file

    def notify_user(self, notification_name, user, context=None):
        if not context:
            context = {
                "account": self,
                "user": user,
            }

        attachments = []
        if notification_name == "notification_balance_below_amount":
            subject = f"{self.vendor}: Saldolimite unterschritten (Konto {self.name})"
            attachments.append(
                {
                    "file": "/tmp/" + self.create_qrbill(),
                    "filename": f"QR_Rechnung_{self.vendor}_{self.name}.pdf",
                }
            )
        else:
            raise ValueError(f"Unknown notification_name: {notification_name}")

        msg_plain = render_to_string(f"credit_accounting/email_{notification_name}.txt", context)
        mail_recipient = user.address.get_mail_recipient()
        mail = EmailMultiAlternatives(
            subject, msg_plain, settings.COHIVA_APP_EMAIL_SENDER, [mail_recipient]
        )
        for att in attachments:
            with open(att["file"], "rb") as attfile:
                mail.attach(att["filename"], attfile.read())  # , 'application/pdf')
        mail.send()

    class Meta:
        verbose_name = "Konto"
        verbose_name_plural = "Konten"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["pin", "vendor"], name="unique_pin_vendor"),
            models.UniqueConstraint(fields=["name", "vendor"], name="unique_name_vendor"),
        ]


class AccountOwner(GenoBase):
    name = models.ForeignKey(
        Account, verbose_name="Konto", on_delete=models.CASCADE, related_name="account_owners"
    )
    owner_id = models.PositiveIntegerField()
    owner_type = models.ForeignKey(
        ContentType,
        verbose_name="Verknüpft mit",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_as_owner",
    )
    owner_object = GenericForeignKey("owner_type", "owner_id")

    def __str__(self):
        if self.name:
            return "%s" % self.name
        else:
            return "[Unbenannt]"

    class Meta:
        verbose_name = "Kontobesitzer:in"
        verbose_name_plural = "Kontobesitzer:innen"


class Transaction(GenoBase):
    name = models.CharField("Buchungstyp", max_length=100, default="Buchung")
    account = models.ForeignKey(
        Account, verbose_name="Konto", on_delete=models.CASCADE, db_index=True
    )
    amount = models.DecimalField(
        "Betrag",
        max_digits=10,
        decimal_places=2,
        help_text="ACHTUNG: Einkauf negativ! Gutschrift positiv.",
    )
    date = models.DateTimeField("Datum")
    description = models.CharField("Notiz", max_length=255, blank=True)
    user = models.ForeignKey(
        User, verbose_name="Benutzer:in", on_delete=models.SET_NULL, null=True
    )
    transaction_id = models.CharField("Transaktions-ID", max_length=150, db_index=True, blank=True)

    __original_amount = None
    __original_account = None

    class Meta:
        verbose_name = "Transaktion"
        verbose_name_plural = "Transaktionen"
        ordering = ["-date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_amount = self.amount
        try:
            self.__original_account = self.account
        except ObjectDoesNotExist:
            self.__original_account = None

    def update_account_balance(self, created=False, deleted=False):
        if deleted:
            logger.info(
                "Deleted transaction %s/%s [id %d] %s CHF %s (%s)"
                % (self.name, self.date, self.id, self.account, self.amount, self.description)
            )
            self.account.update_balance(-1 * self.amount)
        elif created:
            self.account.update_balance(self.amount)
        elif self.__original_account != self.account:
            logger.info(
                "Changed transaction %s/%s [id %d] %s CHF %s -> %s CHF %s (%s)"
                % (
                    self.name,
                    self.date,
                    self.id,
                    self.__original_account,
                    self.__original_amount,
                    self.account,
                    self.amount,
                    self.description,
                )
            )
            self.__original_account.update_balance(-1 * self.__original_amount)
            self.account.update_balance(self.amount)
        elif self.__original_amount != self.amount:
            logger.info(
                "Changed transaction %s/%s [id %d] %s CHF %s -> CHF %s (%s)"
                % (
                    self.name,
                    self.date,
                    self.id,
                    self.account,
                    self.__original_amount,
                    self.amount,
                    self.description,
                )
            )
            self.account.update_balance(self.amount - self.__original_amount)
        self.__original_amount = self.amount
        self.__original_account = self.account

    def save_as_copy(self):
        self.transaction_id = ""
        super().save_as_copy()


class UserAccountSetting(GenoBase):
    name = models.CharField("Name", max_length=100)
    account = models.ForeignKey(
        Account, verbose_name="Konto", on_delete=models.CASCADE, db_index=True
    )
    user = models.ForeignKey(User, verbose_name="Benutzer:in", on_delete=models.CASCADE)
    value = models.CharField("Wert", max_length=255)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Kontoeinstellung pro Benutzer"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "account", "user"], name="unique_name_account_user"
            ),
        ]


@receiver(post_save, sender=Transaction)
def _save_transaction_post(sender, instance, created, *args, **kwargs):
    instance.update_account_balance(created=created)


@receiver(post_delete, sender=Transaction)
def _delete_transaction_post(sender, instance, *args, **kwargs):
    instance.update_account_balance(deleted=True)
