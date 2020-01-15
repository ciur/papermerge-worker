import os
from pathlib import Path
import unittest
from pmworker import mime

DATA_DIR = os.path.join(
    Path(__file__).parent,
    'data'
)


class TestConvert(unittest.TestCase):

    def test_basic_command_call(self):

        file_path = os.path.join(
            DATA_DIR,
            "input.de.pdf"
        )
        mime_type = mime.Mime(filepath=file_path)
        self.assertTrue(
            mime_type.is_pdf()
        )
