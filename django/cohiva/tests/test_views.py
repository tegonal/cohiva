import io
import os
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse, HttpResponseNotFound
from django.test import TestCase

from cohiva.views.generic import UploadedFileProcessorMixin


class UploadedFileProcessorMixinTestCase(TestCase):
    def test_no_input_files(self):
        cls = UploadedFileProcessorMixin()
        input_files = [f for f in cls.get_input_files()]
        self.assertEqual(len(input_files), 0)

    def test_no_output_files(self):
        cls = UploadedFileProcessorMixin()
        response = cls.get_response()
        self.assertTrue(isinstance(response, HttpResponseNotFound))

    def test_single_file(self):
        test_upload = SimpleUploadedFile(
            "test.txt",
            b"Testing",
            content_type="text/plain",
        )
        cls = UploadedFileProcessorMixin()
        cls.set_uploaded_file(test_upload)
        input_files = [f for f in cls.get_input_files()]
        self.assertEqual(len(input_files), 1)
        self.assertEqual(input_files[0], test_upload)

        response_file = "/tmp/response.pdf"
        response_content = b"%PDF-1.4\n%Dummy PDF"
        with open(response_file, "wb") as f:
            f.write(response_content)
        cls.add_output_file(response_file, "test.pdf", "application/pdf")
        response = cls.get_response()
        self.assertTrue(isinstance(response, FileResponse))
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertEqual(
            response.headers["Content-Disposition"], 'attachment; filename="test.pdf"'
        )
        self.assertEqual(response.getvalue(), response_content)
        response.close()
        # Make sure the file was not deleted
        self.assertTrue(os.path.isfile(response_file))
        os.unlink(response_file)

    def test_multiple_files(self):
        file_like_object = io.BytesIO()
        with zipfile.ZipFile(file_like_object, "w") as archive:
            archive.writestr("testA.txt", b"Testing A")
            archive.writestr("testB.txt", b"Testing B")
        file_like_object.seek(0)
        test_upload = SimpleUploadedFile(
            "test_files.zip",
            file_like_object.getvalue(),
            content_type="application/zip",
        )
        cls = UploadedFileProcessorMixin()
        cls.set_uploaded_file(test_upload)
        input_file = [f for f in cls.get_input_files()]
        self.assertEqual(len(input_file), 2)

        response = cls.get_response()
        self.assertTrue(isinstance(response, HttpResponseNotFound))

        response_file_a = "/tmp/responseA.pdf"
        response_content_a = b"%PDF-1.4\n%Dummy PDF A"
        with open(response_file_a, "wb") as f:
            f.write(response_content_a)
        response_file_b = "/tmp/responseB.pdf"
        response_content_b = b"%PDF-1.4\n%Dummy PDF B"
        with open(response_file_b, "wb") as f:
            f.write(response_content_b)
        cls.add_output_file(response_file_a, "testA.pdf", "application/pdf")
        cls.add_output_file(response_file_b, "testB.pdf", "application/pdf")
        response = cls.get_response()
        self.assertTrue(isinstance(response, FileResponse))
        self.assertEqual(response.headers["Content-Type"], "application/zip")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'attachment; filename="test_files_resultat.zip"',
        )
        with zipfile.ZipFile(io.BytesIO(response.getvalue())) as zip_file:
            self.assertEqual(zip_file.read("testA.pdf"), response_content_a)
            self.assertEqual(zip_file.read("testB.pdf"), response_content_b)
        # Make sure the files were not deleted
        self.assertTrue(os.path.isfile(response_file_a))
        self.assertTrue(os.path.isfile(response_file_b))
        os.unlink(response_file_a)
        os.unlink(response_file_b)

    def test_delete_after_single_file(self):
        cls = UploadedFileProcessorMixin()
        response_file = "/tmp/response.pdf"
        response_content = b"%PDF-1.4\n%Dummy PDF"
        with open(response_file, "wb") as f:
            f.write(response_content)
        cls.add_output_file(response_file, "test.pdf", "application/pdf", delete_after=True)
        response = cls.get_response()
        self.assertTrue(isinstance(response, FileResponse))
        response.close()
        # Make sure the file was deleted
        self.assertFalse(os.path.isfile(response_file))

    def test_delete_after_multiple_files(self):
        cls = UploadedFileProcessorMixin()
        response_file_a = "/tmp/responseA.pdf"
        response_content_a = b"%PDF-1.4\n%Dummy PDF A"
        with open(response_file_a, "wb") as f:
            f.write(response_content_a)
        response_file_b = "/tmp/responseB.pdf"
        response_content_b = b"%PDF-1.4\n%Dummy PDF B"
        with open(response_file_b, "wb") as f:
            f.write(response_content_b)
        cls.add_output_file(response_file_a, "testA.pdf", "application/pdf", delete_after=True)
        cls.add_output_file(response_file_b, "testB.pdf", "application/pdf", delete_after=True)
        response = cls.get_response()
        self.assertTrue(isinstance(response, FileResponse))
        # Make sure the files were deleted
        self.assertFalse(os.path.isfile(response_file_a))
        self.assertFalse(os.path.isfile(response_file_b))

    def test_custom_archive_filename(self):
        cls = UploadedFileProcessorMixin()
        response_file_a = "/tmp/responseA.pdf"
        response_content_a = b"%PDF-1.4\n%Dummy PDF A"
        with open(response_file_a, "wb") as f:
            f.write(response_content_a)
        response_file_b = "/tmp/responseB.pdf"
        response_content_b = b"%PDF-1.4\n%Dummy PDF B"
        with open(response_file_b, "wb") as f:
            f.write(response_content_b)
        cls.add_output_file(response_file_a, "testA.pdf", "application/pdf")
        cls.add_output_file(response_file_b, "testB.pdf", "application/pdf")
        response = cls.get_response(archive_file_name="custom.zip")
        self.assertEqual(
            response.headers["Content-Disposition"], 'attachment; filename="custom.zip"'
        )
        os.unlink(response_file_a)
        os.unlink(response_file_b)

    def test_no_custom_archive_filename(self):
        cls = UploadedFileProcessorMixin()
        response_file_a = "/tmp/responseA.pdf"
        response_content_a = b"%PDF-1.4\n%Dummy PDF A"
        with open(response_file_a, "wb") as f:
            f.write(response_content_a)
        response_file_b = "/tmp/responseB.pdf"
        response_content_b = b"%PDF-1.4\n%Dummy PDF B"
        with open(response_file_b, "wb") as f:
            f.write(response_content_b)
        cls.add_output_file(response_file_a, "testA.pdf", "application/pdf")
        cls.add_output_file(response_file_b, "testB.pdf", "application/pdf")
        response = cls.get_response()
        self.assertEqual(
            response.headers["Content-Disposition"], 'attachment; filename="resultat.zip"'
        )
        os.unlink(response_file_a)
        os.unlink(response_file_b)

    def test_custom_archive_filename_single_file(self):
        cls = UploadedFileProcessorMixin()
        response_file_a = "/tmp/responseA.pdf"
        response_content_a = b"%PDF-1.4\n%Dummy PDF A"
        with open(response_file_a, "wb") as f:
            f.write(response_content_a)
        cls.add_output_file(response_file_a, "testA.pdf", "application/pdf")
        response = cls.get_response(archive_file_name="custom.zip")
        self.assertEqual(
            response.headers["Content-Disposition"], 'attachment; filename="testA.pdf"'
        )
        response.close()
        os.unlink(response_file_a)
