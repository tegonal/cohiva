import datetime
import os
import zoneinfo
from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail

## django-filer stuff
from django.core.files import File as DjangoFile
from django.test import TestCase, TransactionTestCase
from filer.models.filemodels import File as FilerFile
from pypdf import PdfReader

import geno.tests.data as testdata
from geno.models import Invoice


class CohivaTestBase:
    UserModel = get_user_model()
    local_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)

    def assertInHTML(self, needle, haystack):
        try:
            super().assertInHTML(needle, haystack)
        except (self.failureException, AssertionError):
            with open("test-failure.html", "w") as outfile:
                outfile.write(haystack)
                print("Wrote assertInHTML haystack to test-failure.html")
            raise

    def assertNotInHTML(self, needle, haystack):
        ## super().assertNotInHTML() will be available in Django 5.1
        ## For now just invert assertInHTML()
        try:
            super().assertInHTML(needle, haystack)
        except AssertionError:
            return

        with open("test-failure.html", "w") as outfile:
            outfile.write(haystack)
            print("Wrote assertInHTML haystack to test-failure.html")
        raise AssertionError(f"Needle {needle} found in HTML!")

    def assertContains(
        self, response, text, count=None, status_code=200, msg_prefix="", html=False
    ):
        try:
            super().assertContains(response, text, count, status_code, msg_prefix, html)
        except self.failureException:
            if status_code in (301, 302):
                print(f"Got redirect: {response.url}")
            if html:
                outfilename = "test-failure.html"
            else:
                outfilename = "test-failure.txt"
            with open(outfilename, "w") as outfile:
                outfile.write(response.content.decode())
                print(f"Wrote assertContains response.content to {outfilename}")
            raise

    def assertInHTMLResponse(self, needle, response, raw=False, allow_redirect=True):
        last_redirect = None
        if allow_redirect:
            max_redirect = 3
            while response.status_code in (301, 302):
                last_redirect = response.url
                # print("Redirecting to: "+last_redirect)
                response = self.client.get(last_redirect)
                max_redirect -= 1
                if max_redirect <= 0:
                    raise Exception("Too many redirections")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        if raw:
            self.assertIn(needle, content)
        else:
            self.assertInHTML(needle, content)
        return (response, content, last_redirect)

    def assertEmailSent(
        self,
        count,
        subject_or_subjectlist=None,
        text_in_body_or_list=None,
        recipient_or_list=None,
        sender=None,
    ):
        if recipient_or_list is None:
            recipient_or_list = []
        if text_in_body_or_list is None:
            text_in_body_or_list = []
        if subject_or_subjectlist is None:
            subject_or_subjectlist = []
        self.assertEqual(len(mail.outbox), count)

        if isinstance(subject_or_subjectlist, str):
            subjects = (subject_or_subjectlist,)
        else:
            subjects = subject_or_subjectlist
        for i, subject in enumerate(subjects):
            self.assertEqual(mail.outbox[i].subject, subject)

        if isinstance(text_in_body_or_list, str):
            texts = (text_in_body_or_list,)
        else:
            texts = text_in_body_or_list
        for i, text in enumerate(texts):
            self.assertIn(text, mail.outbox[i].body)

        if isinstance(recipient_or_list, str):
            recipients = (recipient_or_list,)
        else:
            recipients = recipient_or_list
        for i, recipient in enumerate(recipients):
            self.assertIn(recipient, mail.outbox[i].to[0])

        if sender:
            self.assertIn(sender, mail.outbox[i].from_email)

    def assertNoErrors(self, errorlist):
        if len(errorlist):
            raise AssertionError(
                f"Errorlist has {len(errorlist)} entries. First is: {errorlist[0]}"
            )

    def assertIsFile(self, path):
        if not os.path.isfile(path):
            raise AssertionError("File does not exist: %s" % str(path))

    def get_filelike(self, file_or_bytes):
        if isinstance(file_or_bytes, bytes):
            return BytesIO(file_or_bytes)
        return file_or_bytes

    def assertInPDF(self, pdffile_or_bytes, expected_text_or_list, on_page=None):
        if isinstance(expected_text_or_list, str):
            expected_text_list = [expected_text_or_list]
        else:
            expected_text_list = expected_text_or_list
        pdf = PdfReader(self.get_filelike(pdffile_or_bytes))
        for i, page in enumerate(pdf.pages):
            if not on_page or on_page == i + 1:
                text = page.extract_text()
                if all(expect in text for expect in expected_text_list):
                    return
                print(f"== Page {i + 1} ==")
                print(text)
        if on_page:
            raise AssertionError(
                f"Text not found on page {on_page} in PDF: {expected_text_or_list}"
            )
        else:
            raise AssertionError(f"Text not found in PDF: {expected_text_or_list}")

    def assertNotInPDF(self, pdffile_or_bytes, expected_text_or_list, on_page=None):
        if isinstance(expected_text_or_list, str):
            expected_text_list = [expected_text_or_list]
        else:
            expected_text_list = expected_text_or_list
        pdf = PdfReader(self.get_filelike(pdffile_or_bytes))
        for i, page in enumerate(pdf.pages):
            if not on_page or on_page == i + 1:
                text = page.extract_text()
                for expect in expected_text_list:
                    if expect in text:
                        if on_page:
                            raise AssertionError(
                                f"Text found on page {on_page} in PDF: {expected_text_or_list}"
                            )
                        else:
                            raise AssertionError(f"Text found in PDF: {expected_text_or_list}")

    def assertPDFPages(
        self, pdffile_or_bytes, npages_expected, accept_more_pages_than_expected=False
    ):
        pdf = PdfReader(self.get_filelike(pdffile_or_bytes))
        npages = len(pdf.pages)
        if accept_more_pages_than_expected:
            if npages < npages_expected:
                raise AssertionError(
                    f"PDF has {npages} pages, which is less than the minimum of {npages_expected}"
                )
        else:
            if npages != npages_expected:
                raise AssertionError(f"PDF has {npages} pages instead of {npages_expected}")

    def assertInZIP(self, zipfile_or_bytes, num_files=None, contents=None):
        if contents is None:
            contents = []
        zipfile = ZipFile(self.get_filelike(zipfile_or_bytes))
        zip_contents = zipfile.namelist()
        if num_files is not None and len(zip_contents) != num_files:
            raise AssertionError(
                f"ZIP file contains {len(zip_contents)} files instead of {num_files}."
            )
        if isinstance(contents, str):
            content_list = [contents]
        else:
            content_list = contents
        for content in content_list:
            if content not in zip_contents:
                raise AssertionError(f"File {content} not found in ZIP file.")

    @classmethod
    def addFilerFile(cls, filepath, filename=None, is_public=False):
        if not filename:
            filename = os.path.basename(filepath)
        with open(filepath, "rb") as template_fp:
            return cls.addFilerFD(template_fp, filename, is_public)

    @classmethod
    def addFilerFD(cls, fd, filename, is_public=False):
        file_obj = DjangoFile(fd, name=filename)
        template_file = FilerFile.objects.create(
            owner=cls.su, original_filename=file_obj.name, file=file_obj
        )
        template_file.is_public = is_public
        template_file.save()
        return template_file

    @classmethod
    def tearDownClass(cls):
        cls.clean_up_gnucash_transactions()
        super().tearDownClass()

    @classmethod
    def clean_up_gnucash_transactions(cls):
        for invoice in Invoice.objects.all():
            # print(f"Deleting test invoice {invoice.id}")
            invoice.delete()


class BaseTestCase(CohivaTestBase, TestCase):
    pass


class BaseTransactionTestCase(CohivaTestBase, TransactionTestCase):
    pass


class GenoAdminTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        testdata.create_members(cls)
        testdata.create_children(cls)
        testdata.create_shares(cls)
        testdata.create_users(cls)
        testdata.create_templates(cls)
        testdata.create_documenttypes(cls)
        testdata.create_invoicecategories(cls)

    def setUp(self):
        self.client.login(username="superuser", password="secret")


def fill_template_effect(template, context, output_format="odt"):
    odt_path = "/tmp/mock_odtfile.odt"
    if not os.path.exists(odt_path):
        with open(odt_path, "wb") as f:
            f.write(b"ODT mock\n")
    return odt_path


def odt2pdf_effect(odtfile, instance_tag="default"):
    pdf_path = "/tmp/mock_pdffile.pdf"
    if not os.path.exists(pdf_path):
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.1\n%mock\n")
    return pdf_path


class DocumentCreationMockMixin:
    """
    Mixin that patches `fill_template_pod` and `odt2pdf` and provides helper assertions.
    """

    patch_target_fill_template = "geno.utils.fill_template_pod"
    patch_target_odt2pdf = "geno.utils.odt2pdf"

    def setUp(self):
        super().setUp()
        fill_template_patcher = patch(self.patch_target_fill_template)
        self.mock_fill_template = fill_template_patcher.start()
        self.mock_fill_template.side_effect = fill_template_effect
        self.addCleanup(fill_template_patcher.stop)

        odt2pdf_patcher = patch(self.patch_target_odt2pdf)
        self.mock_odt2pdf = odt2pdf_patcher.start()
        self.mock_odt2pdf.side_effect = odt2pdf_effect
        self.addCleanup(odt2pdf_patcher.stop)

    def reset_mocks(self):
        self.mock_fill_template.reset_mock()
        self.mock_odt2pdf.reset_mock()

    def assertMocksCallCount(self, expected_count):
        self.assertEqual(self.mock_fill_template.call_count, expected_count)
        self.assertEqual(self.mock_odt2pdf.call_count, expected_count)

    def assertFillTemplateCalledOnce(self):
        self.mock_fill_template.assert_called_once()

    def assertFillTemplateCalledWith(
        self, template=None, expected_context_items=None, call_index=None
    ):
        if template:
            self.assertFillTemplateCalledWithTemplate(template, call_index)
        if expected_context_items:
            self.assertFillTemplateContextContains(expected_context_items, call_index)
        if not template and not expected_context_items:
            raise AssertionError("assertFillTemplateCalledWith called without arguments.")

    def assertFillTemplateCalledWithTemplate(self, template, call_index=None):
        """
        Assert that fill_template_pod was called with the given template.

        - If call_index is None: check that *any* call used this template.
        - If call_index is an integer: check only that specific call.
        """

        if not self.mock_fill_template.called:
            raise AssertionError("fill_template_pod was never called.")

        calls = self.mock_fill_template.call_args_list

        # Helper to extract template argument
        def extract_template(call):
            args, kwargs = call
            return kwargs.get("template") or args[0]

        # Check a specific call
        if call_index is not None:
            try:
                call = calls[call_index]
            except IndexError:
                raise AssertionError(
                    f"fill_template_pod was called {len(calls)} times, "
                    f"but call_index {call_index} was requested."
                )

            actual_template = extract_template(call)
            if actual_template != template:
                raise AssertionError(
                    f"In call {call_index}, expected template {template!r}, "
                    f"but got {actual_template!r}."
                )
            return  # success

        # No call_index → check ANY call
        for call in calls:
            if extract_template(call) == template:
                return  # success

        # If we reach here → no call matched
        formatted_calls = "\n".join(
            f"call[{i}].template = {extract_template(call)!r}" for i, call in enumerate(calls)
        )
        raise AssertionError(
            f"No call to fill_template_pod used template {template!r}.\n\n"
            f"Templates used in calls:\n{formatted_calls}"
        )

    def assertFillTemplateContextContains(self, expected_items: dict, call_index=None):
        """
        Assert that the context passed to fill_template_pod contains expected_items.

        - If call_index is None: check that *any* call contains the items.
        - If call_index is an integer: check that specific call.
        """

        calls = self.mock_fill_template.call_args_list

        def extract_context(call):
            args, kwargs = call
            return kwargs.get("context") or args[1]

        # Check a specific call
        if call_index is not None:
            try:
                call = calls[call_index]
            except IndexError:
                raise AssertionError(
                    f"fill_template_pod was called {len(calls)} times, "
                    f"but call_index {call_index} was requested."
                )

            context = extract_context(call)
            for key, value in expected_items.items():
                if key not in context:
                    if value is None:
                        # None means that the key can or should be missing
                        continue
                    print(context)
                    raise AssertionError(f"In call {call_index}, context missing key {key!r}.")
                if value is None:
                    if context[key] not in (None, ""):
                        raise AssertionError(
                            f"In call {call_index}, expected key {key!r} to be missing, "
                            f"but got {context[key]}."
                        )
                elif context[key] != value and str(context[key]) != str(value):
                    raise AssertionError(
                        f"In call {call_index}, key {key!r}: "
                        f"expected {value!r}, got {context[key]!r}."
                    )
            return  # success

        # No call_index → check ANY call
        for call in calls:
            context = extract_context(call)

            if all(key in context and context[key] == val for key, val in expected_items.items()):
                return  # success: at least one call matched

        # If we reach here → no calls matched
        formatted_calls = "\n".join(
            f"call[{i}].context = {extract_context(call)}" for i, call in enumerate(calls)
        )
        raise AssertionError(
            "No call to fill_template_pod had a context containing the expected items.\n\n"
            f"Expected items: {expected_items}\n\n"
            f"All contexts:\n{formatted_calls}"
        )

    def assertOdt2PdfCalledOnce(self):
        self.mock_odt2pdf.assert_called_once()

    def assertOdt2PdfCalledWithFile(self, odtfile, call_index=None):
        """
        Assert that odt2pdf was called with the given odtfile.

        - If call_index is None: check that *any* call used this odtfile.
        - If call_index is an integer: check only that specific call.
        """

        if not self.mock_odt2pdf.called:
            raise AssertionError("odt2pdf was never called.")

        calls = self.mock_odt2pdf.call_args_list

        # Helper to extract odtfile argument
        def extract_odtfile(call):
            args, kwargs = call
            return kwargs.get("odtfile") or args[0]

        # Check a specific call
        if call_index is not None:
            try:
                call = calls[call_index]
            except IndexError:
                raise AssertionError(
                    f"odt2pdf was called {len(calls)} times, "
                    f"but call_index {call_index} was requested."
                )

            actual_odtfile = extract_odtfile(call)
            if actual_odtfile != odtfile:
                raise AssertionError(
                    f"In call {call_index}, expected odtfile {odtfile!r}, "
                    f"but got {actual_odtfile!r}."
                )
            return  # success

        # No call_index → check ANY call
        for call in calls:
            if extract_odtfile(call) == odtfile:
                return  # success

        # If we reach here → no call matched
        formatted_calls = "\n".join(
            f"call[{i}].odtfile = {extract_odtfile(call)!r}" for i, call in enumerate(calls)
        )
        raise AssertionError(
            f"No call to odt2pdf used odtfile {odtfile!r}.\n\n"
            f"Templates used in calls:\n{formatted_calls}"
        )


class MockDate(datetime.date):
    """Mocks datetime.date.today() so it always returns a constant 2025-01-15"""

    @classmethod
    def today(cls):
        return cls(2025, 1, 15)
