import unittest
import os

from pmworker.endpoint import (
    Endpoint, DocumentEp, PageEp,
    get_bucketname, get_keyname
)
from pmworker.step import Step


class TestOthers(unittest.TestCase):

    def test_getbucketname(self):
        self.assertEqual(
            get_bucketname("s3://my-bucket/some/path/to/x.pdf"),
            "my-bucket"
        )
        self.assertEqual(
            get_bucketname("s3:/my-bucket/some/path/to/x.pdf"),
            "my-bucket"
        )
        self.assertEqual(
            get_bucketname("s3:/my-bucket/"),
            "my-bucket"
        )
        self.assertEqual(
            get_bucketname("s3:/my-bucket"),
            "my-bucket"
        )

    def test_getkeyname(self):
        self.assertEqual(
            get_keyname("s3://my-bucket/some/path/to/x.pdf"),
            "some/path/to/x.pdf"
        )
        self.assertEqual(
            get_keyname("s3:/my-bucket/some/path/to/x.pdf"),
            "some/path/to/x.pdf"
        )


class TestEndpoint(unittest.TestCase):

    def test_s3_bucketname(self):
        ep = Endpoint("s3:/constellation/")
        self.assertTrue(ep.is_s3)
        self.assertFalse(ep.is_local)
        self.assertEqual(
            ep.bucketname,
            "constellation"
        )

    def test_s3_bucketname_no_slash(self):
        ep = Endpoint("s3:/kakamaka")
        self.assertEqual(
            ep.bucketname,
            "kakamaka"
        )

    def test_local(self):
        ep = Endpoint("local:/var/media/files")
        self.assertEqual(
            ep.dirname,
            "/var/media/files/"
        )

    def test_repr(self):
        ep = Endpoint("s3:/bucket/")
        self.assertEqual(
            f"{ep}",
            "Endpoint(s3:/bucket/)"
        )


class TestDocumentEp(unittest.TestCase):

    def test_document_url_key(self):
        remote_ep = Endpoint("s3:/silver-bucket/")
        local_ep = Endpoint("local:/var/media/")
        doc_ep = DocumentEp(
            remote_endpoint=remote_ep,
            local_endpoint=local_ep,
            user_id=1,
            document_id=3,
            file_name="contract.pdf"
        )
        self.assertEqual(
            doc_ep.bucketname,
            "silver-bucket"
        )
        self.assertEqual(
            doc_ep.key,
            "docs/user_1/document_3/contract.pdf"
        )

    def test_document_url(self):
        remote_ep = Endpoint("s3:/silver-bucket/")
        local_ep = Endpoint("local:/var/media/")
        doc_ep = DocumentEp(
            remote_endpoint=remote_ep,
            local_endpoint=local_ep,
            user_id=1,
            document_id=3,
            file_name="x.pdf"
        )
        self.assertEqual(
            doc_ep.url(ep=Endpoint.S3),
            "s3:/silver-bucket/docs/user_1/document_3/x.pdf"
        )
        self.assertEqual(
            doc_ep.url(ep=Endpoint.LOCAL),
            "/var/media/docs/user_1/document_3/x.pdf"
        )

    def test_empty_tenant(self):
        """
        With no tenant specified - url to document will
        be without tenant.
        """
        remote_ep = Endpoint("s3:/silver-bucket/")
        local_ep = Endpoint("local:/var/media/")
        doc_ep = DocumentEp(
            remote_endpoint=remote_ep,
            local_endpoint=local_ep,
            user_id=1,
            document_id=3,
            file_name="x.pdf"
        )
        self.assertEqual(
            doc_ep.url(),
            "/var/media/docs/user_1/document_3/x.pdf"
        )


class TestPageEp(unittest.TestCase):
    def test_ppmroot(self):
        remote_ep = Endpoint("s3:/silver-bucket/")
        local_ep = Endpoint("local:/var/media/")
        doc_ep = DocumentEp(
            remote_endpoint=remote_ep,
            local_endpoint=local_ep,
            user_id=1,
            document_id=3,
            file_name="x.pdf"
        )
        page_url = PageEp(
            document_ep=doc_ep,
            page_num=1,
            step=Step(1),
            page_count=3
        )
        self.assertEqual(
            page_url.ppmroot,
            (f"/var/media/results/user_1/"
                f"document_3/pages/page_1/100/page")
        )

    def test_hocr_exists(self):
        local_media = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test",
            "media"
        )
        remote_ep = Endpoint("s3:/test-papermerge/")
        local_ep = Endpoint(f"local:{local_media}")
        doc_ep = DocumentEp(
            remote_endpoint=remote_ep,
            local_endpoint=local_ep,
            user_id=1,
            document_id=3,
            file_name="x.pdf"
        )
        page_ep1 = PageEp(
            document_ep=doc_ep,
            page_num=1,
            step=Step(1),
            page_count=3
        )
        self.assertTrue(
            page_ep1.hocr_exists()
        )
        page_ep2 = PageEp(
            document_ep=doc_ep,
            page_num=2,
            step=Step(1),
            page_count=3
        )
        self.assertFalse(
            page_ep2.hocr_exists()
        )


