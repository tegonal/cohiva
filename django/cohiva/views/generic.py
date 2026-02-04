import io
import os
import tempfile
from zipfile import ZipFile

from django.core.exceptions import ImproperlyConfigured
from django.http import FileResponse, HttpResponseNotFound
from django.views.generic.base import View


class UploadedFileProcessorMixin:
    def __init__(self, *args, **kwargs):
        self.uploaded_file = None
        self.output_files = []

    def set_uploaded_file(self, uploaded_file):
        self.uploaded_file = uploaded_file

    def get_input_files(self):
        """If uploaded_file is a zip file, return the unpacked files, otherwise return the uploaded file."""
        if not self.uploaded_file:
            return
        if self.uploaded_file.name.endswith(".zip"):
            with ZipFile(io.BytesIO(self.uploaded_file.read())) as zip_file:
                for zipinfo in zip_file.infolist():
                    if not (
                        zipinfo.is_dir()
                        or zipinfo.filename.startswith(".")
                        or zipinfo.filename.startswith("_")
                        or ".DS_Store" in zipinfo.filename
                    ):
                        file_like_object = io.BytesIO(zip_file.read(zipinfo))
                        file_like_object.name = zipinfo.filename
                        yield file_like_object
        else:
            yield self.uploaded_file

    def add_output_file(self, filepath, filename, content_type=None, delete_after=False):
        self.output_files.append(
            {
                "filepath": filepath,
                "filename": filename,
                "content_type": content_type,
                "delete_after": delete_after,
            }
        )

    def get_response(self, archive_file_name=None):
        if len(self.output_files) == 1:
            if self.output_files[0]["delete_after"]:
                # Make a temporary copy of the file so we can delete it before sending the response.
                output_file = tempfile.TemporaryFile()
                with open(self.output_files[0]["filepath"], "rb") as source_file:
                    for chunk in iter(lambda: source_file.read(8192), b""):
                        output_file.write(chunk)
                output_file.seek(0)
            else:
                output_file = open(self.output_files[0]["filepath"], "rb")
            resp = FileResponse(
                output_file,
                as_attachment=True,
                filename=self.output_files[0]["filename"],
                content_type=self.output_files[0]["content_type"],
            )
        elif len(self.output_files) > 1:
            file_like_object = io.BytesIO()
            with ZipFile(file_like_object, "w") as archive:
                for f in self.output_files:
                    archive.write(f["filepath"], f["filename"])
            file_like_object.seek(0)
            if not archive_file_name:
                if self.uploaded_file:
                    archive_file_name = f"{self.uploaded_file.name[0:-4]}_resultat.zip"
                else:
                    archive_file_name = "resultat.zip"
            resp = FileResponse(file_like_object, as_attachment=True, filename=archive_file_name)
        else:
            resp = HttpResponseNotFound("Keine Dateien gefunden.")
        for f in self.output_files:
            if f["delete_after"]:
                os.unlink(f["filepath"])
        return resp


class ZipDownloadView(View):
    zipfile_name = "download.zip"

    def get_files(self):
        ## Return array of dicts with keys 'fullpath' and 'archive_filename'.
        raise ImproperlyConfigured("ZipDownloadView requires an implementation of 'get_files()'")

    def get_zipfile_name(self):
        return self.zipfile_name

    def get(self, request, *args, **kwargs):
        file_like_object = io.BytesIO()
        with ZipFile(file_like_object, "w") as archive:
            files = self.get_files()
            if not files:
                return HttpResponseNotFound("Keine Dateien gefunden.")
            for f in files:
                if "content" in f:
                    archive.writestr(f["archive_filename"], f["content"])
                else:
                    archive.write(f["fullpath"], f["archive_filename"])
        file_like_object.seek(0)
        return FileResponse(file_like_object, as_attachment=True, filename=self.get_zipfile_name())


# class ConfirmationMixin:
#    template = 'cohiva/admin_confirm_form.html'
