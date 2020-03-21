import unittest
from pathlib import Path
from pmworker.pdftk import (
    cat_ranges_for_delete,
    cat_ranges_for_reorder,
    split_ranges
)


test_dir = Path(__file__).parent
test_data_dir = test_dir / Path("data")
abs_path_input_pdf = test_data_dir / Path("input.de.pdf")


class TestPDFTk(unittest.TestCase):

    def test_split_ranges_input_1(self):
        """
        Input: total = 9, after=1, before=False
        Output: list1 = [1]; list2 = [2, 3, 4, ..., 9].
        """
        list1, list2 = split_ranges(
            total=9,
            after=1,
            before=False
        )

        self.assertEqual(
            list1,
            [1]
        )
        self.assertEqual(
            list2,
            [2, 3, 4, 5, 6, 7, 8, 9]
        )

    def test_split_ranges_input_2(self):
        """
        Input: total = 9; after=False, before=1
        Output: list1 = [], list2 = [1, 2, 3, 4, ..., 9]
        """
        list1, list2 = split_ranges(
            total=9,
            after=False,
            before=1
        )

        self.assertEqual(
            list1,
            []
        )
        self.assertEqual(
            list2,
            [1, 2, 3, 4, 5, 6, 7, 8, 9]
        )

    def test_split_ranges_input_3(self):
        """
        Input: total = 5; after=4; before=False
        Output: list1 = [1, 2, 3, 4] list2 = [5]
        """
        list1, list2 = split_ranges(
            total=5,
            after=4,
            before=False
        )

        self.assertEqual(
            list1,
            [1, 2, 3, 4]
        )
        self.assertEqual(
            list2,
            [5]
        )

    def test_split_ranges_input_4(self):
        """
        Input: total = 5; after=False; before=False
        Output: list1 = [1, 2, 3, 4, 5] list2 = []
        """
        list1, list2 = split_ranges(
            total=5,
            after=False,
            before=False
        )

        self.assertEqual(
            list1,
            [1, 2, 3, 4, 5]
        )
        self.assertEqual(
            list2,
            []
        )

    def test_cat_ranger_for_reorder(self):
        # swap first and second pages
        result = cat_ranges_for_reorder(
            page_count=4,
            new_order=[
                {'page_num': 2, 'page_order': 1},
                {'page_num': 1, 'page_order': 2},
                {'page_num': 3, 'page_order': 3},
                {'page_num': 4, 'page_order': 4}
            ]
        )
        self.assertEqual(
            result,
            [2, 1, 3, 4],
        )

        # swap first and last pages
        result = cat_ranges_for_reorder(
            page_count=4,
            new_order=[
                {'page_num': 4, 'page_order': 1},
                {'page_num': 2, 'page_order': 2},
                {'page_num': 3, 'page_order': 3},
                {'page_num': 1, 'page_order': 4}
            ]
        )
        self.assertEqual(
            result,
            [4, 2, 3, 1],
        )

        # swap pages in two pages document
        result = cat_ranges_for_reorder(
            page_count=2,
            new_order=[
                {'page_num': 2, 'page_order': 1},
                {'page_num': 1, 'page_order': 2},
            ]
        )
        self.assertEqual(
            result,
            [2, 1],
        )

    def test_cat_ranges_for_delete(self):
        result = cat_ranges_for_delete(
            page_count=8,
            page_numbers=[3]
        )
        self.assertEqual(
            result,
            [1, 2, 4, 5, 6, 7, 8],
        )

        result = cat_ranges_for_delete(
            page_count=8,
            page_numbers=[1, 2, 3]
        )
        self.assertEqual(
            result,
            [4, 5, 6, 7, 8],
        )
        result = cat_ranges_for_delete(
            page_count=8,
            page_numbers=[1, 8]
        )
        self.assertEqual(
            result,
            [2, 3, 4, 5, 6, 7],
        )

