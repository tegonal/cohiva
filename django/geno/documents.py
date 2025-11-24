import datetime
import io
import json
import logging
import os
import re
import time
import zipfile
from decimal import Decimal
from zipfile import ZipFile

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import Context, Template, loader
from django.utils.html import escape
from html2text import html2text

import geno.settings as geno_settings
from geno.billing import add_invoice, get_reference_nr, render_qrbill
from geno.exporter import export_data_to_xls
from geno.models import (
    Address,
    ContentTemplate,
    Contract,
    Document,
    DocumentType,
    GenericAttribute,
    InvoiceCategory,
    Member,
    MemberAttribute,
    MemberAttributeType,
    Share,
    ShareType,
    get_active_shares,
)
from geno.shares import get_share_statement_data
from geno.utils import fill_template_pod, nformat, odt2pdf, remove_temp_files, sanitize_filename

logger = logging.getLogger("geno")


class MailTemplate:
    def __init__(self, template, subject, sender):
        self.is_html = False
        if isinstance(template, str) and template.startswith("template_id_"):
            templ = ContentTemplate.objects.get(id=template[12:])
        else:
            templ = template
        if isinstance(templ, ContentTemplate):
            self.template = Template(
                "%s%s%s" % ("{% autoescape off %}", templ.text, "{% endautoescape %}")
            )
            self.is_html = re.search(r"<html", templ.text, re.IGNORECASE)
        elif isinstance(templ, str):
            self.template = loader.get_template(templ)
            if templ[-5:] == ".html":
                self.is_html = True
        else:
            raise TypeError(f"Unsupported type: {templ}")
        self.subject = subject
        self.sender = sender


class RenderedDocument:
    def __init__(self):
        self.file = None
        self.filename = None
        self.linked_invoice = None


class SkipRecipient(Exception):
    pass


class DocumentTemplate:
    def __init__(self, template, doctype=None, output_format=None, dry_run=False):
        self.content_template = template
        self.doctype = doctype
        self.output_format = output_format
        self.context_options = {
            "share_statement_context": False,
            "billing_context": False,
            #'add_qrbill': False
            "qrbill_account": None,
            #'qrbill_use_refnr': False,
            "qrbill_invoice_type_id": None,
            "qrbill_info": "",
            "qrbill_rental_unit_in_extra_info": False,
            "bill_text_default": None,
            "bill_amount_default": None,
            "bill_text_memberflag_01": None,
            "bill_amount_memberflag_01": None,
            "bill_text_memberflag_02": None,
            "bill_amount_memberflag_02": None,
            "bill_text_memberflag_03": None,
            "bill_amount_memberflag_03": None,
            "bill_text_memberflag_04": None,
            "bill_amount_memberflag_04": None,
            "bill_text_memberflag_05": None,
            "bill_amount_memberflag_05": None,
            "share_count_context_var": None,
            "share_count_sharetype": None,
        }
        self.update_context_options()
        self.dry_run = dry_run
        self.temp_files = []

    def __str__(self):
        return str(self.content_template)

    def update_context_options(self, content_template=None):
        if not content_template:
            content_template = self.content_template
        for opt in content_template.template_context.all():
            opt_type = opt.name
            if opt_type.name in self.context_options:
                if isinstance(self.context_options[opt_type.name], bool):
                    self.context_options[opt_type.name] = True
                else:
                    self.context_options[opt_type.name] = opt.value

    def get_context(self, recipient):
        ctx = {"qr_account": None}
        ctx.update(recipient.address.get_context())
        if self.context_options["billing_context"]:
            ctx.update(self.get_billing_context(recipient))
        if self.context_options["share_statement_context"]:
            ctx.update(self.get_share_statement_context(recipient))
        if self.context_options["qrbill_account"]:
            self.add_qrbill_context(recipient, ctx)
        return ctx

    def get_share_statement_context(self, recipient):
        statement_year = datetime.datetime.now().year - 1
        try:
            statement_data = get_share_statement_data(recipient.address, statement_year)
        except Exception as e:
            raise ValueError(f"Fehler beim Erstellen des Kontoauszugs: {e}")
        if (
            statement_data["sect_shares"]
            or statement_data["sect_loan"]
            or statement_data["sect_deposit"]
        ):
            recipient.content_object = "address"
            return statement_data
        raise SkipRecipient("Keine Beteiligungen für Kontoauszug.")

    def get_billing_context(self, recipient):
        c = {}

        ## Geforderte Beteiligungen
        shares = (
            Share.objects.filter(state="gefordert")
            .filter(name=recipient.address)
            .order_by("share_type")
        )
        c["bill"] = []
        total = 0
        for s in shares:
            if s.share_type.name == "Anteilschein":
                if s.quantity == 1:
                    suffix = ""
                else:
                    suffix = "e"
                item = "%s Anteilschein%s à %s Franken" % (
                    nformat(s.quantity, 0),
                    suffix,
                    nformat(s.value, 0),
                )
            else:
                item = s.share_type.name
            c["bill"].append((item, "Fr. %s" % (nformat(s.quantity * s.value))))
            total += s.quantity * s.value

        ## Count shares of a specific type and save number in context
        if self.context_options.get("share_count_context_var", None) and self.context_options.get(
            "share_count_sharetype", None
        ):
            c[self.context_options["share_count_context_var"]] = 0
            stype = ShareType.objects.filter(
                name=self.context_options["share_count_sharetype"]
            ).first()
            if stype:
                for share in Share.objects.filter(name=recipient.address).filter(share_type=stype):
                    c[self.context_options["share_count_context_var"]] += share.quantity

        ## Set billing information (default or based on membership flag)
        c["bill_text"] = self.context_options.get("bill_text_default", None)
        c["bill_amount"] = self.context_options.get("bill_amount_default", None)
        if recipient.member:
            ## Overwrite bill text/amount based on member flag. Flags with higher numbers take
            ## precedence. This NEEDS TO BE IMPROVED, since multiple member flags can be set and
            ## then the outcome is unclear.
            if recipient.member.flag_05 and self.context_options.get(
                "bill_text_memberflag_05", None
            ):
                c["bill_text"] = self.context_options["bill_text_memberflag_05"]
            elif recipient.member.flag_04 and self.context_options.get(
                "bill_text_memberflag_04", None
            ):
                c["bill_text"] = self.context_options["bill_text_memberflag_04"]
            elif recipient.member.flag_03 and self.context_options.get(
                "bill_text_memberflag_03", None
            ):
                c["bill_text"] = self.context_options["bill_text_memberflag_03"]
            elif recipient.member.flag_02 and self.context_options.get(
                "bill_text_memberflag_02", None
            ):
                c["bill_text"] = self.context_options["bill_text_memberflag_02"]
            elif recipient.member.flag_01 and self.context_options.get(
                "bill_text_memberflag_01", None
            ):
                c["bill_text"] = self.context_options["bill_text_memberflag_01"]

            if recipient.member.flag_05 and self.context_options.get(
                "bill_amount_memberflag_05", None
            ):
                c["bill_amount"] = self.context_options["bill_amount_memberflag_05"]
            elif recipient.member.flag_04 and self.context_options.get(
                "bill_amount_memberflag_04", None
            ):
                c["bill_amount"] = self.context_options["bill_amount_memberflag_04"]
            elif recipient.member.flag_03 and self.context_options.get(
                "bill_amount_memberflag_03", None
            ):
                c["bill_amount"] = self.context_options["bill_amount_memberflag_03"]
            elif recipient.member.flag_02 and self.context_options.get(
                "bill_amount_memberflag_02", None
            ):
                c["bill_amount"] = self.context_options["bill_amount_memberflag_02"]
            elif recipient.member.flag_01 and self.context_options.get(
                "bill_amount_memberflag_01", None
            ):
                c["bill_amount"] = self.context_options["bill_amount_memberflag_01"]

        if c["bill_text"] and c["bill_amount"]:
            ## Add bill line to totall bill
            c["bill"].append((c["bill_text"], "Fr. %s" % (nformat(float(c["bill_amount"])))))
            total += float(c["bill_amount"])

        c["bill_total"] = "Fr. %s" % (nformat(total))

        return c

    def add_qrbill_context(self, recipient, ctx):
        ctx["qr_account"] = self.context_options["qrbill_account"]
        ctx["qr_extra_info"] = Template(self.context_options["qrbill_info"]).render(Context(ctx))
        if self.context_options["qrbill_rental_unit_in_extra_info"] and recipient.contract:
            ctx["qr_extra_info"] = "%s / Whg. %s" % (
                ctx["qr_extra_info"],
                recipient.contract.list_rental_units(short=True, exclude_minor=True),
            )
        ctx["invoice"] = None
        if self.context_options["qrbill_invoice_type_id"]:
            try:
                invoice_category = InvoiceCategory.objects.get(
                    reference_id=self.context_options["qrbill_invoice_type_id"]
                )
            except:
                raise ValueError(
                    f"Rechnungs-Typ {self.context_options['qrbill_invoice_type_id']} nicht gefunden!"
                )
            if ctx["bill_amount"]:
                if not self.dry_run:
                    ctx["invoice"] = self.do_invoice_accounting(recipient, ctx, invoice_category)
                    invoice_id = ctx["invoice"].id
                else:
                    invoice_id = 9999999999
            else:
                invoice_id = 0
            ## TODO: Move get_reference_nr to InvoiceCategory and make extra_id2 configurable there.
            if invoice_category.linked_object_type == "Address":
                ref_number = get_reference_nr(
                    invoice_category,
                    recipient.address.id,
                    extra_id1=invoice_id,
                    extra_id2=ctx["jahr"],
                )
            elif invoice_category.linked_object_type == "Contract":
                if recipient.contract:
                    ref_number = get_reference_nr(
                        invoice_category,
                        recipient.contract.id,
                        extra_id1=invoice_id,
                        extra_id2=ctx["jahr"],
                    )
                else:
                    raise ValueError(
                        "Rechnungs-Typ verlangt Vertrag, aber kein Vertrag ist definiert."
                    )
            else:
                raise RuntimeError("Invalid invoice_category.linked_object_type")
        else:
            invoice_category = None
            ref_number = None
        ctx["qr_ref_number"] = ref_number
        ctx["qr_debtor"] = recipient.address
        if ctx.get("bill_amount", None):
            ctx["qr_amount"] = Decimal(ctx["bill_amount"])
        else:
            ctx["qr_amount"] = None

    ## Create Invoice => TODO: move this to a more appropriate method??
    def do_invoice_accounting(self, recipient, ctx, invoice_category):
        invoice_date = datetime.date.today()
        if ctx["qr_extra_info"]:
            description = f"{invoice_category.name} {ctx['qr_extra_info']}"
        else:
            description = invoice_category.name
        comment = f"Versand {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
        try:
            if invoice_category.linked_object_type == "Address":
                invoice = add_invoice(
                    None,
                    invoice_category,
                    description,
                    invoice_date,
                    ctx["bill_amount"],
                    address=recipient.address,
                    comment=comment,
                )
            elif invoice_category.linked_object_type == "Contract":
                invoice = add_invoice(
                    None,
                    invoice_category,
                    description,
                    invoice_date,
                    ctx["bill_amount"],
                    contract=recipient.contract,
                    comment=comment,
                )
            else:
                raise ValueError(
                    f"Unknown linked_object_type: {invoice_category.linked_object_type}"
                )
        except Exception as e:
            raise RuntimeError(
                f'Konnte Rechnung "{description}" für {recipient} nicht erstellen: {e}'
            )
        logger.info(f"   > Added Invoice object: {invoice}")
        return invoice

    def render(self, recipient):
        output = RenderedDocument()
        output.file = self.content_template.file.path
        filename_tag = sanitize_filename(
            self.content_template.name
        )  # use template name as filename tag
        if self.content_template.template_type == "OpenDocument":
            ctx = self.get_context(recipient)
            logger.info(
                " > fill template %s with context: anrede=%s, name=%s, vorname=%s, org=%s"
                % (
                    self.content_template.file.path,
                    ctx["anrede"],
                    ctx["name"],
                    ctx["vorname"],
                    ctx["organisation"],
                )
            )
            output.file = fill_template_pod(
                self.content_template.file.path, ctx, output_format="odt"
            )
            self.temp_files.append(output.file)
            if not filename_tag:
                filename_tag = os.path.splitext(os.path.basename(self.content_template.file.path))[
                    0
                ]
                logger.warning(
                    "No filename_tag using default: %s" % self.content_template.file.path
                )
            output.filename = (
                f"{recipient.address.get_filename_str()}_{filename_tag}.{self.output_format}"
            )
            if self.output_format == "pdf":
                logger.info(" > odt2pdf(%s) -> %s" % (output.file, output.filename))
                output.file = odt2pdf(output.file, "send_member_mail")
                self.temp_files.append(output.file)
                if ctx["qr_account"]:
                    output_dir = f"/tmp/documents_render_qrbill_{settings.GENO_ID}"
                    logger.info(f" > render_qrbill({output_dir}/{output.filename}")
                    render_qrbill(
                        None,
                        ctx,
                        output.filename,
                        base_pdf_file=output.file,
                        append_pdf_file=None,
                        output_dir=output_dir,
                    )
                    output.linked_invoice = ctx["invoice"]
                    output.file = f"{output_dir}/{output.filename}"
                    self.temp_files.append(output.file)
            elif self.output_format != "odt":
                raise ValueError(f"Unsupported output format: {self.output_format}")
            if not output.file:
                raise RuntimeError("Could not fill template")
        else:
            ## Just append
            logger.info(" > appending file without rendering: %s" % (output.file))
            # append file ending of output.file to filename_tag
            if not filename_tag.endswith(os.path.splitext(output.file)[1]):
                filename_tag += os.path.splitext(output.file)[1]
            output.filename = filename_tag
        return output

    def cleanup(self):
        remove_temp_files(self.temp_files)


## TODO: Make subclasses of Document
# class QRBillDocument(Document):
#    def render(self, recipient):


class Recipient:
    def __init__(self, address, member=None, contract=None, extra_info=None):
        self.address = address
        self.member = member
        self.contract = contract
        self.extra_info = extra_info
        self.skip_reason = None
        self.content_object = None
        self.documents = []
        self.log = []
        self.warning = False
        self.failure = False

    def __str__(self):
        name = str(self.address)
        if self.member:
            name = f"{name} (member)"
        if self.contract:
            name = f"{name} [{self.contract}]"
        return name

    def add_address_warnings(self):
        if len(self.address.city) < 6:
            self.warning = True
            self.log.append("WARNUNG: Keine Adresse/Ort vorhanden!")
        else:
            try:
                int(self.address.city[0:4])
            except ValueError:
                self.warning = True
                self.log.append("WARNUNG: Ungewöhnliche PLZ/Adressierung -> Adresse im Ausland?")


class ProcessDocuments:
    def __init__(self, dry_run=False):
        self.mail_template = None
        self.mail_bcc = None
        self.mail_test = True
        self.zipfile_ob = None
        self.output_format = None
        self.templates = []
        self.recipients = []
        self.contexts = {}
        self.test_email_address = None
        self.dry_run = dry_run

    def setup_mail(self, template, bcc=None):
        self.mail_template = template
        self.mail_bcc = bcc

    def setup_zip(self):
        self.file_like_object = io.BytesIO()
        self.zipfile_ob = ZipFile(self.file_like_object, "w")

    def set_output_format(self, filetype):
        self.output_format = filetype

    def add_document_template(self, att):
        try:
            (att_type, att_id) = att.split(":", 1)
        except ValueError:
            att_type = None
            att_id = None

        content_template = None
        doctype = None
        if att_type == "DocumentType":
            try:
                doctype = DocumentType.objects.get(id=att_id)
                content_template = doctype.template
            except DocumentType.DoesNotExist:
                raise ValueError(f"Dokumenttyp mit ID {att_id} nicht gefunden.")
        elif att_type == "ContentTemplate":
            try:
                content_template = ContentTemplate.objects.get(id=att_id)
            except ContentTemplate.DoesNotExist:
                raise ValueError(f"Vorlage mit ID {att_id} nicht gefunden.")
        else:
            raise TypeError(f"Unbekannter Vorlagentyp: {att}")
        self.templates.append(
            DocumentTemplate(
                content_template,
                doctype=doctype,
                output_format=self.output_format,
                dry_run=self.dry_run,
            )
        )

    def add_recipient(self, member_or_address, contract=None, extra_info=None):
        if isinstance(member_or_address, Member):
            recip = Recipient(
                member_or_address.name,
                member=member_or_address,
                contract=contract,
                extra_info=extra_info,
            )
        elif isinstance(member_or_address, Address):
            recip = Recipient(member_or_address, contract=contract, extra_info=extra_info)
        else:
            raise TypeError(f"{member_or_address} must be Member or Address.")
        self.validate_recipient(recip)
        self.recipients.append(recip)

    def validate_recipient(self, recipient):
        if self.mail_template and not recipient.address.email:
            recipient.skip_reason = "Keine Email-Adresse vorhanden."
        if (
            self.mail_template and recipient.address.paymentslip
        ):  ## TODO: rename address.paymentslip to more generic special_case or similar
            recipient.skip_reason = "Spezialfall (manuelle Bearbeitung)"

    def generate_documents(self):
        if not self.output_format:
            return
        logger.info("Generating documents from the following templates:")
        for template in self.templates:
            logger.info(f" - {template}")
        for recipient in self.recipients:
            if recipient.skip_reason:
                logger.info(f"Skipping {recipient}: {recipient.skip_reason}")
                continue
            logger.info(f"Preparing data for {recipient}")
            for template in self.templates:
                try:
                    doc = template.render(recipient)
                    recipient.documents.append(doc)
                except SkipRecipient as e:
                    logger.info(
                        f" - Skipping recipient: No document (template={template}, reason={e})"
                    )
                    recipient.skip_reason = e
                    break

    def send_output(self):
        if self.mail_template:
            self.send_output_mails()
        if self.zipfile_ob:
            self.add_documents_to_zip()

    def add_documents_to_zip(self):
        for recipient in self.recipients:
            for doc in recipient.documents:
                self.zipfile_ob.write(doc.file, doc.filename)

    def send_output_mails(self):
        logger.info("Start sending mails")
        for recipient in self.recipients:
            if recipient.skip_reason:
                recipient.warning = True
                recipient.log.append(f"KEIN EMAIL GESENDET! Grund: {recipient.skip_reason}")
            else:
                ctx = self.get_email_context(recipient)
                try:
                    mail_recipient = self.send_email(
                        recipient.address,
                        self.mail_template,
                        ctx,
                        bcc=self.mail_bcc,
                        test_to_bcc=self.dry_run,
                        attachments=recipient.documents,
                    )
                except Exception as e:
                    msg = f"Konnte mail an {recipient} nicht schicken!!! Fehler: {e}"
                    logger.error(msg)
                    recipient.failure = True
                    recipient.log.append(msg)
                if not recipient.failure:
                    logger.info(f" > Email an {mail_recipient} geschickt.")
                    recipient.log.append(f"Email an {escape(mail_recipient)} geschickt.")
                self.throttle()

    def throttle(self):
        if not getattr(settings, "IS_RUNNING_TESTS", False):
            time.sleep(0.2)

    def get_email_context(self, recipient):
        ctx = recipient.address.get_context()
        ## TODO: Make this more generic for any member attribute or generic attribute
        if self.mail_template == "geno/member_email_ausschreibung.html":
            atype = MemberAttributeType.objects.get(name="Ausschreibung Code")
            code = MemberAttribute.objects.get(member=recipient.member, attribute_type=atype)
            ctx["email_code"] = code.value
        return ctx

    ## TODO: Move/merge this with generic send-mail function?
    def send_email(
        self, address, mail_template, context, bcc=None, test_to_bcc=True, attachments=None
    ):
        if attachments is None:
            attachments = []
        bcc_recipients = None
        if test_to_bcc:
            mail_recipient = '"%s %s" <%s>' % (address.first_name, address.name, bcc)
        else:
            mail_recipient = address.get_mail_recipient()
            if bcc:
                bcc_recipients = [
                    bcc,
                ]
        mail_text_html = mail_template.template.render(Context(context))
        if mail_template.is_html:
            mail_text = html2text(mail_text_html)
        else:
            mail_text = mail_text_html
        mail = EmailMultiAlternatives(
            mail_template.subject,
            mail_text,
            mail_template.sender,
            [mail_recipient],
            bcc_recipients,
        )
        for att in attachments:
            # logger.info(" > attaching %s as %s" % (att['file'], att['filename']))
            attfile = open(att.file, "rb")
            mail.attach(att.filename, attfile.read())  # , 'application/pdf')
            attfile.close()
        if mail_template.is_html:
            mail.attach_alternative(mail_text_html, "text/html")
        mails_sent = mail.send()
        if mails_sent != 1:
            raise ValueError(f"send_email(): {mails_sent} mails sent instead of 1.")
        return mail_recipient

    def update_member_attributes(self, attribute, value):
        for recipient in self.recipients:
            if not recipient.failure and recipient.member:
                try:
                    att = MemberAttribute.objects.get(
                        member=recipient.member, attribute_type=attribute
                    )
                    old_value = att.value
                except MemberAttribute.DoesNotExist:
                    att = MemberAttribute(member=recipient.member, attribute_type=attribute)
                    old_value = "(Kein)"
                att.value = value
                att.date = datetime.date.today()
                att.save()
                recipient.log.append(
                    f'Mitglieder-Attribut "{attribute}" geändert: "{old_value}" -> "{att.value}"'
                )

    def update_generic_attributes(self, attribute, value):
        for recipient in self.recipients:
            if not recipient.failure and recipient.address:
                try:
                    att = GenericAttribute.objects.filter(addresses=recipient.address).get(
                        name=attribute
                    )
                    old_value = att.value
                except GenericAttribute.DoesNotExist:
                    att = GenericAttribute(content_object=recipient.address, name=attribute)
                    old_value = "(Kein)"
                att.value = value
                att.date = datetime.date.today()
                att.save()
                recipient.log.append(
                    f'Allg.Attribut "{attribute}" geändert: "{old_value}" -> "{att.value}"'
                )

    def get_zipfile(self):
        self.zipfile_ob.close()
        resp = HttpResponse(
            self.file_like_object.getvalue(), content_type="application/x-zip-compressed"
        )
        resp["Content-Disposition"] = "attachment; filename=%s" % "output.zip"
        return resp

    def get_xls_list(self):
        export_data = []
        export_data_fields = [
            "organization",
            "name",
            "first_name",
            "title",
            "email",
            "tel1",
            "tel2",
            "city",
            "street",
            "date_join",
            "date_leave",
            "flag_01",
            "flag_02",
            "flag_03",
            "flag_04",
            "flag_05",
            "info",
            "extra_info",
        ]
        export_data_header = [
            "Organisation",
            "Nachname",
            "Vorname",
            "Anrede",
            "Email",
            "Telefon1",
            "Telefon2",
            "PLZ Ort",
            "Adresse",
            "Beitrittsdatum",
            "Austrittsdatum",
        ]
        for i in range(1, 6):
            export_data_header.append(geno_settings.MEMBER_FLAGS[i])
        export_data_header.append("Info")
        export_data_header.append("Zusatzinfo")
        for recipient in self.recipients:
            obj = lambda: None
            obj._fields = export_data_fields
            obj.organization = recipient.address.organization
            obj.name = recipient.address.name
            obj.first_name = recipient.address.first_name
            obj.title = recipient.address.title
            obj.email = recipient.address.email
            obj.tel1 = recipient.address.telephone
            obj.tel2 = recipient.address.mobile
            obj.city = recipient.address.city
            obj.street = recipient.address.street
            if recipient.member:
                obj.date_join = recipient.member.date_join
                obj.date_leave = recipient.member.date_leave
                obj.flag_01 = recipient.member.flag_01
                obj.flag_02 = recipient.member.flag_02
                obj.flag_03 = recipient.member.flag_03
                obj.flag_04 = recipient.member.flag_04
                obj.flag_05 = recipient.member.flag_05
            obj.info = ", ".join(recipient.log)
            obj.extra_info = recipient.extra_info
            export_data.append(obj)
        return export_data_to_xls(
            export_data,
            title="Mitglieder_Export",
            header=export_data_header,
            filename_suffix="mitglieder",
        )

    def rollback_failed_recipients(self):
        for recipient in self.recipients:
            if recipient.failure:
                for doc in recipient.documents:
                    if doc.linked_invoice:
                        logger.warning(
                            f"Rollback failed recipient {recipient}: Deleting invoice {doc.invoice}"
                        )
                        doc.linked_invoice.delete()

    def get_status_report(self):
        ret = {"errors": [], "warnings": [], "success": []}
        for recipient in self.recipients:
            recipient.add_address_warnings()
            if recipient.failure:
                ret["errors"].append(
                    {
                        "info": f"{recipient.address} - {recipient.extra_info} ({recipient.address.email})",
                        "objects": recipient.log,
                    }
                )
            elif recipient.warning:
                ret["warnings"].append(
                    {
                        "info": f"{recipient.address} - {recipient.extra_info} ({recipient.address.email})",
                        "objects": recipient.log,
                    }
                )
            else:
                ret["success"].append(
                    {
                        "info": f"{recipient.address} - {recipient.extra_info} ({recipient.address.email})",
                        "objects": recipient.log,
                    }
                )
        return ret

    def cleanup(self):
        for template in self.templates:
            template.cleanup()


## TODO: Add possibility to send a Document
def send_member_mail_process(data):
    is_test = data["action"] == "mail_test"
    process = ProcessDocuments(dry_run=is_test)
    if data["action"] in ("mail", "mail_test"):
        mail_template = MailTemplate(data["template_mail"], data["subject"], data["email_sender"])
        process.setup_mail(mail_template, bcc=data["email_copy"])
    if data["action"] in ("makezip", "makezip_pdf"):
        process.setup_zip()
    if data["action"] == "makezip":
        process.set_output_format("odt")
    elif data["template_files"]:
        process.set_output_format("pdf")

    try:
        for template in data["template_files"]:
            process.add_document_template(template)
    except Exception as e:
        return {"errors": [{"info": f"Fehler: Konte Dokumentvorlage nicht hinzufügen: {e}"}]}

    for m in data["members"]:
        if "contract_id" in m:
            contract = Contract.objects.get(id=m["contract_id"])
        else:
            contract = None
        if m["member_type"] == "member":
            recip = Member.objects.get(pk=m["id"])
        else:
            recip = Address.objects.get(pk=m["id"])
        process.add_recipient(recip, contract, m["extra_info"])

    try:
        process.generate_documents()
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Dokumente: {e}")
        return {"errors": [{"info": f"Fehler beim Erstellen der Dokumente: {e}"}]}
    process.send_output()
    process.rollback_failed_recipients()

    if not is_test:
        if data["change_attribute"]:
            process.update_member_attributes(
                data["change_attribute"], data["change_attribute_value"]
            )

        if data["change_genattribute"]:
            process.update_generic_attributes(
                data["change_genattribute"], data["change_genattribute_value"]
            )

    if data["action"] in ("makezip", "makezip_pdf"):
        result = process.get_zipfile()
    elif data["action"] == "list_xls":
        result = process.get_xls_list()
    else:
        result = process.get_status_report()
    process.cleanup()
    return result


def create_documents(default_doctype, objects=None, options=None):
    ret = []
    zipcount = 0
    zipfile_content = []
    makezip = options.get("makezip", False)

    try:
        default_doctype_obj = DocumentType.objects.get(name=default_doctype)
    except DocumentType.DoesNotExist:
        return [
            {
                "info": 'FEHLER: Dokumenttyp "%s" existiert nicht. Bitte zuerst erstellen.'
                % default_doctype
            }
        ]

    if not options:
        options = {"beschreibung": default_doctype_obj.description}

    if not objects:
        return []

    filenames = []
    for o in objects:
        zipcount += 1
        objects = []
        if "info" in o:
            objects.append(o["info"])
        ret.append({"info": str(o["obj"]), "objects": objects})
        if makezip:
            if "doctype" in o:
                doctype = o["doctype"]
                doctype_obj = DocumentType.objects.get(name=doctype)
            else:
                doctype = default_doctype
                doctype_obj = default_doctype_obj
            ## Create document
            # Check if template has a file attached
            if not doctype_obj.template or not doctype_obj.template.file:
                ret.append(
                    {
                        "info": "FEHLER: Keine Vorlage-Datei für Dokumenttyp '%s' konfiguriert."
                        % doctype,
                        "objects": [],
                    }
                )
                continue

            if "extra_context" in o:
                data = get_context_data(doctype, o["obj"].pk, o["extra_context"])
            else:
                data = get_context_data(doctype, o["obj"].pk, {})
            filename = fill_template_pod(
                doctype_obj.template.file.path,
                context_format(data["context"]),
                output_format="odt",
            )
            if not filename:
                raise RuntimeError("Could not fill template")
            output_filename = data["visible_filename"]
            counter = 1
            while output_filename in filenames:
                counter += 1
                output_filename = "%s_%s%s" % (
                    data["visible_filename"][0:-4],
                    counter,
                    data["visible_filename"][-4:],
                )
            zipfile_content.append({"file": filename, "filename": output_filename})
            filenames.append(output_filename)
            if "content_object" in data:
                ## Attach document data to object
                d = Document(
                    name=output_filename,
                    doctype=doctype_obj,
                    data=json.dumps(data["context"]),
                    content_object=data["content_object"],
                )
                d.save()

    if makezip:
        ## Build ZIP-file from list of files
        file_like_object = io.BytesIO()
        zipfile_ob = zipfile.ZipFile(file_like_object, "w")
        for f in zipfile_content:
            # print "%s -> %s_%s" % (f['file'], f['member'].name.name,f['member'].name.first_name)
            zipfile_ob.write(f["file"], f["filename"])
        zipfile_ob.close()
        resp = HttpResponse(
            file_like_object.getvalue(), content_type="application/x-zip-compressed"
        )
        resp["Content-Disposition"] = "attachment; filename=%s" % "output.zip"
        return resp

    if zipcount > 0:
        link_text = "%s erstellen und herunterladen" % options["beschreibung"]
        link_url = options.get("link_url", "")
        ret.append(
            {
                "info": "Dokumente:",
                "objects": [
                    '<a href="%s?makezip=yes">%s (%d LibreOffice Dokumente in ZIP)</a>'
                    % (link_url, link_text, zipcount)
                ],
            }
        )
    else:
        ret.append({"info": "Keine zu erstellenden Dokumente gefunden."})

    return ret


def get_context_data(doctype, obj_id, extra_context):
    c = extra_context
    filename_prefix = {
        "memberletter": "Brief_Bestätigung_Mitgliedschaft",
        "memberfinanz": "Brief_Finanzielle_Unterstützung",
        "memberfee": "Brief_Einforderung_Mitgliederbeitrag",
        "memberfeereminder": "Brief_Einforderung_Mitgliederbeitrag_Reminder",
        "shareconfirm": "Brief_Bestätigung_Anteilscheine",
        "shareconfirm_req": "Brief_Bestätigung_Einforderung",
        #'shareconfirm_reqpart': "Brief_Bestätigung_Einforderung_Rate",
        "loanreminder": "Brief_Erinnerung_Darlehen",
        "statement": "Kontoauszug",
        "mailing": "Brief_Mitglieder",
        "contract": "Vertrag",
        "contract_letter": "Vertrag_Begleitbrief",
        "contract_check": "Formular_Überprüfung_Belegung_Fahrzeuge",
    }

    filename_ext = ".odt"
    if doctype[0:6] == "member":
        obj = Member.objects.get(pk=obj_id)
        adr = obj.name
        c["datum_eintritt"] = obj.date_join.strftime("%d.%m.%Y")
    elif doctype[0:5] == "share":
        obj = Share.objects.get(pk=obj_id)
        adr = obj.name

        if Share.objects.filter(name=adr).filter(share_type=obj.share_type).count() == 1:
            c["is_first_share"] = True
        else:
            c["is_first_share"] = False

        try:
            stype_share = ShareType.objects.get(name="Anteilschein")
        except ShareType.DoesNotExist:
            stype_share = "Nonexistent"
        try:
            stype_loan_noint = ShareType.objects.get(name="Darlehen zinslos")
        except ShareType.DoesNotExist:
            stype_loan_noint = "Nonexistent"
        try:
            stype_loan_int = ShareType.objects.get(name="Darlehen verzinst")
        except ShareType.DoesNotExist:
            stype_loan_int = "Nonexistent"
        try:
            stype_loan_special = ShareType.objects.get(name="Darlehen spezial")
        except ShareType.DoesNotExist:
            stype_loan_special = "Nonexistent"
        try:
            stype_deposit = ShareType.objects.get(name="Depositenkasse")
        except ShareType.DoesNotExist:
            stype_deposit = "Nonexistent"

        if obj.date_due:
            duedate = obj.date_due
        elif obj.duration:
            duedate = obj.date + relativedelta(years=obj.duration)
        else:
            duedate = None
        if duedate:
            duedate_text = " (Fälligkeit: %s)" % duedate.strftime("%d.%m.%Y")
        else:
            duedate_text = ""

        c["betrag_text_zusatz"] = None
        if obj.share_type == stype_share:
            if hasattr(adr, "member"):
                c["datum_eintritt"] = adr.member.date_join.strftime("%d.%m.%Y")
            else:
                c["datum_eintritt"] = None
            if c["datum_eintritt"] and c["is_first_share"]:
                c["betreff"] = "Bestätigung Anteilscheine/Mitgliedschaft"
            else:
                c["betreff"] = "Bestätigung Anteilscheine"
            if obj.quantity == 1:
                c["betrag_text"] = "1 Anteilschein zu CHF %s" % (nformat(obj.value))
            else:
                c["betrag_text"] = "%s Anteilscheine zu CHF %s in Summe CHF %s" % (
                    nformat(obj.quantity, 0),
                    nformat(obj.value),
                    nformat(obj.quantity * obj.value),
                )
            if obj.is_pension_fund:
                c["betrag_text"] = "%s (aus Mitteln der beruflichen Vorsorge)" % (c["betrag_text"])
                c["bvg"] = True
            else:
                c["bvg"] = False
            count = 0
            amount = 0
            for s in get_active_shares().filter(name=obj.name).filter(share_type=stype_share):
                count += s.quantity
                amount += s.quantity * s.value
            if count == 1:
                c["total_anzahl"] = "1 Anteilschein"
            else:
                c["total_anzahl"] = "%s Anteilscheine" % (nformat(count, 0))
            c["total_summe"] = "%s" % (nformat(amount))
        elif obj.share_type == stype_loan_noint:
            c["betrag_text"] = "Zinsloses Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
        elif obj.share_type == stype_loan_int:
            c["betrag_text"] = "Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
            c["betrag_text_zusatz"] = "Aktueller Zinssatz: %s%%" % (nformat(obj.interest(), 2))
        elif obj.share_type == stype_deposit:
            c["betrag_text"] = "Einlage in die Depositenkasse von CHF %s" % (nformat(obj.value, 2))
            c["betrag_text_zusatz"] = "Aktueller Zinssatz: %s%%" % (nformat(obj.interest(), 2))
        elif obj.share_type == stype_loan_special:
            c["betrag_text"] = "Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
            c["betrag_text_zusatz"] = "Zinssatz: %s%% (gemäss Darlehensvertrag)" % (
                nformat(obj.interest(), 2)
            )
        else:
            c["betrag_text"] = "%s von CHF %s" % (
                obj.share_type.name,
                nformat(obj.value, 2),
            )

        c["datum_zahlung"] = obj.date.strftime("%d.%m.%Y")
    elif doctype == "statement" or doctype == "mailing" or doctype == "loanreminder":
        obj = Address.objects.get(pk=obj_id)
        adr = obj
    elif doctype[0:8] == "contract":
        obj = Contract.objects.get(pk=obj_id)
        adr = obj.get_contact_address()
        # adr = obj.person
        c["mietobjekt"] = ", ".join([str(ru) for ru in obj.rental_units.all()])
        c["mindestbelegung"] = " + ".join(
            [str(int(ru.min_occupancy)) for ru in obj.rental_units.filter(min_occupancy__gt=0)]
        )
        c["bewohnende"] = []
        duplicate_check = []
        for tenant in obj.contractors.exclude(ignore_in_lists=True):
            dup_id = f"{tenant.name}{tenant.first_name}"
            if dup_id not in duplicate_check:
                c["bewohnende"].append({"name": tenant.name, "vorname": tenant.first_name})
                duplicate_check.append(dup_id)
        for child in obj.children.exclude(name__ignore_in_lists=True):
            dup_id = f"{child.name.name}{child.name.first_name}"
            if dup_id not in duplicate_check:
                c["bewohnende"].append({"name": child.name.name, "vorname": child.name.first_name})
                duplicate_check.append(dup_id)
        # c['area'] = "%s" % (nformat(obj.area,0))
        # c['netto'] = "%s" % (nformat(obj.rent_total-obj.nk,2))
        # c['nk'] = "%s" % (nformat(obj.nk,2))
        # c['rent_total'] = "%s" % (nformat(obj.rent_total,2))
        # c['depot'] = "%s" % (nformat(obj.depot,2))
        # c['begin'] = obj.date.strftime("%d.%m.%Y")
    else:
        raise RuntimeError("Doctype not implemented.")

    adr_filename_str = ""
    if adr:
        c.update(adr.get_context())
        adr_filename_str = adr.get_filename_str()
    if "filename_tag" in c:
        filename_tag = "_%s" % c["filename_tag"]
    else:
        filename_tag = ""
    if c["roomnr"]:
        adr_filename_str = "%s_%s" % (c["roomnr"], adr_filename_str)
    filename = "%s_%s%s%s" % (
        filename_prefix[doctype],
        adr_filename_str,
        filename_tag,
        filename_ext,
    )

    return {
        "content_object": obj,
        "visible_filename": filename.replace(" ", "").replace("+", "-").replace("/", "-"),
        "context": c,
    }


def context_format(context, output_format="odt"):
    # for k,v in context.items():
    #    if output_format == 'odt':
    #        if isinstance(context[k], basestring):
    #            context[k] = mark_safe(v.replace('\n', '<text:line-break />'))
    return context
