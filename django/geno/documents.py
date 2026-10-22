import datetime
import json
import logging
import os
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, Q
from django.template import Context, Template
from django.utils.translation import gettext as _

from geno.billing import add_invoice, get_reference_nr, render_qrbill
from geno.mail import Recipient
from geno.models import (
    Address,
    Contract,
    Document,
    DocumentType,
    InvoiceCategory,
    Member,
    Share,
    ShareType,
)
from geno.shares import get_share_statement_data
from geno.utils import (
    fill_pod_template,
    nformat,
    odt2pdf,
    remove_temp_files,
    sanitize_filename,
)

logger = logging.getLogger("geno")

class _ContextEncoder(DjangoJSONEncoder):
    """
    Custom JSON encoder that serializes Django Model instances to their string representation.
    Used to dump JSON data during Document creation
    """

    def default(self, obj):
        if isinstance(obj, Model):
            return str(obj)
        return super().default(obj)


class RenderedDocument:
    def __init__(self):
        self.file = None
        self.filename = None
        self.linked_invoice = None
        self.context = None
        self.doctype = None
        self.content_template = None


class DocumentTemplate:
    # TODO: create a DocumentOutputType class that uses Literal
    SUPPORTED_OUTPUT_TYPES = ("odt", "pdf")

    def __init__(self,
                 template: Template,
                 doctype: DocumentType=None,
                 output_format: str=None,
                 dry_run: bool=False):
        self.content_template = template
        self.doctype = doctype
        self.output_format = output_format
        self.context_options = {
            "share_statement_context": False,
            "billing_context": False,
            "qrbill_account": None,
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
        from geno.mail import SkipRecipientException
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
        raise SkipRecipientException("Keine Beteiligungen für Kontoauszug.")

    def get_billing_context(self, recipient):
        c = {}

        ## Geforderte Beteiligungen
        shares = (
            Share.objects.filter(
                Q(payment_date__gt=datetime.date.today()) | Q(payment_date__isnull=True)
            )
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

    def render(self, recipient) -> RenderedDocument:
        rendered_document = RenderedDocument()
        rendered_document.file = self.content_template.file.path
        filename_tag = sanitize_filename(self.content_template.name)
        if self.content_template.template_type == "OpenDocument":
            context = self.get_context(recipient)
            self.log_template_rendering(context)
            temporary_filename = fill_pod_template(
                self.content_template.file.path,
                context,
                output_format="odt"
            )
            rendered_document.file = temporary_filename
            self.temp_files.append(rendered_document.file)
            if not filename_tag:
                # TODO: smells funny
                filename_tag = os.path.splitext(os.path.basename(self.content_template.file.path))[
                    0
                ]
                logger.warning(
                    "No filename_tag using default: %s" % self.content_template.file.path
                )
            rendered_document.filename = (
                f"{recipient.address.get_filename_str()}_{filename_tag}.{self.output_format}"
            )
            if self.output_format not in self.SUPPORTED_OUTPUT_TYPES:
                raise ValueError(f"Unsupported output format: {self.output_format}")
            if self.output_format == "pdf":
                self.render_document_as_pdf(rendered_document, context)
            if not rendered_document.file:
                raise RuntimeError("Could not fill template")
            rendered_document.context = context
            rendered_document.doctype = self.doctype
            # Fallback if the doctype has not been set explicitly
            if not rendered_document.doctype and self.content_template:
                rendered_document.doctype = self.content_template.document_types.filter(active=True).first()
            rendered_document.content_template = self.content_template
        else:
            # ContentTemplate is not an OpenDocument
            logger.info(" > appending file without rendering: %s" % (rendered_document.file))
            # append file ending of output.file to filename_tag
            if not filename_tag.endswith(os.path.splitext(rendered_document.file)[1]):
                filename_tag += os.path.splitext(rendered_document.file)[1]
            rendered_document.filename = filename_tag
        return rendered_document

    def render_document_as_pdf(self, rendered_document, context):
        logger.info(" > odt2pdf(%s) -> %s" % (rendered_document.file, rendered_document.filename))
        rendered_document.file = odt2pdf(rendered_document.file, "send_member_mail")
        self.temp_files.append(rendered_document.file)
        if context["qr_account"]:
            output_dir = f"/tmp/documents_render_qrbill_{settings.GENO_ID}"
            logger.info(f" > render_qrbill({output_dir}/{rendered_document.filename}")
            render_qrbill(
                        None,
                        context,
                        rendered_document.filename,
                        base_pdf_file=rendered_document.file,
                        append_pdf_file=None,
                        output_dir=output_dir,
                    )
            rendered_document.linked_invoice = context["invoice"]
            rendered_document.file = f"{output_dir}/{rendered_document.filename}"
            self.temp_files.append(rendered_document.file)

    def log_template_rendering(self, ctx) -> None:
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

    def cleanup(self):
        remove_temp_files(self.temp_files)


## TODO: Make subclasses of Document
# class QRBillDocument(Document):
#    def render(self, recipient):




@dataclass
class DocumentFetchResult:
    """A Result indicating the status of a Document fetching action."""
    status: Literal["success", "error"]
    label: str
    detail: list[str] = field(default_factory=list)


@dataclass
class DocumentCreationResult:
    """A Result indicating the status of a Document creation action."""
    status: Literal["success", "info", "error", "warning"]
    label: str
    detail: list[str] = field(default_factory=list)
    temporary_file_location: str | None = None
    filename: str | None = None


class DocumentTypeError(Exception):
    # TODO: implement
    pass


class DocumentGenerator:
    """
    Builder class to create Documents. As a rule, Documents should be persisted
    at creation time, so that they remain accessible with re-generation.
    """
    default_document_type: DocumentType = None

    def __init__(self, default_document_type: DocumentType=None, dry_run: bool=False):
        self.default_document_type = default_document_type
        self.dry_run = dry_run
        self.temp_files = []

    def render_documents_for_recipient(
        self, recipient: Recipient, templates: list[DocumentTemplate]
    ) -> None:
        """Render DocumentTemplates for a Recipient and attach results."""
        from geno.mail import SkipRecipientException

        if recipient.skip_reason:
            return
        for template in templates:
            try:
                doc = template.render(recipient)
                recipient.documents.append(doc)
            except SkipRecipientException as e:
                logger.info(
                    "Skipping recipient: No document (template=%s, reason=%s)", template, e
                )
                recipient.skip_reason = str(e)
                break

    def create_document(
            self,
            document_type: DocumentType,
            template: DocumentTemplate,
            context: dict,
            filename: str=None,
        ) -> DocumentCreationResult:
        """
        Create a single Document object from a known DocumentType and
        DocumentTemplate. The Template is filled upon creation, and the
        resulting file is persisted, s.t. it can be retrieved later.

        Returns a DocumentCreationResult with an exit status and paths to the
        created Document and its File.
        """
        # TODO: perform error-checking here
        if filename:
            output_filename = filename
        else:
            output_filename = context["visible_filename"]
        data = json.dumps(context, cls=_ContextEncoder)
        # TODO: deduplicate filename
        document = Document(
            name=output_filename,
            doctype=document_type,
            template=template,
            data=data,
            content_object=context.get("content_object"),
        )
        # TODO: error handling to catch error results
        temporary_file_location = self._fill_template(template, {"context": context})
        self.temp_files.append(temporary_file_location)
        self._persist_document(document)
        self._save_document_file(document, temporary_file_location)
        # TODO: are we passing back everything that we require?
        result = DocumentCreationResult(
            status="success",
            label=str(document),
            detail=[str(document)],
            temporary_file_location=temporary_file_location,
            filename=output_filename
        )
        return result

    def create_documents_for_recipient(self, recipient: Recipient) -> list[DocumentCreationResult]:
        """
        Create Documents for an e-mail recipient. A single Recipient
        can receive multiple Documents in a single e-mail.

        recipient: planned e-mail recipient.

        Returns a list of DocumentCreationResults
        """
        results: list[DocumentCreationResult] = []

        for rendered_document in recipient.documents:
            if rendered_document.doctype is None or rendered_document.context is None:
                continue
            try:
                context = dict(rendered_document.context)
                if "content_object" not in context:
                    context["content_object"] = recipient.address
                result = self.create_document(
                    document_type=rendered_document.doctype,
                    template=rendered_document.content_template,
                    context=context,
                    filename=rendered_document.filename,
                )
                results.append(result)
            except Exception as e:
                msg = f"Konnte Dokument '{rendered_document.filename}' für {recipient} nicht speichern. Fehler: {e}"
                logger.error(msg)
                recipient.failure = True
                recipient.log.append(msg)
        return results


    def create_documents(self,
                         document_objects: list[dict],
                         options: list[dict] | None) -> list[DocumentCreationResult]:
        """
        Given a list of Document objects, creates individual Documents, and
        persists the result to the database and filesystem.

        document_objects: list of dictionaries, containing a Model object, a
            DocumentType, and additional "info".

        Returns a list of DocumentCreationResults, which can be consumed to
        create Views.
        """
        results: list[DocumentCreationResult] = []
        files_to_zip = []
        make_zip = options.get("makezip", False)
        filenames: list[str] = []
        # Early exit: the default DocumentType is not available
        try:
            default_document_type = DocumentType.objects.get(name=self.default_document_type)
        except DocumentType.DoesNotExist:
            return [ DocumentCreationResult(
                status="error",
                label=(_(f"The document type '{self.default_document_type}' does not exist."))
            )]

        for object in document_objects:
            # Resolve DocumentType for this object
            document_type_name = object["doctype"]
            if "doctype" in object:
                try:
                    document_type = DocumentType.objects.get(name=document_type_name)
                except DocumentType.DoesNotExist:
                    results.append(
                        DocumentCreationResult(
                            status="error",
                            label=(_(f"Document type '{document_type}' not found."))
                        )
                    )
                    break
            else:
                # No DocumentType found, use the default
                document_type = default_document_type
            detail = []

            # Get info from the Object
            if "info" in object:
                detail.append(object["info"])

            # Validate the template
            content_template = self._get_template(document_type=document_type)
            # TODO: handle "extra_context" in Object
            context = get_context_data(document_type_name, object["obj"].pk)
            # Create the Document
            result = self.create_document(
                document_type=document_type,
                template=content_template,
                context=context
            )
            results.append(result)
            if not make_zip:
                # Exit early: we do not need to create a .zip for one Document
                return results
            else:
                # Track the files that will be placed into a .zip
                filenames.append(result.filename)
                files_to_zip.append({"obj": object, "doctype": document_type_name, "doctype_obj": document_type})
        # TODO: pass this off to a helper function
        if files_to_zip:
            link_text = "%s erstellen und herunterladen" % options["beschreibung"]
            link_url = options.get("link_url", "")
            results.append(
                DocumentCreationResult(
                    status="info",
                    label="Dokumente:",
                    detail=[
                        '<a href="%s?makezip=yes">%s (%d LibreOffice Dokumente in ZIP)</a>'
                        % (link_url, link_text, len(files_to_zip))
                    ],
                )
            )
        else:
            results.append(
                DocumentCreationResult(
                    status="warning", label="No Documents to be created."
                )
            )
        return results


    def _deduplicate_filename(filename: str) -> str:
        # TODO: implement the counter
        file_count = 0
        filename_stem, file_extension = os.path.splitext(filename)
        output_filename = "%s_%s.%s" % (filename_stem, file_count, file_extension)
        return output_filename

    def _persist_document(self, document: Document) -> None:
        """
        Persist a Document object in the database.
        """
        document.save()

    def _save_document_file(self, document, temporary_filename):
        """
        Copy a file from temporary storage into the Document object's File field

        document: the Document object that will store the file.
        temporary_filename: path to the temporary File data.
        """
        with open(temporary_filename, "rb") as f:
            document.file.save(document.name, File(f), save=True)

    def cleanup(self):
        remove_temp_files(self.temp_files)
        self.temp_files = []

    def _get_template(self, document_type, document=None, template_pk=None):
        """Resolve template: explicit pk first, then doc.template, then first active."""
        # TODO: check these execution paths
        if template_pk:
            return document_type.templates.get(pk=template_pk)
        if document:
            return document.template
        else:
            return document_type.templates.filter(active=True).first()

    def _assert_template_file(self, template):
        if not template.file:
            raise RuntimeError(
                _("The template '{template}' has no file linked to it.").format(template=template)
            )

    def _fill_template(self, template, data):
        """Render the template and return the temporary file path."""
        self._assert_template_file(template)
        temporary_filename = fill_pod_template(
            template.file.path, context_format(data["context"]), output_format="odt"
        )
        if not temporary_filename:
            raise RuntimeError(_("Could not fill the template"))
        return temporary_filename




def get_context_data(doctype, obj_id, extra_context: dict=None) -> dict:
    if extra_context is None:
        extra_context = dict()
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
    if "member" in doctype:
        obj = Member.objects.get(pk=obj_id)
        adr = obj.name
        extra_context["datum_eintritt"] = obj.date_join.strftime("%d.%m.%Y")
    elif "share" in doctype:
        obj = Share.objects.get(pk=obj_id)
        adr = obj.name
        # TODO: consider refactoring this
        if Share.objects.filter(name=adr).filter(share_type=obj.share_type).count() == 1:
            extra_context["is_first_share"] = True
        else:
            extra_context["is_first_share"] = False
        # TODO: consider refactoring this
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

        extra_context["betrag_text_zusatz"] = None
        if obj.share_type == stype_share:
            if hasattr(adr, "member"):
                extra_context["datum_eintritt"] = adr.member.date_join.strftime("%d.%m.%Y")
            else:
                extra_context["datum_eintritt"] = None
            if extra_context["datum_eintritt"] and extra_context["is_first_share"]:
                extra_context["betreff"] = "Bestätigung Anteilscheine/Mitgliedschaft"
            else:
                extra_context["betreff"] = "Bestätigung Anteilscheine"
            if obj.quantity == 1:
                extra_context["betrag_text"] = "1 Anteilschein zu CHF %s" % (nformat(obj.value))
            else:
                extra_context["betrag_text"] = "%s Anteilscheine zu CHF %s in Summe CHF %s" % (
                    nformat(obj.quantity, 0),
                    nformat(obj.value),
                    nformat(obj.quantity * obj.value),
                )
            if obj.is_pension_fund:
                extra_context["betrag_text"] = "%s (aus Mitteln der beruflichen Vorsorge)" % (extra_context["betrag_text"])
                extra_context["bvg"] = True
            else:
                extra_context["bvg"] = False
            count = 0
            amount = 0
            for s in Share.get_active().filter(name=obj.name).filter(share_type=stype_share):
                count += s.quantity
                amount += s.quantity * s.value
            if count == 1:
                extra_context["total_anzahl"] = "1 Anteilschein"
            else:
                extra_context["total_anzahl"] = "%s Anteilscheine" % (nformat(count, 0))
            extra_context["total_summe"] = "%s" % (nformat(amount))
        elif obj.share_type == stype_loan_noint:
            extra_context["betrag_text"] = "Zinsloses Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
        elif obj.share_type == stype_loan_int:
            extra_context["betrag_text"] = "Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
            extra_context["betrag_text_zusatz"] = "Aktueller Zinssatz: %s%%" % (nformat(obj.interest(), 2))
        elif obj.share_type == stype_deposit:
            extra_context["betrag_text"] = "Einlage in die Depositenkasse von CHF %s" % (nformat(obj.value, 2))
            extra_context["betrag_text_zusatz"] = "Aktueller Zinssatz: %s%%" % (nformat(obj.interest(), 2))
        elif obj.share_type == stype_loan_special:
            extra_context["betrag_text"] = "Darlehen von CHF %s%s" % (
                nformat(obj.value, 2),
                duedate_text,
            )
            extra_context["betrag_text_zusatz"] = "Zinssatz: %s%% (gemäss Darlehensvertrag)" % (
                nformat(obj.interest(), 2)
            )
        else:
            extra_context["betrag_text"] = "%s von CHF %s" % (
                obj.share_type.name,
                nformat(obj.value, 2),
            )

        extra_context["datum_zahlung"] = obj.payment_date.strftime("%d.%m.%Y")
        extra_context.update(obj.get_context(include_related_shares=True))
    elif doctype == "statement" or doctype == "mailing" or doctype == "loanreminder":
        obj = Address.objects.get(pk=obj_id)
        adr = obj
    elif doctype[0:8] == "contract":
        obj = Contract.objects.get(pk=obj_id)
        adr = obj.get_contact_address()
        extra_context.update(obj.get_context())
    else:
        raise RuntimeError("Doctype not implemented.")

    adr_filename_str = ""
    if adr:
        extra_context.update(adr.get_context())
        adr_filename_str = adr.get_filename_str()
    if "filename_tag" in extra_context:
        filename_tag = "_%s" % extra_context["filename_tag"]
    else:
        filename_tag = ""
    if extra_context["roomnr"]:
        adr_filename_str = "%s_%s" % (extra_context["roomnr"], adr_filename_str)
    filename = "%s_%s%s%s" % (
        filename_prefix[doctype],
        adr_filename_str,
        filename_tag,
        filename_ext,
    )

    return {
        "content_object": obj,
        "visible_filename": filename.replace(" ", "").replace("+", "-").replace("/", "-"),
        "context": extra_context,
    }


def context_format(context, output_format="odt"):
    # for k,v in context.items():
    #    if output_format == 'odt':
    #        if isinstance(context[k], basestring):
    #            context[k] = mark_safe(v.replace('\n', '<text:line-break />'))
    return context
