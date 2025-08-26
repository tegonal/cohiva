import datetime

from dateutil.relativedelta import relativedelta
from stdnum.ch import esr

from .gnucash import add_invoice, create_qrbill, get_reference_nr
from .models import Invoice, InvoiceCategory
from .utils import nformat


class InvoiceCreatorError(Exception):
    pass


class InvoiceNotUnique(Exception):
    pass


class InvoiceCreator:
    ## Used in (note for testing):
    ##  - Holliger Schlüssel Webform - website.views.holliger()
    ##  - TODO: Manual invoice through admin tool - geno.views.invoice_manual()
    ##  - TODO: Automatic invoices (Miete / Nebenkosten)
    def __init__(self, category_name, dry_run=True):
        ## Control
        self.category = InvoiceCategory.objects.get(name=category_name)
        self.dry_run = dry_run

        ## Invoice content
        self.date = datetime.date.today()
        self.lines = []
        self.extra_text = ""
        self.address = None
        self.ref_number = None

        ## Internal variables
        self.invoice_object = None
        self.total_amount = 0

        ## Email
        self.email_template = "email_invoice.html"

    def create_invoice_object(self, comment=""):
        if self.invoice_object:
            raise InvoiceCreatorError("Invoice object exists already")
        if not self.category:
            raise AttributeError("category is not set")
        if not self.address:
            raise AttributeError("address is not set")
        if self.dry_run:
            return
        ret = add_invoice(
            None,
            self.category,
            self.category.name,
            self.date,
            self.total_amount,
            address=self.address,
            comment=comment,
        )
        if isinstance(ret, str):
            raise InvoiceCreatorError("Could not add invoice object: %s" % ret)
        self.invoice_object = ret

    def get_invoice_id(self):
        if self.dry_run:
            return 9999999999
        else:
            return self.invoice_object.id

    def add_line(self, text, amount, date=None):
        if not date:
            date = self.date
        self.lines.append(
            {"date": date.strftime("%d.%m.%Y"), "text": text, "total": nformat(amount)}
        )
        self.total_amount += amount

    def create_invoice_pdf(self, send_email=False):
        if not self.category:
            raise AttributeError("category is not set")
        if not self.address:
            raise AttributeError("address is not set")
        self.ref_number = get_reference_nr(self.category, self.address.id, self.get_invoice_id())
        output_filename = "Rechnung_%s_%s_%s.pdf" % (
            self.category.name,
            self.date.strftime("%Y%m%d"),
            esr.compact(self.ref_number),
        )
        context = self.address.get_context()
        if self.category.name == "Geschäftsstelle":
            context["betreff"] = "Rechnung"
        else:
            context["betreff"] = "Rechnung %s" % self.category.name
        context["extra_text"] = self.extra_text
        context["invoice_date"] = self.date.strftime("%d.%m.%Y")
        context["invoice_duedate"] = (self.date + relativedelta(months=1)).strftime("%d.%m.%Y")
        context["invoice_nr"] = self.get_invoice_id()
        context["show_liegenschaft"] = False
        context["contract_info"] = None
        context["sect_rent"] = False
        context["sect_generic"] = True
        context["generic_info"] = self.lines
        context["s_generic_total"] = nformat(self.total_amount)
        context["qr_amount"] = self.total_amount
        context["qr_extra_info"] = "Rechnung %s" % context["invoice_nr"]
        context["preview"] = self.dry_run

        email_subject = "%s Nr. %s/%s" % (
            context["betreff"],
            context["invoice_nr"],
            context["invoice_date"],
        )

        render = True
        if send_email:
            email_templ = self.email_template
        else:
            email_templ = None

        (ret, mails_sent, mail_recipient) = create_qrbill(
            self.ref_number,
            self.address,
            context,
            output_filename,
            render,
            email_templ,
            email_subject,
            self.dry_run,
        )

        if email_templ:
            if mails_sent != 1:
                raise InvoiceCreatorError(
                    "Could not send invoice-email to %s / ref_number = %s"
                    % (mail_recipient, self.ref_number)
                )

    def create_and_send(self, adr, comment="", check_unique=False):
        self.address = adr
        if check_unique:
            existing_invoice = Invoice.objects.filter(
                person=self.address,
                invoice_type="Invoice",
                invoice_category=self.category,
                amount=self.total_amount,
                active=True,
            ).first()
            if existing_invoice:
                raise InvoiceNotUnique("%s" % existing_invoice)
        self.create_invoice_object(comment)
        try:
            self.create_invoice_pdf(send_email=True)
        except Exception as e:
            ## Rollback invoice creation
            self.invoice_object.delete()
            raise e
