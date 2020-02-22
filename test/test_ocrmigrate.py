import unittest
import os

from pmworker.ocrmigrate import (
    get_pagecount,
    OcrMigrate
)

from pmworker.endpoint import (
    Endpoint, DocumentEp, PageEp,
    get_bucketname, get_keyname
)
from pmworker.step import Step


class TestOthers(unittest.TestCase):

    def setUp(self):
        self.local_media = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test",
            "media"
        )

    def test_getbucketname(self):
        remote_ep = Endpoint("s3:/test-papermerge/")
        local_ep = Endpoint(f"local:{self.local_media}")
        doc_ep = DocumentEp(
            remote_endpoint=remote_ep,
            local_endpoint=local_ep,
            user_id=1,
            document_id=3,
            file_name="x.pdf"
        )
        self.assertEqual(
            2, get_pagecount(doc_ep)
        )
