from django.test import TestCase
from pypdf import PdfReader

from cohiva.utils.pdf import PdfGenerator


class UtilsPdfTestCase(TestCase):
    def assertPDFPages(self, pages):
        r = PdfReader("/tmp/out.pdf")
        self.assertEqual(len(r.pages), len(pages))
        for i, page in enumerate(r.pages):
            text = page.extract_text()
            for text_element in pages[i]:
                self.assertIn(text_element, text)

    def test_pdf_append_filename(self):
        p = PdfGenerator()
        p.append_pdf_file("cohiva/tests/A1A2.pdf")
        p.append_pdf_file("cohiva/tests/B1.pdf")
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["A1"], ["A2"], ["B1"]])

    def test_pdf_append_fp(self):
        p = PdfGenerator()
        with open("cohiva/tests/B1.pdf", "rb") as fp:
            p.append_pdf_file(fp)
        with open("cohiva/tests/A1A2.pdf", "rb") as fp:
            p.append_pdf_file(fp)
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["B1"], ["A1"], ["A2"]])

    def test_pdf_append_merge(self):
        p = PdfGenerator()
        p.append_pdf_file("cohiva/tests/A1A2.pdf", "cohiva/tests/B1.pdf")
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["A1"], ["A2", "B1"]])

    def test_pdf_append_merge_fp(self):
        p = PdfGenerator()
        with open("cohiva/tests/B1.pdf", "rb") as fp:
            p.append_pdf_file("cohiva/tests/A1A2.pdf", fp)
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["A1"], ["A2", "B1"]])

    def test_pdf_append_merge_multipage(self):
        p = PdfGenerator()
        with self.assertRaises(RuntimeError):
            p.append_pdf_file("cohiva/tests/B1.pdf", "cohiva/tests/A1A2.pdf")

    def test_pdf_append_merge_list(self):
        p = PdfGenerator()
        p.append_pdf_file("cohiva/tests/A1A2.pdf", ["cohiva/tests/B1.pdf"])
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["A1"], ["A2", "B1"]])

    def test_pdf_append_merge_list_multi(self):
        p = PdfGenerator()
        with self.assertRaises(RuntimeError):
            p.append_pdf_file(
                "cohiva/tests/A1A2.pdf", ["cohiva/tests/B1.pdf", "cohiva/tests/C1.pdf"]
            )

    def test_pdf_append_merge_list_multi_transform(self):
        p = PdfGenerator()
        p.append_pdf_file("cohiva/tests/A1A2.pdf")
        p.append_pdf_file(
            "cohiva/tests/A1A2.pdf",
            ["cohiva/tests/B1.pdf", "cohiva/tests/C1.pdf"],
            transform={"tx": 60, "ty": 560, "dy": -250, "scale": 0.2},
        )
        p.append_pdf_file("cohiva/tests/B1.pdf")
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["A1"], ["A2"], ["A1"], ["A2", "B1", "C1"], ["B1"]])

    def test_pdf_append_merge_list_multi_transform_with_missing(self):
        p = PdfGenerator()
        p.append_pdf_file("cohiva/tests/A1A2.pdf")
        p.append_pdf_file(
            "cohiva/tests/A1A2.pdf",
            ["cohiva/tests/B1.pdf", "cohiva/tests/C1.pdf", "invalid.pdf"],
            transform={"tx": 60, "ty": 560, "dy": -250, "scale": 0.2},
        )
        p.append_pdf_file("cohiva/tests/B1.pdf")
        p.write_file("/tmp/out.pdf")
        self.assertPDFPages([["A1"], ["A2"], ["A1"], ["A2", "B1", "C1"], ["B1"]])

    def test_pdf_append_merge_raises_with_missing(self):
        p = PdfGenerator(ignore_missing=False)
        p.append_pdf_file("cohiva/tests/A1A2.pdf")
        with self.assertRaises(RuntimeError):
            p.append_pdf_file(
                "cohiva/tests/A1A2.pdf",
                ["cohiva/tests/B1.pdf", "cohiva/tests/C1.pdf", "invalid.pdf"],
            )
