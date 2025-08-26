import os
import zoneinfo
from io import BytesIO
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

    def assertPDFPages(self, pdffile_or_bytes, npages_expected):
        pdf = PdfReader(self.get_filelike(pdffile_or_bytes))
        npages = len(pdf.pages)
        if npages != npages_expected:
            raise AssertionError(f"PDF has {npages} pages insted of {npages_expected}")

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
