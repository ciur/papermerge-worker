import unittest
from pathlib import Path
from pmworker.pdftk import cat_ranges_for_delete


test_dir = Path(__file__).parent
test_data_dir = test_dir / Path("data")
abs_path_input_pdf = test_data_dir / Path("input.de.pdf")


class TestPDFTk(unittest.TestCase):

    def test_cat_ranges_for_delete(self):
        result = cat_ranges_for_delete(
            page_count=22,
            page_numbers=[3]
        )
        self.assertEqual(
            result,
            "1-2 3-22",
        )
