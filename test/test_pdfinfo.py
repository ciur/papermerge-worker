import unittest
from pathlib import Path
from pmworker.pdfinfo import get_pagecount


test_dir = Path(__file__).parent
test_data_dir = test_dir / Path("data")
abs_path_input_pdf = test_data_dir / Path("input.de.pdf")


class TestPDFInfo(unittest.TestCase):

    def test_get_pdfcount(self):
        page_count = get_pagecount(abs_path_input_pdf)

        self.assertEqual(
            page_count,
            2,
            f"Document actually has 2 pages, not {page_count}"
        )
