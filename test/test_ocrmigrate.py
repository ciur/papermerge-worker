import unittest
import os

from pmworker.ocrmigrate import (
    get_pagecount,
    get_assigns_after_delete
)

from pmworker.endpoint import (
    Endpoint, DocumentEp
)


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
            aux_dir="results",
            file_name="x.pdf"
        )
        self.assertEqual(
            2, get_pagecount(doc_ep)
        )

    def test_get_assigns_after_delete(self):
        result = get_assigns_after_delete(
            total_pages=5,
            deleted_pages=[1, 5]
        )
        # after deleting pages 1 and 5,in next version of
        # the document page #1 get the content
        # of previous page #2
        # the document page #2 get the content
        # of previous page #3
        # the document page #3 get the content
        # of previous page #4
        self.assertEqual(
            result,
            [(1, 2), (2, 3), (3, 4)]
        )

        result = get_assigns_after_delete(
            total_pages=5,
            deleted_pages=[2, 3]
        )
        # after deleting pages 2 and 3,in next version of
        # the document page #1 get the content
        # of previous page #1
        # the document page #2 get the content
        # of previous page #4
        # the document page #3 get the content
        # of previous page #5
        self.assertEqual(
            result,
            [(1, 1), (2, 4), (3, 5)]
        )
