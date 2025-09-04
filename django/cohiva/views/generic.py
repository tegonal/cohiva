import io
from zipfile import ZipFile

from django.core.exceptions import ImproperlyConfigured
from django.http import FileResponse, HttpResponseNotFound
from django.views.generic.base import View


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
