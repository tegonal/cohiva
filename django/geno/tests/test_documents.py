import datetime
from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.http import HttpResponse

# from geno.views import send_member_mail_process
from geno.documents import send_member_mail_process
from geno.forms import MemberMailActionForm
from geno.models import (
    Address,
    ContentTemplate,
    GenericAttribute,
    Invoice,
    InvoiceCategory,
    MemberAttribute,
    MemberAttributeType,
    Share,
)
from geno.tests import data as geno_testdata

from .base import DocumentCreationMockMixin, GenoAdminTestCase


class DocumentSendTest(DocumentCreationMockMixin, GenoAdminTestCase):
    # Specify correct import paths for patching
    patch_target_fill_template = "geno.documents.fill_template_pod"
    patch_target_odt2pdf = "geno.documents.odt2pdf"

    def test_select_without_session(self):
        response = self.client.get("/geno/member/send_mail/select/")
        self.assertRedirects(response, "/geno/member/send_mail/")

    def form_filter_active_members(self):
        response = self.client.get("/geno/member/send_mail/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Allg. Attribut-Wert:", response.content.decode())

        post_data = {
            "base_dataset": "active_members",
            "select_attributeA_value": "--OHNE--",
            "select_attributeB_value": "--OHNE--",
            "select_flag_01": "none",
            "select_flag_02": "none",
            "select_flag_03": "none",
            "select_flag_04": "none",
            "select_flag_05": "none",
            "filter_invoice": "none",
            "filter_invoice_consolidated": "none",
        }
        response = self.client.post("/geno/member/send_mail/", post_data)
        self.assertRedirects(
            response, "/geno/member/send_mail/select/", fetch_redirect_response=False
        )

    def form_select_members(self):
        response = self.client.get("/geno/member/send_mail/select/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Muster, Hans", response.content.decode())

        post_data = {
            "select_members": [
                self.members[0].pk,
                self.members[1].pk,
                self.members[2].pk,
                self.members[3].pk,
                self.members[4].pk,
            ],
        }
        response = self.client.post("/geno/member/send_mail/select/", post_data)
        self.assertRedirects(
            response, "/geno/member/send_mail/action/", fetch_redirect_response=False
        )

    def form_action_list(self):
        response = self.client.get("/geno/member/send_mail/action/")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Member Bill [OpenDocument Vorlage]", response.content.decode())

        post_data = {
            "action": "list",
        }
        response = self.client.post("/geno/member/send_mail/action/", post_data)
        self.assertEqual(response.status_code, 200)

    def form_action_send(self, formal):
        self.reset_mocks()
        prev_geno_formal = settings.GENO_FORMAL
        settings.GENO_FORMAL = formal
        mail.outbox = []

        post_data = {
            "action": "mail_test",
            "template_files": [f"ContentTemplate:{ContentTemplate.objects.get(name='Simple').pk}"],
            "template_mail": f"template_id_{self.email_templates[0].pk}",
            "subject": "Email-Test-Subject",
            "email_sender": MemberMailActionForm.email_sender_choices[1],
            "email_copy": "bcc-copy@example.com",
            # change_attribute	""
            # change_attribute_value	""
            # change_genattribute	""
            # change_genattribute_value	""
        }
        response = self.client.post("/geno/member/send_mail/action/", post_data)
        self.assertEqual(response.status_code, 200)

        ## Check mails
        self.assertEmailSent(4, "Email-Test-Subject", "Liebe Anna\n\nDies ist ein Test für dich.")
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Anna_Simple.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")

        ## Check document creation (mocked)
        self.assertMocksCallCount(4)

        current_year = datetime.datetime.now().year
        self.assertFillTemplateCalledWith(
            call_index=0,
            expected_context_items={
                "organisation": None,
                "vorname": "Anna",
                "name": "Muster",
                "strasse": "Beispielweg 1",
                "wohnort": "3000 Bern",
                "anrede": "Liebe Anna",
                "share_count": None,
                "jahr": f"{current_year}",
            },
        )

        ## Sie
        if formal:
            self.assertFillTemplateCalledWith(
                call_index=1,
                expected_context_items={
                    "organisation": None,
                    "anrede": "Sehr geehrter Herr Muster",
                },
            )
        else:
            self.assertFillTemplateCalledWith(
                call_index=1,
                expected_context_items={
                    "organisation": None,
                    "anrede": "Lieber Herr Muster",
                },
            )

        ## Organisation ohne Namen
        self.assertFillTemplateCalledWith(
            call_index=2,
            expected_context_items={
                "organisation": "WBG Test",
                "anrede": "Liebe WBG Test",
            },
        )

        ## Organisation mit Namen
        self.assertFillTemplateCalledWith(
            call_index=3,
            expected_context_items={
                "organisation": "WBG Test",
                "anrede": "Liebe WBG Test, Lieber Ernst",
            },
        )

        settings.GENO_FORMAL = prev_geno_formal

    def test_send_member_bill(self):
        self.form_filter_active_members()
        self.form_select_members()
        self.form_action_list()
        self.form_action_send(formal=False)
        self.form_action_send(formal=True)


class DocumentFormFilterTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_members = []
        cls.test_members.append(
            Address.objects.create(name="Filtertest", first_name="no_invoice")
        )  # 0
        cls.test_members.append(
            Address.objects.create(name="Filtertest", first_name="invoice_catA_old")
        )  # 1
        cls.test_members.append(
            Address.objects.create(name="Filtertest", first_name="invoice_catA_med")
        )  # 2
        cls.test_members.append(
            Address.objects.create(name="Filtertest", first_name="invoice_catA_med_consolidated")
        )  # 3
        cls.test_members.append(
            Address.objects.create(name="Filtertest", first_name="invoice_catA_new")
        )  # 4
        cls.test_members.append(
            Address.objects.create(name="Filtertest", first_name="invoice_catB_new")
        )  # 5

        cls.catA = InvoiceCategory.objects.create(name="catA", reference_id=80)
        cls.catB = InvoiceCategory.objects.create(name="catB", reference_id=81)

        Invoice.objects.create(
            name="Test",
            person=cls.test_members[0],
            invoice_type="Payment",
            invoice_category=cls.catA,
            date=datetime.date(2000, 1, 1),
            amount=Decimal("1.0"),
        )
        Invoice.objects.create(
            name="Test",
            person=cls.test_members[1],
            invoice_type="Invoice",
            invoice_category=cls.catA,
            date=datetime.date(2000, 1, 1),
            amount=Decimal("1.0"),
        )
        Invoice.objects.create(
            name="Test",
            person=cls.test_members[2],
            invoice_type="Invoice",
            invoice_category=cls.catA,
            date=datetime.date(2000, 1, 10),
            amount=Decimal("1.0"),
        )
        Invoice.objects.create(
            name="Test",
            person=cls.test_members[3],
            invoice_type="Invoice",
            invoice_category=cls.catA,
            date=datetime.date(2000, 1, 10),
            amount=Decimal("1.0"),
            consolidated=True,
        )
        Invoice.objects.create(
            name="Test",
            person=cls.test_members[4],
            invoice_type="Invoice",
            invoice_category=cls.catA,
            date=datetime.date(2000, 1, 20),
            amount=Decimal("1.0"),
        )
        Invoice.objects.create(
            name="Test",
            person=cls.test_members[5],
            invoice_type="Invoice",
            invoice_category=cls.catB,
            date=datetime.date(2000, 1, 20),
            amount=Decimal("1.0"),
        )

    def assertInvoiceFilter(self, filterspec, members_include):
        post_data = {
            "base_dataset": "addresses",
            "select_attributeA_value": "--OHNE--",
            "select_attributeB_value": "--OHNE--",
            "select_flag_01": "none",
            "select_flag_02": "none",
            "select_flag_03": "none",
            "select_flag_04": "none",
            "select_flag_05": "none",
            "filter_invoice": "none",
            "filter_invoice_category": "",
            "filter_invoice_consolidated": "none",
            "filter_invoice_daterange_min": "",
            "filter_invoice_daterange_max": "",
        }
        post_data.update(filterspec)
        response = self.client.post("/geno/member/send_mail/", post_data)
        # self.assertInHTML("OJWOIFJOIJ", response.content.decode())
        self.assertRedirects(response, "/geno/member/send_mail/select/")

        response2 = self.client.get("/geno/member/send_mail/select/")
        self.assertEqual(response2.status_code, 200)
        for member in self.test_members:
            if member.first_name in members_include:
                self.assertInHTML(f"Filtertest, {member.first_name}", response2.content.decode())
            else:
                self.assertNotInHTML(
                    f"Filtertest, {member.first_name}", response2.content.decode()
                )

    def test_invoice_filter_none(self):
        self.assertInvoiceFilter(
            {},
            [
                "no_invoice",
                "invoice_catA_old",
                "invoice_catA_med",
                "invoice_catA_med_consolidated",
                "invoice_catA_new",
                "invoice_catB_new",
            ],
        )

    def test_invoice_filter_any(self):
        self.assertInvoiceFilter(
            {"filter_invoice": "include"},
            [
                "invoice_catA_old",
                "invoice_catA_med",
                "invoice_catA_med_consolidated",
                "invoice_catA_new",
                "invoice_catB_new",
            ],
        )

    def test_invoice_filter_any_exclude(self):
        self.assertInvoiceFilter(
            {"filter_invoice": "exclude"},
            [
                "no_invoice",
            ],
        )

    def test_invoice_filter_catA(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "include",
                "filter_invoice_category": self.catA.id,
            },
            [
                "invoice_catA_old",
                "invoice_catA_med",
                "invoice_catA_med_consolidated",
                "invoice_catA_new",
            ],
        )

    def test_invoice_filter_catA_exclude(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "exclude",
                "filter_invoice_category": self.catA.id,
            },
            [
                "no_invoice",
                "invoice_catB_new",
            ],
        )

    def test_invoice_filter_catA_NOT_consolidated(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "include",
                "filter_invoice_category": self.catA.id,
                "filter_invoice_consolidated": "false",
            },
            [
                "invoice_catA_old",
                "invoice_catA_med",
                "invoice_catA_new",
            ],
        )

    def test_invoice_filter_catA_consolidated(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "include",
                "filter_invoice_category": self.catA.id,
                "filter_invoice_consolidated": "true",
            },
            [
                "invoice_catA_med_consolidated",
            ],
        )

    def test_invoice_filter_catA_range_older(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "include",
                "filter_invoice_category": self.catA.id,
                "filter_invoice_daterange_max": "15.01.2000",
            },
            [
                "invoice_catA_old",
                "invoice_catA_med",
                "invoice_catA_med_consolidated",
            ],
        )

    def test_invoice_filter_catA_range_newer(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "include",
                "filter_invoice_category": self.catA.id,
                "filter_invoice_daterange_min": "05.01.2000",
            },
            [
                "invoice_catA_med",
                "invoice_catA_med_consolidated",
                "invoice_catA_new",
            ],
        )

    def test_invoice_filter_catA_range_inside(self):
        self.assertInvoiceFilter(
            {
                "filter_invoice": "include",
                "filter_invoice_category": self.catA.id,
                "filter_invoice_daterange_min": "05.01.2000",
                "filter_invoice_daterange_max": "15.01.2000",
            },
            [
                "invoice_catA_med",
                "invoice_catA_med_consolidated",
            ],
        )


class DocumentProcessTest(GenoAdminTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        geno_testdata.create_contracts(cls)

    def setUp(self):
        super().setUp()
        self.data = {
            "action": "list",  # mail, mail_test, makezip, makezip_pdf, list_xls
            "template_mail": None,
            "subject": "DocumentProcessTest Subject",
            "email_sender": "documentprocesstest@example.com",
            "email_copy": "bcctest@example.com",
            "template_files": [],
            "members": [],
            "change_attribute": None,
            "change_attribute_value": "newAttVal",
            "change_genattribute": None,
            "change_genattribute_value": "newGenAttVal",
        }
        self.year = datetime.datetime.now().year

    def setup_members(self):
        for member in self.members[0:5]:
            self.data["members"].append(
                {
                    "id": member.pk,
                    "member": str(member),
                    "extra_info": "EXTRA_INFO_TEST",
                    "member_type": "member",
                }
            )

    def setup_addresses(self, addresses=None):
        if not addresses:
            addresses = self.addresses[0:5]
        for address in addresses:
            self.data["members"].append(
                {
                    "id": address.pk,
                    "member": str(address),
                    "extra_info": "",
                    "member_type": "address",
                }
            )

    def setup_contracts(self):
        for address in self.addresses[0:5]:
            contract = address.address_contracts.first()
            if contract:
                self.data["members"].append(
                    {
                        "id": address.pk,
                        "contract_id": contract.id,
                        "member": str(address),
                        "extra_info": None,
                        "member_type": "address",
                    }
                )

    def assertResultCount(self, results, n_success, n_warnings, n_errors):
        if "success" in results or n_success:
            self.assertEqual(len(results["success"]), n_success)
        if "warnings" in results or n_warnings:
            self.assertEqual(len(results["warnings"]), n_warnings)
        if "errors" in results or n_errors:
            self.assertEqual(len(results["errors"]), n_errors)

    def assertInResults(self, results, info, logs=None):
        if logs is None:
            logs = []
        for res in results:
            # print(f"Checking: {res['info']}")
            if res["info"] == info:
                if logs:
                    for log in logs:
                        if log not in res["objects"]:
                            raise AssertionError(
                                f"Log {log} not found in result {res['info']}: {res['objects']}."
                            )
                elif logs == [] and "objects" in res:
                    self.assertEqual(res["objects"], [])
                return
        raise AssertionError(f"Result {info} not found in {results}.")

    def test_empty_list(self):
        ret = send_member_mail_process(self.data)
        self.assertResultCount(ret, 0, 0, 0)

    def test_list(self):
        self.setup_members()
        ret = send_member_mail_process(self.data)
        self.assertResultCount(ret, len(self.data["members"]) - 1, 1, 0)
        self.assertInResults(
            ret["success"], "Muster, Hans - EXTRA_INFO_TEST (hans.muster@example.com)"
        )
        self.assertInResults(
            ret["warnings"],
            "Noaddress, Harry - EXTRA_INFO_TEST ()",
            logs=["WARNUNG: Keine Adresse/Ort vorhanden!"],
        )

    def test_list_xls(self):
        self.setup_members()
        self.data["action"] = "list_xls"
        ret = send_member_mail_process(self.data)
        self.assertTrue(isinstance(ret, HttpResponse))
        self.assertEqual(
            ret.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # @patch('geno.exporter.export_data_to_xls')
    # def test_list_xls_mock(self, mock_export):
    #    self.setup_members()
    #    self.data['action'] = "list_xls"
    #    ret = send_member_mail_process(self.data)
    #    mock_export.assert_called_with(
    #        "PdfGenerator: Warning: File invalid.pdf does not exist. Can't merge it."
    #    )

    def test_change_member_attribute(self):
        at = MemberAttributeType.objects.create(name="TestAttribute", description="Test")
        MemberAttribute.objects.create(
            member=self.members[0],
            attribute_type=at,
            date=datetime.date(2000, 1, 1),
            value="oldAttVal",
        )

        self.setup_members()
        self.data["change_attribute"] = at
        ret = send_member_mail_process(self.data)
        self.assertResultCount(ret, len(self.data["members"]) - 1, 1, 0)
        self.assertInResults(
            ret["success"],
            "Muster, Hans - EXTRA_INFO_TEST (hans.muster@example.com)",
            logs=['Mitglieder-Attribut "TestAttribute" geändert: "oldAttVal" -> "newAttVal"'],
        )
        self.assertInResults(
            ret["warnings"],
            "Noaddress, Harry - EXTRA_INFO_TEST ()",
            logs=[
                "WARNUNG: Keine Adresse/Ort vorhanden!",
                'Mitglieder-Attribut "TestAttribute" geändert: "(Kein)" -> "newAttVal"',
            ],
        )

        newatt = MemberAttribute.objects.get(member=self.members[0], attribute_type=at)
        self.assertEqual(newatt.value, "newAttVal")
        self.assertEqual(newatt.date, datetime.date.today())
        newatt = MemberAttribute.objects.get(member=self.members[1], attribute_type=at)
        self.assertEqual(newatt.value, "newAttVal")
        self.assertEqual(newatt.date, datetime.date.today())

    def test_change_generic_attribute(self):
        GenericAttribute.objects.create(
            name="GenTestAttr", content_object=self.addresses[0], value="oldGenAttVal"
        )

        self.setup_addresses()
        self.data["change_genattribute"] = "GenTestAttr"
        ret = send_member_mail_process(self.data)
        self.assertResultCount(ret, len(self.data["members"]) - 1, 1, 0)
        self.assertInResults(
            ret["success"],
            "Muster, Hans -  (hans.muster@example.com)",
            logs=['Allg.Attribut "GenTestAttr" geändert: "oldGenAttVal" -> "newGenAttVal"'],
        )
        self.assertInResults(
            ret["warnings"],
            "Noaddress, Harry -  ()",
            logs=[
                "WARNUNG: Keine Adresse/Ort vorhanden!",
                'Allg.Attribut "GenTestAttr" geändert: "(Kein)" -> "newGenAttVal"',
            ],
        )

        newadr = Address.objects.get(pk=self.addresses[0].id)
        self.assertEqual(newadr.attributes.all()[0].value, "newGenAttVal")
        self.assertEqual(newadr.attributes.all()[0].date, datetime.date.today())
        newadr = Address.objects.get(pk=self.addresses[1].id)
        self.assertEqual(newadr.attributes.all()[0].value, "newGenAttVal")
        self.assertEqual(newadr.attributes.all()[0].date, datetime.date.today())

    def test_send_test_mail(self):
        self.setup_members()
        self.data["action"] = "mail_test"
        self.data["template_mail"] = f"template_id_{self.email_templates[0].pk}"
        ret = send_member_mail_process(self.data)
        self.assertResultCount(ret, len(self.data["members"]) - 1, 1, 0)
        self.assertInResults(
            ret["success"],
            "Muster, Hans - EXTRA_INFO_TEST (hans.muster@example.com)",
            logs=["Email an &quot;Hans Muster&quot; &lt;bcctest@example.com&gt; geschickt."],
        )
        self.assertInResults(
            ret["warnings"],
            "Noaddress, Harry - EXTRA_INFO_TEST ()",
            logs=["KEIN EMAIL GESENDET! Grund: Keine Email-Adresse vorhanden."],
        )

        self.assertEmailSent(
            4,
            4 * ["DocumentProcessTest Subject"],
            "Sehr geehrter Herr Muster\n\nDies ist ein Test für Sie.",
            4 * ["bcctest@example.com"],
        )
        self.assertEqual(mail.outbox[0].from_email, "documentprocesstest@example.com")
        self.assertEqual(mail.outbox[0].bcc, [])

    @patch("geno.models.Address.get_mail_recipient")
    def test_send_mail_recipient(self, mock_get_mail_recipient):
        mock_get_mail_recipient.return_value = '"Mocky Mock" <mock@example.com>'
        self.setup_members()
        self.data["action"] = "mail"
        self.data["template_mail"] = f"template_id_{self.email_templates[0].pk}"
        ret = send_member_mail_process(self.data)
        self.assertInResults(
            ret["success"],
            "Muster, Hans - EXTRA_INFO_TEST (hans.muster@example.com)",
            logs=["Email an &quot;Mocky Mock&quot; &lt;mock@example.com&gt; geschickt."],
        )

        self.assertEmailSent(
            4,
            4 * ["DocumentProcessTest Subject"],
            "Sehr geehrter Herr Muster\n\nDies ist ein Test für Sie.",
            4 * ["mock@example.com"],
        )
        self.assertEqual(mail.outbox[0].from_email, "documentprocesstest@example.com")
        self.assertEqual(mail.outbox[0].bcc, ["bcctest@example.com"])
        self.assertEqual(len(mail.outbox[0].attachments), 0)
        self.assertEqual(len(mail.outbox[0].alternatives), 0)

    def test_send_mail_html(self):
        self.setup_members()
        self.data["action"] = "mail"
        self.data["template_mail"] = f"template_id_{self.email_templates[1].pk}"
        send_member_mail_process(self.data)
        self.assertEmailSent(
            4,
            4 * ["DocumentProcessTest Subject"],
            "Sehr geehrter Herr Muster\n\nAnbei die Rechnung.",
        )
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual("text/html", mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn(
            "<html><body><p>Sehr geehrter Herr Muster</p><p>Anbei die Rechnung.</p></body></html>",
            mail.outbox[0].alternatives[0][0],
        )

    def send_with_templates(self, templates, action="mail"):
        template_list = [templates] if isinstance(templates, str) else templates
        self.data["action"] = action
        self.data["template_mail"] = f"template_id_{self.email_templates[0].pk}"
        self.data["template_files"] = [
            f"ContentTemplate:{ContentTemplate.objects.get(name=name).pk}"
            for name in template_list
        ]
        return send_member_mail_process(self.data)

    def test_send_mail_singlefile(self):
        """One PDF files attached."""
        self.setup_members()
        self.send_with_templates("Test PDF1")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "TestPDF1.pdf")  # testpdf_b1.pdf
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(mail.outbox[0].attachments[0][1], "B1")

    def test_send_mail_twofiles(self):
        """Two PDF files attached."""
        self.setup_members()
        self.send_with_templates(("Test PDF1", "Test PDF2"))
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 2)
        self.assertEqual(len(mail.outbox[1].attachments), 2)
        self.assertEqual(mail.outbox[0].attachments[0][0], "TestPDF1.pdf")  # testpdf_b1.pdf
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertEqual(mail.outbox[0].attachments[1][0], "TestPDF2.pdf")  # testpdf_c1.pdf
        self.assertEqual(mail.outbox[0].attachments[1][2], "application/pdf")
        self.assertInPDF(mail.outbox[0].attachments[0][1], "B1")
        self.assertInPDF(mail.outbox[0].attachments[1][1], "C1")

    def test_send_mail_document_simple(self):
        """Documents are created with simple context only."""
        self.setup_members()
        self.send_with_templates("Simple")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_Simple.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "<adr-line1>: Hans Muster\n",
                "<member_bill_amount>: \n",
                "<n_shares>: \n",
            ],
        )
        self.assertNotInPDF(
            mail.outbox[0].attachments[0][1], "Zahlbar durch"
        )  # Make sure there is no QR-bill

    def test_send_mail_document_statement(self):
        """Documents are created with statement context only."""
        self.setup_members()
        self.send_with_templates("Statement")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_Statement.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "<adr-line1>: Hans Muster\n",
                "<member_bill_amount>: \n",
                "<n_shares>: 4 Anteilscheine\n",
            ],
        )
        self.assertNotInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch",  # Make sure there is no QR-bill
                "<share_count>",
            ],
        )

    def test_send_mail_document_bill(self):
        """Documents are created with billing (default) context only."""
        self.setup_members()
        self.send_with_templates("Bill")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_Bill.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "<adr-line1>: Hans Muster\n",
                "<member_bill_text>: Standard-Rechnungstext\n",
                "<member_bill_amount>: 9.95\n",
                "<n_shares>: \n",
            ],
        )
        self.assertNotInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch",  # Make sure there is no QR-bill
                "<share_count>",
            ],
        )

    def test_send_mail_document_memberbill(self):
        """Documents are created with billing (member) context only."""
        self.setup_members()
        self.send_with_templates("Member Bill")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_MemberBill.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "<adr-line1>: Hans Muster\n",
                "<member_bill_text>: Rechnung-Flag01\n",
                "<member_bill_amount>: 10.00\n",
                "<share_count>: 1\n",  ## Anteilschein freiwillig
                "<n_shares>: \n",
            ],
        )
        self.assertNotInPDF(
            mail.outbox[0].attachments[0][1], "Zahlbar durch"
        )  # Make sure there is no QR-bill

    def test_send_mail_document_qrbill(self):
        """Documents are created with IBAN and QR-infotext and amount."""
        self.setup_members()
        self.send_with_templates("QR-Bill")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_QR-Bill.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster\nBeispielweg 1\nCH-3000 Bern",
                (
                    "Konto / Zahlbar an\n"
                    "CH56 0483 5012 3456 7800 9\n"  # Not QR-IBAN
                    "Genossenschaft Musterweg\n"
                    "Musterweg 1\n"
                    "CH-3000 Bern\n"
                ),
                f"Zusätzliche Informationen\nQR-Infotext {self.year}",
                "Betrag\nCHF\n9.95",
            ],
        )
        self.assertEqual(Invoice.objects.count(), 0)

    def test_send_mail_document_qrbill_noamount(self):
        """Documents are created with IBAN without QR-infotext/amount."""
        self.setup_members()
        self.send_with_templates("QR-Bill Noamount")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_QR-BillNoamount.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH56 0483 5012 3456 7800 9",  # Not QR-IBAN
                "Betrag\nCHF\nAnnahmestelle",  # No amount
            ],
        )
        self.assertNotInPDF(mail.outbox[0].attachments[0][1], "Zusätzliche Informationen")
        self.assertEqual(Invoice.objects.count(), 0)

    def test_send_mail_document_qrbill_ref(self):
        """
        Documents and invoices are created with QR-IBAN, Ref.Nr for address,
        QR-infotext and amount.
        """
        self.setup_members()
        self.send_with_templates("QR-Bill Ref")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_QR-BillRef.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        invoice = Invoice.objects.first()
        self.assertEqual(Invoice.objects.count(), 4)
        self.assertEqual(invoice.amount, Decimal("9.95"))
        self.assertEqual(invoice.invoice_type, "Invoice")
        self.assertEqual(invoice.invoice_category.reference_id, 77)
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster\nBeispielweg 1\nCH-3000 Bern",
                (
                    "Konto / Zahlbar an\n"
                    "CH64 3196 1000 0044 2155 7\n"  # QR-IBAN
                    "Genossenschaft Musterweg\n"
                    "Musterweg 1\n"
                    "CH-3000 Bern\n"
                ),
                f"Referenz\n77 00000 {invoice.id:05} 00000 {self.addresses[0].id:05} {self.year}",
                f"Zusätzliche Informationen\nQR-Infotext {self.year}",
                "Betrag\nCHF\n9.95",
            ],
        )

    def test_send_mail_document_qrbill_ref_dryrun(self):
        """
        Documents are created with QR-IBAN, Ref.Nr for address, QR-infotext and amount,
        but no invoices (dry-run).
        """
        self.setup_members()
        self.send_with_templates("QR-Bill Ref", action="mail_test")
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_QR-BillRef.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH64 3196 1000 0044 2155 7",  # QR-IBAN
                f"Referenz\n77 99999 99999 00000 {self.addresses[0].id:05} {self.year}",
                f"Zusätzliche Informationen\nQR-Infotext {self.year}",
                "Betrag\nCHF\n9.95",
            ],
        )
        self.assertEqual(Invoice.objects.count(), 0)

    def test_send_mail_document_qrbill_ref_contract_no_contract_failure(self):
        """Document creation fails if there is no contract."""
        self.setup_members()
        ret = self.send_with_templates("QR-Bill Ref Contract")
        self.assertResultCount(ret, 0, 0, 1)
        self.assertEmailSent(0)

    def test_send_mail_document_qrbill_ref_contract_noamount(self):
        """
        Documents are created with QR-IBAN, Ref.Nr for contract, QR-info: only rental, NO amount.
        """
        self.setup_contracts()
        self.send_with_templates("QR-Bill Ref Contract Noamount")
        self.assertEmailSent(2)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(
            mail.outbox[0].attachments[0][0], "Muster_Hans_QR-BillRefContractNoamount.pdf"
        )
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH64 3196 1000 0044 2155 7",  # QR-IBAN
                f"Referenz\n12 00000 00000 00000 {self.contracts[0].id:05} {self.year}",
                "Zusätzliche Informationen\n/ Whg. 001a/001b",  # TODO: remove slash?
                "Betrag\nCHF\nAnnahmestelle",
            ],
        )
        self.assertEqual(Invoice.objects.count(), 0)

    def test_send_mail_document_qrbill_ref_contract_noamount_dryrun(self):
        """
        Documents are created with QR-IBAN, Ref.Nr for contract,
        QR-info: only rental, NO amount (dry-run).
        """
        self.setup_contracts()
        self.send_with_templates("QR-Bill Ref Contract Noamount", action="mail_test")
        self.assertEmailSent(2)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(
            mail.outbox[0].attachments[0][0], "Muster_Hans_QR-BillRefContractNoamount.pdf"
        )
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH64 3196 1000 0044 2155 7",  # QR-IBAN
                f"Referenz\n12 00000 00000 00000 {self.contracts[0].id:05} {self.year}",
                "Zusätzliche Informationen\n/ Whg. 001a/001b",  # TODO: remove slash?
                "Betrag\nCHF\nAnnahmestelle",
            ],
        )
        self.assertEqual(Invoice.objects.count(), 0)

    def test_send_mail_document_qrbill_ref_contract(self):
        """
        Documents and invoices are created with QR-IBAN, Ref.Nr for contract,
        QR-infotext+rental and amount.
        """
        self.setup_contracts()
        self.send_with_templates("QR-Bill Ref Contract")
        self.assertEmailSent(2)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertEqual(len(mail.outbox[1].attachments), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_QR-BillRefContract.pdf")
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.amount, Decimal("9.95"))
        self.assertEqual(invoice.invoice_type, "Invoice")
        self.assertEqual(invoice.invoice_category.reference_id, 12)
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH64 3196 1000 0044 2155 7",  # QR-IBAN
                f"Referenz\n12 00000 {invoice.id:05} 00000 {self.contracts[0].id:05} {self.year}",
                f"Zusätzliche Informationen\nQR-Infotext {self.year} / Whg. 001a/001b",
                "Betrag\nCHF\n9.95",
            ],
        )
        self.assertEqual(Invoice.objects.count(), 2)

    def test_send_mail_multiple_documents_multiple_contexts(self):
        """
        Multiple documents are created with the correct context:
        statement + fileA + billing IBAN + fileB + billing QR-IBAN
        """
        self.setup_members()
        self.send_with_templates(("Statement", "Test PDF1", "QR-Bill", "Test PDF2", "QR-Bill Ref"))
        self.assertEmailSent(4)
        self.assertEqual(len(mail.outbox[0].attachments), 5)
        self.assertEqual(len(mail.outbox[1].attachments), 5)

        self.assertEqual(mail.outbox[0].attachments[0][0], "Muster_Hans_Statement.pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "<adr-line1>: Hans Muster\n",
                "<member_bill_amount>: \n",
                "<n_shares>: 4 Anteilscheine\n",
            ],
        )
        self.assertNotInPDF(
            mail.outbox[0].attachments[0][1],
            [
                "Zahlbar durch",  # Make sure there is no QR-bill
                "<share_count>",
            ],
        )

        self.assertEqual(mail.outbox[0].attachments[1][0], "TestPDF1.pdf")  # testpdf_b1.pdf

        self.assertEqual(mail.outbox[0].attachments[2][0], "Muster_Hans_QR-Bill.pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[2][1],
            [
                "<adr-line1>: Hans Muster\n",
                "<member_bill_amount>: 9.95\n",
                "<n_shares>: \n",
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH56 0483 5012 3456 7800 9",  # Not QR-IBAN
                f"Zusätzliche Informationen\nQR-Infotext {self.year}",
                "Betrag\nCHF\n9.95",
            ],
        )

        self.assertEqual(mail.outbox[0].attachments[3][0], "TestPDF2.pdf")  # testpdf_c1.pdf

        self.assertEqual(mail.outbox[0].attachments[4][0], "Muster_Hans_QR-BillRef.pdf")
        self.assertInPDF(
            mail.outbox[0].attachments[4][1],
            [
                "Zahlbar durch\nHans Muster",
                "Konto / Zahlbar an\nCH64 3196 1000 0044 2155 7",  # QR-IBAN
                f"Zusätzliche Informationen\nQR-Infotext {self.year}",
                "Betrag\nCHF\n9.95",
            ],
        )

    ## Already covered by test_send_test_mail
    # def test_skip_no_email:

    def test_skip_manual(self):
        adr_noskip = Address.objects.create(
            name="Noskip", email="noskip@example.com", city_zipcode="3000", city_name="Bern"
        )
        adr_skip = Address.objects.create(
            name="Skip",
            paymentslip=True,
            email="skip@example.com",
            city_zipcode="3000",
            city_name="Bern",
        )
        self.setup_addresses([adr_noskip, adr_skip])

        self.data["action"] = "mail_test"
        self.data["template_mail"] = f"template_id_{self.email_templates[0].pk}"
        ret = send_member_mail_process(self.data)
        self.assertResultCount(ret, len(self.data["members"]) - 1, 1, 0)
        self.assertInResults(
            ret["success"],
            "Noskip,  -  (noskip@example.com)",
            logs=["Email an &quot; Noskip&quot; &lt;bcctest@example.com&gt; geschickt."],
        )
        self.assertInResults(
            ret["warnings"],
            "Skip,  -  (skip@example.com)",
            logs=["KEIN EMAIL GESENDET! Grund: Spezialfall (manuelle Bearbeitung)"],
        )

    def test_noskip_manual_zip(self):
        adr_noskip = Address.objects.create(
            name="Noskip", email="noskip@example.com", city_zipcode="3000", city_name="Bern"
        )
        adr_skip = Address.objects.create(
            name="Skip",
            paymentslip=True,
            email="skip@example.com",
            city_zipcode="3000",
            city_name="Bern",
        )
        self.setup_addresses([adr_noskip, adr_skip])
        self.data["template_files"] = [
            f"ContentTemplate:{ContentTemplate.objects.get(name='Simple').pk}"
        ]
        self.data["action"] = "makezip"
        ret = send_member_mail_process(self.data)
        self.assertTrue(isinstance(ret, HttpResponse))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.headers["Content-Type"], "application/x-zip-compressed")
        self.assertInZIP(ret.content, 2)

    def test_skip_no_statement_data(self):
        """Skip recipients with no statement data."""
        adr_noskip = Address.objects.create(
            name="Noskip", email="noskip@example.com", city_zipcode="3000", city_name="Bern"
        )
        adr_skip = Address.objects.create(
            name="Skip", email="skip@example.com", city_zipcode="3000", city_name="Bern"
        )
        Share.objects.create(
            name=adr_noskip,
            share_type=self.sharetypes[0],
            state="bezahlt",
            date=datetime.date(2000, 2, 15),
            value=1000,
        )
        self.setup_addresses([adr_noskip, adr_skip])

        ret = self.send_with_templates("Statement")
        self.assertEmailSent(1)
        self.assertInResults(
            ret["warnings"],
            "Skip,  -  (skip@example.com)",
            logs=["KEIN EMAIL GESENDET! Grund: Keine Beteiligungen für Kontoauszug."],
        )

    @patch("geno.documents.get_share_statement_data")
    def test_statement_generation_fails(self, mock_get_share_statement_data):
        """Handle failure of statement generation."""
        mock_get_share_statement_data.side_effect = RuntimeError("Test Exception")
        adr_noskip = Address.objects.create(
            name="Noskip", email="noskip@example.com", city_zipcode="3000", city_name="Bern"
        )
        Share.objects.create(
            name=adr_noskip,
            share_type=self.sharetypes[0],
            state="bezahlt",
            date=datetime.date(2000, 2, 15),
            value=1000,
        )
        self.setup_addresses([adr_noskip])

        ret = self.send_with_templates("Statement")
        self.assertEmailSent(0)
        self.assertResultCount(ret, 0, 0, 1)
        self.assertInResults(
            ret["errors"],
            "Fehler beim Erstellen der Dokumente: "
            "Fehler beim Erstellen des Kontoauszugs: Test Exception",
        )

    def test_makezip_document_simple(self):
        """Documents are created in a ZIP file with simple context."""
        self.setup_members()
        self.data["action"] = "makezip"
        self.data["template_files"] = [
            f"ContentTemplate:{ContentTemplate.objects.get(name='Simple').pk}"
        ]
        ret = send_member_mail_process(self.data)
        self.assertEmailSent(0)
        self.assertTrue(isinstance(ret, HttpResponse))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.headers["Content-Type"], "application/x-zip-compressed")
        self.assertInZIP(ret.content, 5, ["Muster_Hans_Simple.odt"])

    def test_makezip_pdf_document_simple(self):
        """PDF documents are created in a ZIP file with simple context."""
        self.setup_members()
        self.data["action"] = "makezip_pdf"
        self.data["template_files"] = [
            f"ContentTemplate:{ContentTemplate.objects.get(name='Simple').pk}"
        ]
        ret = send_member_mail_process(self.data)
        self.assertEmailSent(0)
        self.assertTrue(isinstance(ret, HttpResponse))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.headers["Content-Type"], "application/x-zip-compressed")
        self.assertInZIP(ret.content, 5, ["Muster_Hans_Simple.pdf"])

    ## TODO
    # def test_mail_sending_failure(self):
    #    pass

    # def test_mail_sending_failure_with_invoice_rollback(self):
    #    pass
