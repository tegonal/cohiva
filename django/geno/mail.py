import datetime
import io
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Literal
from zipfile import ZipFile

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import Context, Template, loader
from django.utils.html import escape
from html2text import html2text

import geno.settings as geno_settings
from geno.exporter import export_data_to_xls
from geno.models import (
    Address,
    ContentTemplate,
    Contract,
    DocumentType,
    GenericAttribute,
    Member,
    MemberAttribute,
    MemberAttributeType,
)

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


class SkipRecipientException(Exception):
    pass

@dataclass
class MailSendResult:
    # TODO: implement a Result class
    status: Literal["success", "error", "warning"]
    label: str
    detail: list[str] = field(default_factory=list)

class DocumentMailer:
    def __init__(self, dry_run=False):
        from geno.documents import DocumentTemplate
        self.mail_template = None
        self.mail_bcc = None
        self.mail_test = True
        self.zipfile = None
        self.output_format = None
        self.templates: list[DocumentTemplate] = []
        self.recipients = []
        self.contexts = {}
        self.test_email_address = None
        self.dry_run = dry_run

    def setup_mail(self, template, bcc=None):
        self.mail_template = template
        self.mail_bcc = bcc

    def setup_zip(self):
        self.zip_bytes = io.BytesIO()
        self.zipfile = ZipFile(self.zip_bytes, "w")

    def set_output_format(self, filetype):
        self.output_format = filetype

    def add_document_template(self, att):
        from geno.documents import DocumentTemplate
        # TODO: what does att contain?
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
                # TODO: create a helper that gets and validates the content template
                content_template = doctype.templates.filter(active=True).first()
                if not content_template:
                    raise ValueError(f"Dokumenttyp {doctype} hat keine aktive Vorlage")
                if not content_template.file:
                    raise ValueError(f"Dokumenttyp {doctype}: Vorlage hat keine Datei hinterlegt")
            except DocumentType.DoesNotExist:
                raise ValueError(f"Dokumenttyp mit ID {att_id} nicht gefunden.")
        elif att_type == "ContentTemplate":
            try:
                content_template = ContentTemplate.objects.get(id=att_id)
                if not content_template.file:
                    raise ValueError(f"Vorlage '{content_template.name}' hat keine Datei hinterlegt")
            except ContentTemplate.DoesNotExist:
                raise ValueError(f"Vorlage mit ID {att_id} nicht gefunden.")
        else:
            raise TypeError(f"Unbekannter Vorlagentyp: {att}")
        self.templates.append(
            DocumentTemplate(
                template=content_template,
                doctype=doctype,
                output_format=self.output_format,
                dry_run=self.dry_run,
            )
        )

    def add_recipient(self,
                      addressee: Member | Address,
                      contract: Contract=None,
                      extra_info: str=None) -> None:
        """
        Creates a new Recipient and appends it to the DocumentMailer's list of
        Recipients.
        """
        if isinstance(addressee, Member):
            recipient = Recipient(
                address=addressee.name,
                member=addressee,
                contract=contract,
                extra_info=extra_info,
            )
        elif isinstance(addressee, Address):
            recipient = Recipient(
                address=addressee,
                contract=contract,
                extra_info=extra_info,
            )
        else:
            raise TypeError(f"{addressee} must be a Member or an Address.")
        self.validate_recipient(recipient)
        self.recipients.append(recipient)

    def validate_recipient(self, recipient: Recipient) -> None:
        if self.mail_template and not recipient.address.email:
            recipient.skip_reason = "Keine Email-Adresse vorhanden."
        if self.mail_template and recipient.address.paymentslip:
            ## TODO: rename address.paymentslip to more generic special_case or similar
            recipient.skip_reason = "Spezialfall (manuelle Bearbeitung)"

    def send_output(self):
        if self.mail_template:
            self.send_output_mails()
        if self.zipfile:
            self.add_documents_to_zip()

    def add_documents_to_zip(self):
        for recipient in self.recipients:
            for doc in recipient.documents:
                self.zipfile.write(doc.file, doc.filename)

    def send_output_mails(self):
        logger.info("Start sending e-mails.")
        for recipient in self.recipients:
            if recipient.skip_reason:
                recipient.warning = True
                recipient.log.append(f"KEIN EMAIL GESENDET! Grund: {recipient.skip_reason}")
            else:
                context = self.get_email_context(recipient)
                try:
                    mail_recipient = self.send_email(
                        address=recipient.address,
                        mail_template=self.mail_template,
                        context=context,
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
        logger.info("Finish sending e-mails.")

    def throttle(self):
        if not getattr(settings, "IS_RUNNING_TESTS", False):
            time.sleep(0.2)

    def get_email_context(self, recipient):
        context = recipient.address.get_context()
        ## TODO: Make this more generic for any member attribute or generic attribute
        if self.mail_template == "geno/member_email_ausschreibung.html":
            atype = MemberAttributeType.objects.get(name="Ausschreibung Code")
            code = MemberAttribute.objects.get(member=recipient.member, attribute_type=atype)
            context["email_code"] = code.value
        return context

    ## TODO: Move/merge this with generic send-mail function?
    # TODO: complete method signature type-hints
    def send_email(
        self,
        address: Address,
        mail_template: MailTemplate,
        context,
        bcc: list=None,
        test_to_bcc=True,
        attachments=None
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
        for attachment in attachments:
            attfile = open(attachment.file, "rb")
            mail.attach(attachment.filename, attfile.read())
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
                    member_attribute = MemberAttribute.objects.get(
                        member=recipient.member, attribute_type=attribute
                    )
                    old_value = member_attribute.value
                except MemberAttribute.DoesNotExist:
                    member_attribute = MemberAttribute(member=recipient.member, attribute_type=attribute)
                    old_value = "(Kein)"
                member_attribute.value = value
                member_attribute.date = datetime.date.today()
                member_attribute.save()
                recipient.log.append(
                    f'Mitglieder-Attribut "{attribute}" geändert: "{old_value}" -> "{member_attribute.value}"'
                )

    def update_generic_attributes(self, attribute, value):
        for recipient in self.recipients:
            if not recipient.failure and recipient.address:
                try:
                    generic_attribute = (GenericAttribute
                                    .objects
                                    .filter(addresses=recipient.address)
                                    .get(name=attribute)
                    )
                    old_value = generic_attribute.value
                except GenericAttribute.DoesNotExist:
                    generic_attribute = GenericAttribute(content_object=recipient.address, name=attribute)
                    old_value = "(Kein)"
                generic_attribute.value = value
                generic_attribute.date = datetime.date.today()
                generic_attribute.save()
                recipient.log.append(
                    f'Allg.Attribut "{attribute}" geändert: "{old_value}" -> "{generic_attribute.value}"'
                )

    def get_zipfile(self):
        self.zipfile.close()
        resp = HttpResponse(
            self.zip_bytes.getvalue(), content_type="application/x-zip-compressed"
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
        # TODO: why this range, specifically?
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
                            f"Rollback failed recipient {recipient}: Deleting invoice {doc.linked_invoice}"
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

    def send_member_mail_process(self, data):
        """
        Process and create Documents for sending to Members.
        """
        from geno.documents import DocumentGenerator
        is_test = data["action"] == "mail_test"
        if data["action"] in ("mail", "mail_test"):
            mail_template = MailTemplate(data["template_mail"], data["subject"], data["email_sender"])
            self.setup_mail(mail_template, bcc=data["email_copy"])
        if data["action"] in ("makezip", "makezip_pdf"):
            self.setup_zip()
        if data["action"] == "makezip":
            self.set_output_format("odt")
        elif data["template_files"]:
            self.set_output_format("pdf")

        try:
            for template in data["template_files"]:
                self.add_document_template(template)
        except Exception as e:
            return {"errors": [{"info": f"Fehler: Konte Dokumentvorlage nicht hinzufügen: {e}"}]}

        for member in data["members"]:
            if "contract_id" in member:
                contract = Contract.objects.get(id=member["contract_id"])
            else:
                contract = None
            if member["member_type"] == "member":
                recipient = Member.objects.get(pk=member["id"])
            else:
                recipient = Address.objects.get(pk=member["id"])
            self.add_recipient(recipient, contract, member["extra_info"])

        document_generator = DocumentGenerator(dry_run=is_test)
        try:
            for recipient in self.recipients:
                document_generator.render_documents_for_recipient(recipient, self.templates)
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Dokumente: {e}")
            self.cleanup()
            document_generator.cleanup()
            return {"errors": [{"info": f"Fehler beim Erstellen der Dokumente: {e}"}]}

        self.send_output()
        self.rollback_failed_recipients()

        if not is_test:
            if data["change_attribute"]:
                self.update_member_attributes(
                    data["change_attribute"], data["change_attribute_value"]
                )

            if data["change_genattribute"]:
                self.update_generic_attributes(
                    data["change_genattribute"], data["change_genattribute_value"]
                )

            if data["action"] in ("mail", "makezip", "makezip_pdf"):
                for recipient in self.recipients:
                    if not recipient.failure and not recipient.skip_reason:
                        document_generator.create_documents_for_recipient(recipient)

        if data["action"] in ("makezip", "makezip_pdf"):
            result = self.get_zipfile()
        elif data["action"] == "list_xls":
            result = self.get_xls_list()
        else:
            result = self.get_status_report()
        self.cleanup()
        document_generator.cleanup()
        return result


    def cleanup(self):
        for template in self.templates:
            template.cleanup()
