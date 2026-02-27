import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Row
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.widgets import (
    UnfoldAdminDateWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelect2MultipleWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldBooleanSwitchWidget,
)

import geno.settings as geno_settings
from geno.layout_helpers import UnfoldSeparator
from geno.utils import send_error_mail

from .models import (
    Address,
    Building,
    ContentTemplate,
    Contract,
    GenericAttribute,
    Invoice,
    InvoiceCategory,
    MemberAttribute,
    MemberAttributeType,
    Registration,
    RegistrationEvent,
    RegistrationSlot,
)


class TransactionForm(forms.Form):
    # Transaction types are loaded from centralized module
    from geno.transaction_types import get_manual_transaction_types

    transaction = forms.ChoiceField(
        choices=get_manual_transaction_types(),
        label="Buchungstyp",
        widget=UnfoldAdminSelectWidget(),
    )
    name = forms.ModelChoiceField(
        queryset=Address.objects.filter(active=True),
        label="Name",
        widget=UnfoldAdminSelect2Widget(),
    )
    date = forms.DateField(label="Datum", widget=UnfoldAdminDateWidget())
    amount = forms.DecimalField(
        label="Betrag",
        decimal_places=2,
        required=False,
        widget=UnfoldAdminDecimalFieldWidget(),
        help_text="",
    )
    note = forms.CharField(
        label="Kommentar",
        required=False,
        widget=UnfoldAdminTextareaWidget(attrs={"rows": 2}),
        help_text="(optional)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Crispy Forms helper for Unfold styling
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("transaction", css_class="mb-4"),
            Div("name", css_class="mb-4"),
            Div("date", css_class="mb-4"),
            Div("amount", css_class="mb-4"),
            Div("note", css_class="mb-4"),
        )

    def clean_amount(self):
        """Validate that amount is positive if provided."""
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Betrag muss grösser als 0 sein.")
        return amount

    def clean_date(self):
        """Validate that date is not in the future."""
        date = self.cleaned_data.get("date")
        if date and date > datetime.date.today():
            raise forms.ValidationError("Datum darf nicht in der Zukunft liegen.")
        return date


class TransactionFormInvoice(forms.Form):
    invoice = forms.ModelChoiceField(
        queryset=Invoice.objects.filter(active=True)
        .filter(consolidated=False)
        .filter(invoice_type="Invoice"),
        label="Rechnung",
        widget=UnfoldAdminSelect2Widget(),
    )
    date = forms.DateField(label="Datum", widget=UnfoldAdminDateWidget())
    amount = forms.DecimalField(
        label="Betrag",
        decimal_places=2,
        min_value=0.01,
        required=False,
        widget=UnfoldAdminDecimalFieldWidget(),
        help_text="(nur ausfüllen, falls abweichend von Rechnung)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Crispy Forms helper for Unfold styling
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("invoice", css_class="mb-4"),
            Div("date", css_class="mb-4"),
            Div("amount", css_class="mb-4"),
        )

    def clean(self):
        """Cross-field validation for invoice payment."""
        cleaned_data = super().clean()
        invoice = cleaned_data.get("invoice")
        date = cleaned_data.get("date")

        if not invoice:
            self.add_error("invoice", "Bitte eine Rechnung auswählen.")
            return cleaned_data

        if date and invoice.date and date < invoice.date:
            formatted_date = date_format(invoice.date, format="SHORT_DATE_FORMAT")
            self.add_error(
                "date", f"Datum darf nicht vor Rechnungsdatum ({formatted_date}) liegen."
            )

        if date and date > datetime.date.today():
            self.add_error("date", "Datum darf nicht in der Zukunft liegen.")

        return cleaned_data


class MemberMailForm(forms.Form):
    def get_attribute_value_choices(self):
        from django.utils.translation import gettext_lazy as _

        choices_attval = [("--OHNE--", _("ist nicht vorhanden"))]
        for v in (
            MemberAttribute.objects.order_by("value").values_list("value", flat=True).distinct()
        ):
            choices_attval.append((v, _("ist {}").format(v)))
        return choices_attval

    def __init__(self, *args, **kwargs):
        from crispy_forms.helper import FormHelper
        from crispy_forms.layout import HTML, Div, Layout
        from django.utils.translation import gettext_lazy as _

        from geno.layout_helpers import (
            CollapsibleSection,
            ConditionalDiv,
            UnfoldSectionHeading,
            UnfoldSeparator,
        )

        super().__init__(*args, **kwargs)
        self.fields["select_attributeA_value"] = forms.ChoiceField(
            choices=self.get_attribute_value_choices(),
            label=_("Wert"),
            required=False,
            widget=UnfoldAdminSelectWidget(),
        )
        self.fields["select_attributeB_value"] = forms.ChoiceField(
            choices=self.get_attribute_value_choices(),
            label=_("Wert"),
            required=False,
            widget=UnfoldAdminSelectWidget(),
        )
        for v in (
            GenericAttribute.objects.order_by("name").values_list("name", flat=True).distinct()
        ):
            self.fields["filter_genattribute"].choices.append((v, v))
            self.fields["filter_genattribute"].widget.choices.append((v, v))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("base_dataset", css_class="mb-4"),
            ConditionalDiv(
                "member-filters",
                UnfoldSeparator(),
                UnfoldSectionHeading(_("Mitglieder-Filter")),
                CollapsibleSection(
                    _("Mitglieder-Attribute"),
                    Div(
                        HTML(
                            '<p class="text-xs font-medium text-gray-500 mb-2">{}</p>'.format(
                                _("Filter A")
                            )
                        ),
                        Div(
                            Div("select_attributeA", css_class="mb-4"),
                            Div("select_attributeA_value", css_class="mb-4"),
                            css_class="p-3 border border-base-200 dark:border-base-800 rounded",
                        ),
                        css_class="mb-4",
                    ),
                    Div(
                        HTML(
                            '<p class="text-xs font-medium text-gray-500 mb-2">{}</p>'.format(
                                _("Filter B")
                            )
                        ),
                        Div(
                            Div("select_attributeB", css_class="mb-4"),
                            Div("select_attributeB_value", css_class="mb-4"),
                            css_class="p-3 border border-base-200 dark:border-base-800 rounded",
                        ),
                        css_class="mb-4",
                    ),
                    collapsed=True,
                ),
                CollapsibleSection(
                    _("Weitere Filter"),
                    Div("select_flag_01", css_class="mb-4"),
                    Div("select_flag_02", css_class="mb-4"),
                    Div("select_flag_03", css_class="mb-4"),
                    Div("select_flag_04", css_class="mb-4"),
                    Div("select_flag_05", css_class="mb-4"),
                    Div("ignore_join_date", css_class="mb-4"),
                    *(
                        [
                            Div("share_paid_01", css_class="mb-4"),
                            Div("share_unpaid", css_class="mb-4"),
                        ]
                        if settings.GENO_ID == "HSG"
                        else []
                    ),
                    collapsed=True,
                ),
                initial_display="none",
            ),
            ConditionalDiv(
                "renter-filters",
                UnfoldSeparator(),
                UnfoldSectionHeading(_("Mietobjekt-Filter")),
                Div("select_rentaltype", css_class="mb-4"),
                CollapsibleSection(
                    _("Allgemeine Attribute"),
                    Div("filter_genattribute", css_class="mb-4"),
                    Div("filter_genattribute_value", css_class="mb-4"),
                    collapsed=True,
                ),
                Div("include_subcontracts", css_class="mb-4"),
                Div("filter_building", css_class="mb-4"),
                initial_display="none",
            ),
            ConditionalDiv(
                "share-filters",
                UnfoldSeparator(),
                UnfoldSectionHeading(_("Beteiligungen-Filter")),
                Div("select_sharetype", css_class="mb-4"),
                Div("select_document", css_class="mb-4"),
                initial_display="none",
            ),
            UnfoldSeparator(),
            UnfoldSectionHeading(_("Rechnungen-Filter")),
            Div("filter_invoice", css_class="mb-4"),
            ConditionalDiv(
                "invoice-detail-filters",
                Div("filter_invoice_category", css_class="mb-4"),
                Div("filter_invoice_consolidated", css_class="mb-4"),
                Div("filter_invoice_daterange_min", css_class="mb-4"),
                Div("filter_invoice_daterange_max", css_class="mb-4"),
                initial_display="none",
            ),
        )

    rentaltype_choices = [
        ("all", _("Alle Mietenden inkl. Gewerbe/Lager/PP")),
        ("all_nobusiness", _("Alle Bewohnenden exkl. Gewerbe/Lager/PP")),
        ("Wohnung", _("Wohnungen bis 6.5Zi.")),
        ("Grosswohnung", _("Grosswohnungen ab 7Zi. (ohne Selbstausbau)")),
        ("Selbstausbau", _("Selbstausbau")),
        ("Gewerbe", _("Gewerbemietende")),
    ]

    document_choices = [
        ("none", ""),
        ("nostatement", _("Kein Kontoauszug in den letzten 6 Monaten")),
    ]

    sharetype_choices = [
        ("none", ""),
        ("shares", _("Nur Anteilscheine")),
        ("loan_deposit", _("Nur Darlehen+Deposito")),
        ("with_interest", _("Nur verzinste Darlehen+Deposito")),
    ]

    boolean_choices = [
        ("none", ""),
        ("true", _("Muss gesetzt sein")),
        ("false", _("Ausschliessen")),
    ]

    base_dataset_choices = [
        ("active_members", _("Alle aktuellen Mitglieder")),
        ("renters", _("Alle aktuellen Mieter")),
        ("shares", _("Alle Personen mit Beteiligungen (ohne Hypothek/Spezial)")),
        ("addresses", _("Alle aktiven Adressen/Kontakte")),
    ]

    base_dataset = forms.ChoiceField(
        choices=base_dataset_choices,
        label=_("Basis-Datensatz"),
        required=True,
        help_text=_("Diese Auswahl kann ggf. mit den Filtern unten noch eingeschränkt werden"),
        widget=UnfoldAdminSelectWidget(),
    )
    select_attributeA = forms.ModelChoiceField(
        queryset=MemberAttributeType.objects.all(),
        label=_("Attribut"),
        required=False,
        empty_label=_("Bitte ein Attribut wählen"),
        widget=UnfoldAdminSelectWidget(),
    )
    select_attributeA_value = forms.ChoiceField(choices=[], label=_("Filter A - Attribut-Wert"))
    select_attributeB = forms.ModelChoiceField(
        queryset=MemberAttributeType.objects.all(),
        label=_("Attribut"),
        required=False,
        empty_label=_("Bitte ein Attribut wählen"),
        widget=UnfoldAdminSelectWidget(),
    )
    select_attributeB_value = forms.ChoiceField(choices=[], label=_("Filter B - Attribut-Wert"))
    select_flag_01 = forms.ChoiceField(
        choices=boolean_choices,
        label=geno_settings.MEMBER_FLAGS[1],
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    select_flag_02 = forms.ChoiceField(
        choices=boolean_choices,
        label=geno_settings.MEMBER_FLAGS[2],
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    select_flag_03 = forms.ChoiceField(
        choices=boolean_choices,
        label=geno_settings.MEMBER_FLAGS[3],
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    select_flag_04 = forms.ChoiceField(
        choices=boolean_choices,
        label=geno_settings.MEMBER_FLAGS[4],
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    select_flag_05 = forms.ChoiceField(
        choices=boolean_choices,
        label=geno_settings.MEMBER_FLAGS[5],
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    if settings.GENO_ID == "HSG":
        share_paid_01 = forms.BooleanField(
            label=_("Nur Mitglieder MIT bezahltem Anteilschein Einzelmitglied"),
            required=False,
            widget=UnfoldBooleanSwitchWidget(),
        )
        share_unpaid = forms.BooleanField(
            label=_("Nur Mitglieder OHNE Anteilscheine"),
            required=False,
            widget=UnfoldBooleanSwitchWidget(),
        )
    select_rentaltype = forms.ChoiceField(
        choices=rentaltype_choices,
        label=_("Typ"),
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    select_document = forms.ChoiceField(
        choices=document_choices,
        label=_("Dokumente"),
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    select_sharetype = forms.ChoiceField(
        choices=sharetype_choices,
        label=_("Typ"),
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    ignore_join_date = forms.DateField(
        label=_("Beitritts-Datum älter als"),
        required=False,
        widget=UnfoldAdminDateWidget(),
    )
    filter_genattribute = forms.ChoiceField(
        choices=[
            ("none", ""),
        ],
        label=_("Attribut"),
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    filter_genattribute_value = forms.CharField(
        label=_("Allg. Attribut-Wert"),
        required=False,
        help_text=_("--OHNE-- eingeben für keinen Wert"),
        initial="--OHNE--",
        widget=UnfoldAdminTextInputWidget(),
    )
    filter_invoice_choices = (
        ("none", ""),
        (
            "include",
            _("eine passende Rechnung existiert"),
        ),
        (
            "exclude",
            _("keine passende Rechnung existiert"),
        ),
    )
    filter_invoice = forms.ChoiceField(
        choices=filter_invoice_choices,
        label=_("Empfänger:in nur einschliessen, falls"),
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    filter_invoice_category = forms.ModelChoiceField(
        queryset=InvoiceCategory.objects.filter(active=True),
        label=_("Rechnungstyp"),
        required=False,
        empty_label="",
        widget=UnfoldAdminSelectWidget(),
    )
    filter_invoice_consolidate_choices = (
        ("none", ""),
        ("true", _("Nur konsolidierte Rechnungen")),
        ("false", _("Nur NICHT konsolidierte Rechnungen")),
    )
    filter_invoice_consolidated = forms.ChoiceField(
        choices=filter_invoice_consolidate_choices,
        label=_("Rechnung konsolidiert"),
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    filter_invoice_daterange_max = forms.DateField(
        label=_("Rechnungsdatum älter als"),
        required=False,
        help_text=_("Leer lassen für alle"),
        widget=UnfoldAdminDateWidget(),
    )
    filter_invoice_daterange_min = forms.DateField(
        label=_("Rechnungsdatum jünger als"),
        required=False,
        help_text=_("Leer lassen für alle"),
        widget=UnfoldAdminDateWidget(),
    )
    include_subcontracts = forms.BooleanField(
        label=_("Unterverträge einbeziehen"),
        required=False,
        widget=UnfoldBooleanSwitchWidget(),
    )

    filter_building = forms.ModelMultipleChoiceField(
        label=_("Mit Vertrag in Liegenschaft(en)"),
        required=False,
        queryset=Building.objects.filter(active=True).order_by("name"),
        widget=UnfoldAdminSelect2MultipleWidget(),
        help_text=_("Tippen um zu suchen, mehrere Einträge möglich"),
    )


class MemberMailSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        from crispy_forms.helper import FormHelper
        from crispy_forms.layout import Div, Layout
        from django.contrib.admin.widgets import FilteredSelectMultiple
        from django.utils.translation import gettext_lazy as _

        members = kwargs.pop("members")
        super().__init__(*args, **kwargs)
        choices = []
        for m in members:
            if m["id"] and m["member"]:
                choices.append((m["id"], m["member"]))
        self.fields["select_members"] = forms.MultipleChoiceField(
            choices=choices,
            label=_("Empfänger auswählen"),
            widget=FilteredSelectMultiple(
                verbose_name=_("Empfänger"),
                is_stacked=False,
                attrs={"size": "20"},
            ),
        )

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("select_members", css_class="mb-4"),
        )


class MemberMailActionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        from crispy_forms.helper import FormHelper
        from crispy_forms.layout import HTML, Div, Layout
        from django.utils.translation import gettext_lazy as _

        from geno.layout_helpers import ConditionalDiv, UnfoldSectionHeading, UnfoldSeparator

        super().__init__(*args, **kwargs)
        choices = []
        ## Add ContentTemplates
        for template in ContentTemplate.objects.filter(
            active=True, template_type__in=["OpenDocument", "File"], manual_creation_allowed=True
        ).order_by("-template_type", "name"):
            choices.append(
                (
                    f"ContentTemplate:{template.id}",
                    f"{template.name} [{template.template_type} Vorlage]",
                )
            )
        ## Add DocumentTypes
        ## TODO: Code is not really ready for this now. And not even sure if we want to be able to create documents this way.
        # for doctype in DocumentType.objects.filter(active=True, template__active=True, template__manual_creation_allowed=True):
        #    choices.append( (f'DocumentType:{doctype.id}', f"Dokument «{doctype.description}» (erzeugt auch ein Dokument-Objekt {doctype.name})") )

        self.fields["template_files"] = forms.MultipleChoiceField(
            choices=choices,
            label=_("Vorlagen Dokumente/Anhänge"),
            widget=UnfoldAdminSelect2MultipleWidget(),
            required=False,
            help_text=_("Tippen um zu suchen, mehrere Einträge möglich"),
        )

        template_mail_choices = []
        try:
            for template in (
                ContentTemplate.objects.filter(active=True)
                .filter(template_type="Email")
                .order_by("name")
            ):
                template_mail_choices.append(("template_id_%s" % template.id, template.name))
        except:
            print("WARNING: Could not load ContentTemplates.")
            send_error_mail("MemberMailActionForm", "Could not load ContentTemplates")
        self.fields["template_mail"] = forms.ChoiceField(
            label=_("Vorlage"),
            choices=template_mail_choices,
            required=False,
            widget=UnfoldAdminSelectWidget(),
        )

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("action", css_class="mb-4"),
            UnfoldSeparator(),
            UnfoldSectionHeading(_("Dokumente")),
            Div("template_files", css_class="mb-4"),
            UnfoldSeparator(),
            UnfoldSectionHeading(_("E-Mail")),
            Div("send_email", css_class="mb-4"),
            ConditionalDiv(
                "email-settings",
                Div("template_mail", css_class="mb-4"),
                Div("subject", css_class="mb-4"),
                Div("email_sender", css_class="mb-4"),
                Div("email_copy", css_class="mb-4"),
                initial_display="none",
            ),
            UnfoldSeparator(),
            UnfoldSectionHeading(_("Attribute ändern")),
            HTML(
                '<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{}</p>'.format(
                    _(
                        "Setzt oder aktualisiert ein Attribut bei allen ausgewählten "
                        "Empfängern. Bestehende Werte werden überschrieben."
                    )
                )
            ),
            Div("change_attributes", css_class="mb-4"),
            ConditionalDiv(
                "attribute-settings",
                Div(
                    HTML(
                        '<p class="text-xs font-medium text-gray-500 mb-2">{}</p>'.format(
                            _("Mitglieder-Attribut")
                        )
                    ),
                    Div(
                        Div("change_attribute", css_class="mb-4"),
                        Div("change_attribute_value", css_class="mb-4"),
                        css_class="p-3 border border-base-200 dark:border-base-800 rounded",
                    ),
                    css_class="mb-4",
                ),
                Div(
                    HTML(
                        '<p class="text-xs font-medium text-gray-500 mb-2">{}</p>'.format(
                            _("Allgemeines Attribut")
                        )
                    ),
                    Div(
                        Div("change_genattribute", css_class="mb-4"),
                        Div("change_genattribute_value", css_class="mb-4"),
                        css_class="p-3 border border-base-200 dark:border-base-800 rounded",
                    ),
                    css_class="mb-4",
                ),
                initial_display="none",
            ),
        )

    action = forms.ChoiceField(
        label=_("Aktion"),
        choices=[
            ("list", _("Liste anzeigen / nur Attribute ändern")),
            ("list_xls", _("Liste als XLS herunterladen / nur Attribute ändern")),
            ("makezip", _("ZIP-File mit Dokumenten erzeugen (odt)")),
            ("makezip_pdf", _("ZIP-File mit Dokumenten erzeugen (pdf)")),
            ("mail", _("Mails mit Text und evtl. Anhang verschicken")),
            ("mail_test", _("Test-Mails nur an Kopie-Adresse verschicken")),
        ],
        widget=UnfoldAdminSelectWidget(),
    )

    send_email = forms.BooleanField(
        label=_("E-Mail versenden"),
        required=False,
        widget=UnfoldBooleanSwitchWidget(),
    )

    subject = forms.CharField(
        label=_("Betreff"),
        required=False,
        widget=UnfoldAdminTextInputWidget(),
    )
    default_email_sender = f'"{settings.GENO_NAME}" <{settings.GENO_DEFAULT_EMAIL}>'
    email_sender_choices = [(default_email_sender, default_email_sender)]
    if hasattr(settings, "GENO_EXTRA_EMAIL_SENDER_CHOICES"):
        for email_sender in settings.GENO_EXTRA_EMAIL_SENDER_CHOICES:
            email_sender_choices.append((email_sender, email_sender))
    email_sender = forms.ChoiceField(
        label=_("Absender"),
        choices=email_sender_choices,
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    email_copy = forms.EmailField(
        label=_("Kopie (Bcc) an"),
        required=False,
        help_text=_("Leer lassen, falls keine Kopie gewünscht"),
        widget=UnfoldAdminTextInputWidget(attrs={"type": "email"}),
    )
    change_attributes = forms.BooleanField(
        label=_("Attribute ändern"),
        required=False,
        widget=UnfoldBooleanSwitchWidget(),
    )
    change_attribute = forms.ModelChoiceField(
        queryset=MemberAttributeType.objects.all(),
        label=_("Attribut"),
        required=False,
        empty_label="",
        widget=UnfoldAdminSelectWidget(),
    )
    change_attribute_value = forms.CharField(
        label=_("Wert"),
        required=False,
        widget=UnfoldAdminTextInputWidget(),
    )
    change_genattribute = forms.CharField(
        label=_("Name"),
        required=False,
        help_text=_("Name eines allgemeinen Attributs eingeben"),
        widget=UnfoldAdminTextInputWidget(),
    )
    change_genattribute_value = forms.CharField(
        label=_("Wert"),
        required=False,
        widget=UnfoldAdminTextInputWidget(),
    )

    def clean(self):
        cleaned_data = super().clean()

        cl_action = cleaned_data.get("action")
        cl_template_file = cleaned_data.get("template_file")
        cl_template_mail = cleaned_data.get("template_mail")
        cl_subject = cleaned_data.get("subject")
        cl_email_copy = cleaned_data.get("email_copy")
        cl_email_sender = cleaned_data.get("email_sender")
        cl_change_attribute = cleaned_data.get("change_attribute")
        cl_change_attribute_value = cleaned_data.get("change_attribute_value")
        cl_change_genattribute = cleaned_data.get("change_genattribute")
        cl_change_genattribute_value = cleaned_data.get("change_genattribute_value")
        from django.utils.translation import gettext_lazy as _

        if cl_action == "makezip" or cl_action == "makezip_pdf":
            if cl_template_file == "none":
                raise forms.ValidationError(
                    _("Für diese Aktion muss eine Vorlage für das Dokument ausgewählt werden")
                )
        if cl_action == "mail" or cl_action == "mail_test":
            if cl_template_mail == "none":
                raise forms.ValidationError(
                    _("Für diese Aktion muss eine Vorlage für das E-Mail ausgewählt werden")
                )
            if len(cl_subject) < 3:
                raise forms.ValidationError(
                    _("Für diese Aktion muss ein E-Mail-Betreff eingegeben werden")
                )
            if cl_email_sender == "none":
                raise forms.ValidationError(
                    _("Für diese Aktion muss ein E-Mail-Absender ausgewählt werden")
                )
            if cl_action == "mail_test" and len(cl_email_copy) < 3:
                raise forms.ValidationError(
                    _("Für diese Aktion muss eine Kopie-E-Mail-Adresse eingegeben werden")
                )
        if cl_change_attribute is not None and len(cl_change_attribute_value) < 1:
            raise forms.ValidationError(_("Der Mitglieder-Attribut-Wert ist leer"))
        if len(cl_change_genattribute) and len(cl_change_genattribute_value) < 1:
            raise forms.ValidationError(_("Der Allg. Attribut-Wert ist leer"))


class RegistrationFormSlotField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        ## Work around select2 problem (ugly... TODO: find a better solution (with django-select2 instead of django-select2-forms or Django's autocomplete_fields?)
        kwargs.pop("js_options", None)
        kwargs.pop("model", None)
        kwargs.pop("ajax", None)
        kwargs.pop("name", None)
        kwargs.pop("search_field", None)

        kwargs["empty_label"] = None
        kwargs["label"] = ""
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        n_registered = Registration.objects.filter(slot=obj).count()
        if obj.max_places >= 0:
            n_free = obj.max_places - n_registered
            if n_free > 0:
                if n_free == 1:
                    n_txt = "1 Platz"
                else:
                    n_txt = "%s Plätze" % (n_free)
                if obj.event.show_counter:
                    place_info = " (noch %s frei)" % (n_txt)
                else:
                    place_info = ""
            else:
                place_info = " (AUSGEBUCHT!)"
        else:
            if n_registered == 1:
                n_txt = "1 Anmeldung"
            else:
                n_txt = "%s Anmeldungen" % (n_registered)
            if obj.event.show_counter:
                place_info = " (bisher %s)" % (n_txt)
            else:
                place_info = ""
        return "%s%s" % (obj.get_slot_text(), place_info)


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = (
            "slot",
            "first_name",
            "name",
            "email",
            "telephone",
            "check1",
            "check2",
            "check3",
            "check4",
            "check5",
            "text1",
            "text2",
            "text3",
            "text4",
            "text5",
            "notes",
        )

        field_classes = {
            "slot": RegistrationFormSlotField,
        }
        widgets = {
            "slot": forms.RadioSelect(),
        }

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not event.enable_notes:
            self.fields["notes"].widget = forms.widgets.HiddenInput()
        if event.enable_telephone:
            self.fields["telephone"].required = True
        else:
            self.fields["telephone"].widget = forms.widgets.HiddenInput()
        for f in (
            "check1",
            "check2",
            "check3",
            "check4",
            "check5",
            "text1",
            "text2",
            "text3",
            "text4",
            "text5",
        ):
            label = getattr(event, "%s_label" % f)
            if label:
                self.fields[f].label = label
            else:
                self.fields[f].widget = forms.widgets.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        cl_email = cleaned_data.get("email")
        cl_slot = cleaned_data.get("slot")
        if Registration.objects.filter(slot__event=cl_slot.event).filter(email=cl_email).count():
            raise forms.ValidationError("Es gibt bereits eine Anmeldung mit dieser Email-Adresse!")
        if cl_slot.max_places >= 0:
            n_free = cl_slot.max_places - Registration.objects.filter(slot=cl_slot).count()
            if n_free < 1:
                raise forms.ValidationError("Dieser Termin ist bereits ausgebucht!")


def process_registration_forms(request, selector="internal"):
    form_data = []
    if selector == "internal":
        events = RegistrationEvent.objects.filter(publication_type="internal")
        action_url = "/intern/anmeldung"
    else:
        events = RegistrationEvent.objects.filter(pk=selector).exclude(publication_type="internal")
        action_url = "/anmeldung/%s" % selector
    for event in events.filter(active=True):
        start_period = None
        end_period = None
        too_early = False
        too_late = False
        if event.publication_start:
            localized_start = timezone.localtime(event.publication_start)
            start_period = date_format(localized_start, format="DATETIME_FORMAT") + " Uhr"
            if event.publication_start > timezone.now():
                too_early = True
        if event.publication_end:
            localized_end = timezone.localtime(event.publication_end)
            end_period = date_format(localized_end, format="DATETIME_FORMAT") + " Uhr"
            if event.publication_end < timezone.now():
                too_late = True
        q = (
            RegistrationSlot.objects.filter(event=event)
            .filter(name__gt=timezone.now())
            .order_by("name")
        )
        slots_available = False
        backup_slots_to_exclude = []
        for slot in q:
            if slot.max_places < 0:
                slots_available = True
            else:
                n_free = slot.max_places - Registration.objects.filter(slot=slot).count()
                if n_free > 0:
                    slots_available = True
                    ## Remove backup slots that have no registrations yet, since there are still free slots available
                    s = slot
                    while hasattr(s, "backup_slot"):
                        s = s.backup_slot
                        if Registration.objects.filter(slot=s).count() == 0:
                            backup_slots_to_exclude.append(s.pk)
        q = q.exclude(pk__in=backup_slots_to_exclude)
        if q.count():
            reg_id = request.POST.get("reg_id", None)
            if request.method == "POST" and int(reg_id) == event.pk:
                form = RegistrationForm(event, request.POST)
                if form.is_valid():
                    try:
                        form.save()
                        form.success = True
                    except:
                        send_error_mail(
                            "process_registration_forms()", "Failed to save registration"
                        )
                    if event.confirmation_mail_sender:
                        ## Send confirmation Email
                        if settings.GENO_FORMAL:
                            msg = (
                                "Hallo %s %s\n\nSie haben sich für den Anlass «%s» am %s angemeldet.\n\n%s"
                                % (
                                    form.cleaned_data["first_name"],
                                    form.cleaned_data["name"],
                                    event.name,
                                    form.cleaned_data["slot"].get_slot_text(),
                                    event.confirmation_mail_text,
                                )
                            )
                        else:
                            msg = (
                                "Hallo %s\n\nDu hast dich für den Anlass «%s» am %s angemeldet.\n\n%s"
                                % (
                                    form.cleaned_data["first_name"],
                                    event.name,
                                    form.cleaned_data["slot"].get_slot_text(),
                                    event.confirmation_mail_text,
                                )
                            )
                        subject = "Anmeldung %s" % event.name
                        if settings.DEBUG:
                            recipient = settings.TEST_MAIL_RECIPIENT
                        else:
                            recipient = form.cleaned_data["email"]
                        if send_mail(
                            subject,
                            msg,
                            event.confirmation_mail_sender,
                            [recipient],
                            fail_silently=True,
                        ):
                            form.confirmation_email = (
                                "Eine Bestätigung wurde an %s geschickt." % recipient
                            )
                        else:
                            send_error_mail(
                                "process_registration_forms()",
                                "Failed to send confirmation to %s" % recipient,
                            )
            else:
                if request.user.is_authenticated and request.user.username != "mitglied":
                    init = {
                        "email": request.user.email,
                        "name": request.user.last_name,
                        "first_name": request.user.first_name,
                    }
                    if hasattr(request.user, "address"):
                        init["telephone"] = request.user.address.telephone
                else:
                    init = {}
                form = RegistrationForm(event, initial=init)
            form.fields["slot"].queryset = q
            if q.count() == 1:
                only_one_slot = True
            else:
                only_one_slot = False
            form_data.append(
                {
                    "title": event.name,
                    "description": event.description,
                    "reg_id": event.pk,
                    "slots_available": slots_available,
                    "start_period": start_period,
                    "end_period": end_period,
                    "too_early": too_early,
                    "too_late": too_late,
                    "only_one_slot": only_one_slot,
                    "action_url": action_url,
                    "form": form,
                }
            )
    return form_data


class SendInvoicesForm(forms.Form):
    SCOPE_CHOICES = [
        ("next_month", "bis Ende nächsten Monat"),
        ("this_month", "nur bis aktueller Monat"),
        ("last_month", "nur bis letzten Monat"),
    ]
    date = forms.ChoiceField(
        widget=UnfoldAdminRadioSelectWidget(),
        choices=SCOPE_CHOICES,
        label="Rechnungen für Zeitraum",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        buildingList = Building.objects.filter(active=True).order_by("name")
        buildingMapping = [(b.id, b.name) for b in buildingList]
        self.fields["buildings"] = forms.MultipleChoiceField(
            label="Liegenschaft(en)",
            required=False,
            widget=UnfoldAdminSelect2MultipleWidget(),
            choices=buildingMapping,
        )

        # Add Crispy Forms helper for Unfold styling
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("date", css_class="mb-4"),
            Div("buildings", css_class="mb-4"),
        )


class TransactionUploadForm(forms.Form):
    file = forms.FileField(
        label="Zahlungsdatei",
        required=False,
        widget=UnfoldAdminFileFieldWidget(),
        help_text="camt.053 oder camt.054 (XML) oder ZIP-Datei mit mehreren XML-Dateien",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Crispy Forms helper for Unfold styling
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("file", css_class="mb-4"),
        )


class TransactionUploadFileForm(forms.Form):
    file = forms.FileField(required=False)


class Odt2PdfForm(forms.Form):
    """Form for uploading ODT files to convert to PDF."""

    form_id = "odt2pdf-form"

    file = forms.FileField(
        label=_("ODT- oder ZIP-Datei"),
        required=True,
        help_text=_(
            "Wähle eine LibreOffice-Datei (.odt) oder eine ZIP-Datei (.odt) zum Hochladen aus."
        ),
        widget=UnfoldAdminFileFieldWidget(
            attrs={
                "accept": ".odt,.zip",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy Forms helper for stacked layout
        self.helper = FormHelper()
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("file", css_class="mb-4"),
        )

    @property
    def button_attrs(self):
        return {"form": self.form_id}


class TransactionUploadProcessForm(forms.Form):
    # Transaction types are loaded from centralized module
    from geno.transaction_types import get_upload_transaction_types

    transaction = forms.ChoiceField(
        choices=get_upload_transaction_types(),
        label="Buchungstyp",
        widget=UnfoldAdminSelectWidget(),
    )
    name = forms.ModelChoiceField(
        queryset=Address.objects.filter(active=True),
        required=False,
        label="Name",
        widget=UnfoldAdminSelect2Widget(),
    )
    note = forms.CharField(label="Mitteilung", widget=forms.HiddenInput(), required=False)
    date = forms.DateField(label="Datum", widget=UnfoldAdminDateWidget())
    amount = forms.DecimalField(
        label="Betrag", decimal_places=2, required=False, widget=UnfoldAdminDecimalFieldWidget()
    )
    extra_info = forms.CharField(
        label="Zusatzinfo", required=False, widget=UnfoldAdminTextInputWidget()
    )

    def __init__(self, *args, **kwargs):
        transaction = kwargs.pop("transaction")
        super().__init__(*args, **kwargs)

        # Add Crispy Forms helper for Unfold styling
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("transaction", css_class="mb-4"),
            Div("name", css_class="mb-4"),
            Div("date", css_class="mb-4"),
            Div("amount", css_class="mb-4"),
            Div("extra_info", css_class="mb-4"),
            Div("save_sender", css_class="mb-4"),
            Div("note", css_class="mb-4"),  # Hidden field
        )

        choices = [("IGNORE", "Nicht speichern")]
        if transaction:
            combo_amount = "%s__CHF%s" % (transaction["person"], transaction["amount"])
            combo_note = "%s__N:%s" % (transaction["person"], transaction["note"])
            combo_amount_note = "%s__CHF%s__N:%s" % (
                transaction["person"],
                transaction["amount"],
                transaction["note"],
            )
            if transaction["person"]:
                choices.append((transaction["person"], transaction["person"]))
            choices.append((combo_amount, combo_amount))
            choices.append((combo_note, combo_note))
            choices.append((combo_amount_note, combo_amount_note))
        self.fields["save_sender"] = forms.ChoiceField(
            choices=choices, label="Absender speichern", widget=UnfoldAdminSelectWidget()
        )

        guess_info = [
            "Absender nicht erkannt",
            '<span style="color:green">Gespeicherter Absender gefunden</span>',
            '<span style="color:red">Absender geraten</span>',
        ]
        if "guess_sender_state" in kwargs["initial"]:
            self.fields["name"].help_text = mark_safe(
                guess_info[kwargs["initial"]["guess_sender_state"]]
            )

    def clean(self):
        cleaned_data = super().clean()
        ttype = cleaned_data.get("transaction")
        name = cleaned_data.get("name")
        if ttype != "ignore" and ttype != "kiosk_payment" and not name:
            raise forms.ValidationError("Bitte einen Namen (Zahlungsabsender) wählen.")


class ManualInvoiceForm(forms.Form):
    category = forms.ModelChoiceField(
        label="Rechnungstyp",
        queryset=InvoiceCategory.objects.filter(active=True).filter(manual_allowed=True),
        widget=UnfoldAdminSelectWidget(),
    )
    date = forms.DateField(
        label="Rechnungsdatum",
        widget=UnfoldAdminDateWidget(),
    )
    address = forms.ModelChoiceField(
        label="Rechnungsempfänger:in",
        queryset=Address.objects.filter(active=True),
        widget=UnfoldAdminSelect2Widget(),
        required=False,
    )
    contract = forms.ModelChoiceField(
        label="Rechnungsempfänger:in/Vertrag",
        queryset=Contract.objects.filter(state="unterzeichnet"),
        widget=UnfoldAdminSelect2Widget(),
        required=False,
    )
    extra_text = forms.CharField(
        label="Zusatztext",
        help_text="(optional)",
        widget=UnfoldAdminTextareaWidget(attrs={"rows": 3}),
        required=False,
    )
    send_email = forms.BooleanField(
        label="Per Email verschicken",
        required=False,
        widget=UnfoldBooleanSwitchWidget(attrs={"form": "invoice_form"}),
        initial=False,
    )

    def __init__(self, *args, **kwargs):
        linked_object_type = kwargs.pop("linked_object_type", None)
        super().__init__(*args, **kwargs)
        # Add Crispy Forms helper for Unfold styling
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        if linked_object_type == "Contract":
            recipient_field = "contract"
        else:
            recipient_field = "address"
        self.helper.layout = Layout(
            Div("category", css_class="mb-4"),
            UnfoldSeparator(),
            Div("date", css_class="mb-4"),
            Div(recipient_field, css_class="mb-4"),
            Div("extra_text", css_class="mb-4"),
            # Note: send_email is rendered in footer submit bar, not in form content
        )

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get("address")
        contract = cleaned_data.get("contract")
        category = cleaned_data.get("category")
        if category.linked_object_type == "Contract" and not contract:
            raise forms.ValidationError(
                "Für diesen Rechnungstyp muss ein Vetrag angegeben werden, "
                "um eine Rechnung zu erstellen!"
            )
        if category.linked_object_type == "Address" and not address:
            raise forms.ValidationError(
                "Für diesen Rechnungstyp muss eine Adresse angegeben werden, "
                "um eine Rechnung zu erstellen!"
            )


class ManualInvoiceLineForm(forms.Form):
    date = forms.DateField(
        label="Datum",
        widget=UnfoldAdminDateWidget(),
        required=False,
    )
    text = forms.CharField(
        label="Beschreibung",
        max_length=50,
        min_length=3,
        widget=UnfoldAdminTextInputWidget(),
        required=False,
    )
    amount = forms.DecimalField(
        label="Betrag",
        decimal_places=2,
        widget=UnfoldAdminDecimalFieldWidget(),
        required=False,
    )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class WebstampForm(forms.Form):
    files = MultipleFileField(
        label="PDF Dateien",
        help_text="Es können mehrere Dateien ausgewählt werden. Es werden alle frankiert (erste Seite) und in einem PDF zusammengefügt.",
    )

    def __init__(self, *args, **kwargs):
        ## Add dynamic ChoiceField with available stamp types
        stamps = kwargs.pop("stamps_available")
        super().__init__(*args, **kwargs)
        choices = []
        if stamps:
            for key in sorted(stamps):
                choices.append((key, stamps[key]))
        self.fields["stamp_type"] = forms.ChoiceField(choices=choices, label="Frankierung")


class InvoiceFilterForm(forms.Form):
    search = forms.CharField(
        label="Suche",
        required=False,
        widget=UnfoldAdminTextInputWidget(
            attrs={
                "placeholder": "Vertrag, Person, Organisation...",
                "autofocus": True,
            }
        ),
    )

    category_filter_options = [
        ("_all", "Alle Rechnungen"),
        ("_contract", "Alle mit Veträgen verknüpfte Rechnungen"),
        ("_person", "Alle mit Personen/Org. verknüpfte Rechnungen"),
    ]

    category_filter = forms.ChoiceField(
        choices=category_filter_options, label="Rechnungstyp", widget=UnfoldAdminSelectWidget()
    )

    show_consolidated = forms.BooleanField(
        label="Zeige bereits konsolidierte Rechnungen",
        required=False,
        widget=UnfoldBooleanSwitchWidget(),
    )

    date_from = forms.DateField(label="Von", required=False, widget=UnfoldAdminDateWidget())

    date_to = forms.DateField(label="Bis", required=False, widget=UnfoldAdminDateWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ## Add dynamic ChoiceField with invoice categories
        for ic in InvoiceCategory.objects.filter(active=True):
            self.fields["category_filter"].choices.append((ic.id, str(ic)))
            self.fields["category_filter"].widget.choices.append((ic.id, str(ic)))

        # Add Crispy Forms helper for Unfold styling
        # Responsive grid layout: search full-width, then 2-column rows
        self.helper = FormHelper()
        self.helper.form_tag = False  # Form tag handled in template
        self.helper.form_class = ""
        self.helper.layout = Layout(
            # Row 1: Search field (full width)
            Div("search", css_class="mb-4"),
            # Row 2: Category filter + Show consolidated toggle
            Row(
                Column("category_filter", css_class="mb-4"),
                Column("show_consolidated", css_class="mb-4"),
                css_class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4",
            ),
            # Row 3: Date range
            Row(
                Column("date_from", css_class="mb-4 lg:mb-0"),
                Column("date_to", css_class="mb-4 lg:mb-0"),
                css_class="grid grid-cols-1 lg:grid-cols-2 gap-4",
            ),
        )


class ShareOverviewFilterForm(forms.Form):
    date = forms.DateField(
        label=_("Übersicht per Stichtag"),
        required=False,
        widget=UnfoldAdminDateWidget(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = ""
        self.helper.layout = Layout(
            Div("date", css_class="mb-0"),
        )


class ShareStatementForm(forms.Form):
    date = forms.DateField(
        label="Kontoauszug per",
        required=True,
        widget=UnfoldAdminDateWidget(),
    )
