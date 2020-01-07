import os
from pathlib import Path
import unittest
from pmworker import mime


# points to digilette.testing folder
BASE_DIR = Path(__file__).parent.parent


class TestConvert(unittest.TestCase):

    def test_basic_command_call(self):

        file_path = os.path.join(
            BASE_DIR,
            "data",
            "files",
            "kyuss.pdf"
        )
        mime_type = mime.Mime(filepath=file_path)
        self.assertTrue(
            mime_type.is_pdf()
        )
