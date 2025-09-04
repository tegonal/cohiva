import os

from pypdf import PdfReader, PdfWriter, Transformation


class PdfGenerator:
    def __init__(self, ignore_missing=True):
        self._output_pdf = PdfWriter()
        self._merge_files = []
        self._ignore_missing = ignore_missing

    def append_pdf_file(self, filename_or_fp, merge_pdfs_on_last_page=None, transform=None):
        if merge_pdfs_on_last_page is None:
            merge_pdfs_on_last_page = []
        if isinstance(filename_or_fp, str):
            with open(filename_or_fp, "rb") as fp:
                self.append_pdf(fp, merge_pdfs_on_last_page, transform)
        else:
            self.append_pdf(filename_or_fp, merge_pdfs_on_last_page, transform)

    def append_pdf(self, fp, merge_pdfs_on_last_page=None, transform=None):
        if merge_pdfs_on_last_page is None:
            merge_pdfs_on_last_page = []
        pdf = PdfReader(fp)
        n_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            if merge_pdfs_on_last_page and i == n_pages - 1:
                self.merge_pages(page, merge_pdfs_on_last_page, transform)
            self._output_pdf.add_page(page)
            for fp in self._merge_files:
                fp.close()
            self._merge_files = []

    def merge_pages(self, page, merge_pdfs, transform):
        if not isinstance(merge_pdfs, list):
            merge_pdfs = [merge_pdfs]
        if transform:
            for var in ("ty", "tx", "dx", "dy"):
                if var not in transform:
                    transform[var] = 0
            if "scale" not in transform:
                transform["scale"] = 1
            transform["ty0"] = transform["ty"]
        elif len(merge_pdfs) != 1:
            raise RuntimeError("Can only merge one PDF to last page!")
        for merge_pdf_file in merge_pdfs:
            if isinstance(merge_pdf_file, str):
                if not os.path.isfile(merge_pdf_file):
                    if self._ignore_missing:
                        continue
                    raise RuntimeError(f"File {merge_pdf_file} does not exist. Can't merge it.")
                fp = open(merge_pdf_file, "rb")
                self._merge_files.append(fp)
                self.merge_page(page, fp, transform)
            else:
                self.merge_page(page, merge_pdf_file, transform)

    def merge_page(self, page, fp, transform):
        merge_pdf = PdfReader(fp)
        if len(merge_pdf.pages) != 1:
            fp.close()
            raise RuntimeError("Can't merge: PDF to merge must have exaclty 1 page!")
        if transform:
            trans = (
                Transformation()
                .scale(transform["scale"])
                .translate(transform["tx"], transform["ty"])
            )
            page.merge_transformed_page(merge_pdf.pages[0], trans)
            transform["ty"] += transform["dy"]
        else:
            page.merge_page(merge_pdf.pages[0])

    def write_file(self, output_filename):
        with open(output_filename, "wb") as fp:
            self._output_pdf.write(fp)
