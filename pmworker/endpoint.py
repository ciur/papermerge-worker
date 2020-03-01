import os
import logging
import boto3
from botocore.errorfactory import ClientError


logger = logging.getLogger(__name__)


def get_keyname(s3_url):
    """
    Extracts key part from s3 URL:
        s3_url = s3://my-bucket/some/path/to/x.pdf
        result = some/path/to/x.pdf
    """
    s3 = s3_url.replace('//', '/')
    scheme, bucket, *rest = s3.split('/')
    return '/'.join(rest)


def get_bucketname(s3_url):
    """
    Extracts key part from s3 URL:
        s3_url = s3://my-bucket/some/path/to/x.pdf
        result = my-bucket
    """
    s3 = s3_url.replace('//', '/')
    scheme, bucket, *rest = s3.split('/')
    return bucket


def s3_key_exists(endpoint_url):
    bucketname = get_bucketname(endpoint_url)
    keyname = get_keyname(endpoint_url)
    s3_client = boto3.client('s3')

    try:
        s3_client.head_object(Bucket=bucketname, Key=keyname)
    except ClientError:
        logger.debug(f"Endpoint s3:/{bucketname}/{keyname} does not exist.")
        return False

    return True


class Endpoint:
    """
    Endpoint is a either remote or local root storage
    from/to where files are downloaded/uploaded.

    In case of S3 storage:

        ep_root = Endpoint("s3:/my-bucket")
        ep_root.bucketname == 'my-bucket'

    In case of local storage:

        ep_root = Endpoint("local:/var/media/files")
        ep_root.dirname == '/var/media/files'
    """
    S3 = 's3'
    LOCAL = 'local'

    def __init__(self, url):
        if not url or len(url) < 1:
            raise ValueError("Invalid url")

        self.url = url
        self.local_tmp_ref = None

    @property
    def is_s3(self):
        return self.scheme == Endpoint.S3

    @property
    def scheme(self):
        if ":" in self.url:
            s, path = self.url.split(':')
        else:
            s = Endpoint.LOCAL

        return s

    @property
    def is_local(self):
        return self.scheme == Endpoint.LOCAL

    @property
    def bucketname(self):
        # First part is scheme, then bucket name.
        if not self.is_s3:
            raise ValueError("How come? Bucketname applies only to S3.")

        return self.url.split('/')[1]

    @property
    def dirname(self):
        if not self.is_local:
            raise ValueError("How come? dirname applies only to local.")

        parts = self.url.split('/')[1:]
        joined = '/'.join(parts)

        if self.url.endswith('/'):
            return f"/{joined}"
        else:
            return f"/{joined}/"

    def __str__(self):
        return "Endpoint(%s)" % self.url

    def __repr__(self):
        return "Endpoint(%s)" % self.url


class DocumentEp:
    """
    Document Endpoint:
    <schema>://<media_root>/<aux_dir>/<user_id>/<doc_id>/<version>/<file_name>

    If version = 0, it is not included in Endpoint.
    Document's version is incremented everytime pdftk operation runs on it
    (when pages are deleted, reordered, pasted)
    """

    def __init__(
        self,
        remote_endpoint,
        local_endpoint,
        user_id,
        document_id,
        file_name,
        aux_dir="docs",
        version=0
    ):
        self.remote_endpoint = remote_endpoint
        self.local_endpoint = local_endpoint
        self.user_id = user_id
        self.document_id = document_id
        self.file_name = file_name
        self.aux_dir = aux_dir
        # by default, document has version 0
        self.version = version
        self.pages = "pages"

    def url(self, ep=Endpoint.LOCAL):
        full_path = None

        if ep == Endpoint.S3:
            full_path = (
                f"s3:/{self.bucketname}/"
                f"{self.key}"
            )
        else:
            full_path = f"{self.dirname}{self.file_name}"

        return full_path

    @property
    def dirname(self):
        root_dir = f"{self.local_endpoint.dirname}"

        full_path = (
            f"{root_dir}"
            f"{self.aux_dir}/user_{self.user_id}/"
            f"document_{self.document_id}/"
        )

        if self.version > 0:
            full_path = f"{full_path}v{self.version}/"

        return full_path

    @property
    def pages_dirname(self):
        return f"{self.dirname}{self.pages}/"

    @property
    def bucketname(self):
        return self.remote_endpoint.bucketname

    @property
    def key(self):
        root_dir = f"{self.aux_dir}"

        full_path = (
            f"{root_dir}/user_{self.user_id}/"
            f"document_{self.document_id}/"
        )

        if self.version > 0:
            full_path = f"{full_path}v{self.version}/{self.file_name}"
        else:
            full_path = f"{full_path}{self.file_name}"

        return full_path

    def __repr__(self):
        message = (
            f"DocumentEp(version={self.version},"
            f"remote_endpoint={self.remote_endpoint},"
            f"local_endpoint={self.local_endpoint},"
            f"user_id={self.user_id},"
            f"document_id={self.document_id},"
            f"file_name={self.file_name})"
        )
        return message

    def inc_version(self):
        self.version = self.version + 1

    def exists(self, ep=Endpoint.LOCAL):
        result = False

        if ep == Endpoint.LOCAL:
            result = os.path.exists(self.url(ep=Endpoint.LOCAL))
        else:
            result = s3_key_exists(self.url(ep=Endpoint.S3))

        return result

    def copy_from(doc_ep, aux_dir):
        return DocumentEp(
            remote_endpoint=doc_ep.remote_endpoint,
            local_endpoint=doc_ep.local_endpoint,
            user_id=doc_ep.user_id,
            document_id=doc_ep.document_id,
            file_name=doc_ep.file_name,
            version=doc_ep.version,
            aux_dir=aux_dir
        )


class PageEp:
    """
    schema://.../<doc_id>/pages/<page_num>/<step>/page-<xyz>.jpg
    """

    def __init__(
        self,
        document_ep,
        page_num,
        page_count,
        step=None
    ):
        if not isinstance(page_num, int):
            msg_err = f"PageEp.page_num must be an int. Got {page_num}."
            raise ValueError(msg_err)

        self.document_ep = document_ep
        self.results_document_ep = DocumentEp.copy_from(
            document_ep,
            aux_dir="results"
        )
        self.page_count = page_count
        self.page_num = page_num
        self.step = step
        self.pages = self.document_ep.pages

    @property
    def ppmroot(self):
        # returns schema://.../<doc_id>/pages/<page_num>/<step>/page
        pages_dirname = self.results_document_ep.pages_dirname
        result = (
            f"{pages_dirname}page_{self.page_num}/"
            f"{self.step.percent}/page"
        )
        return result

    @property
    def pages_dirname(self):
        return self.document_ep.pages_dirname

    def exists(self, ep=Endpoint.LOCAL):
        return self.txt_exists(ep)

    def url(self, ep=Endpoint.LOCAL):
        return self.txt_url(ep)

    def txt_url(self, ep=Endpoint.LOCAL):
        result = None

        if ep == Endpoint.LOCAL:
            pages_dirname = self.results_document_ep.pages_dirname
            result = f"{pages_dirname}page_{self.page_num}.txt"
        else:
            aux_dir = self.results_document_ep.aux_dir
            user_id = self.results_document_ep.user_id
            document_id = self.results_document_ep.document_id

            result = (
                f"s3:/{self.results_document_ep.remote_endpoint.bucketname}/"
                f"{aux_dir}/user_{user_id}/"
                f"document_{document_id}/{self.pages}/page_{self.page_num}.txt"
            )

        return result

    def txt_exists(self, ep=Endpoint.LOCAL):
        result = False

        if ep == Endpoint.LOCAL:
            result = os.path.exists(self.txt_url(ep=ep))
        else:
            result = s3_key_exists(self.txt_url(ep=Endpoint.S3))

        return result

    @property
    def bucketname(self):
        return self.results_document_ep.remote_endpoint.bucketname

    def hocr_url(self, ep=Endpoint.LOCAL):
        url = None
        if ep == Endpoint.LOCAL:
            url = f"{self.ppmroot}-{self.ppmtopdf_formated_number}.hocr"
        else:
            aux_dir = self.results_document_ep.aux_dir
            user_id = self.results_document_ep.user_id
            document_id = self.results_document_ep.document_id

            url = (
                f"s3:/{self.results_document_ep.remote_endpoint.bucketname}/"
                f"{aux_dir}/user_{user_id}/"
                f"document_{document_id}/{self.pages}/page_{self.page_num}/"
                f"{self.step.percent}/"
                f"page-{self.ppmtopdf_formated_number}.hocr"
            )

        return url

    def hocr_exists(self, ep=Endpoint.LOCAL):
        result = False

        if ep == Endpoint.LOCAL:
            result = os.path.exists(self.hocr_url(ep=ep))
        elif ep == Endpoint.S3:
            endpoint_url = self.hocr_url(ep=Endpoint.S3)
            result = s3_key_exists(endpoint_url)

        return result

    @property
    def ppmtopdf_formated_number(self):

        if self.page_count <= 9:
            fmt_num = "{num:d}"
        elif self.page_count > 9 and self.page_count < 100:
            fmt_num = "{num:02d}"
        elif self.page_count > 100:
            fmt_num = "{num:003d}"

        return fmt_num.format(
            num=int(self.page_num)
        )

    def img_exists(self, ep=Endpoint.LOCAL):
        result = False

        if ep == Endpoint.LOCAL:
            result = os.path.exists(self.img_url(ep=ep))

        return result

    def img_url(self, ep=Endpoint.LOCAL):
        url = None
        if ep == Endpoint.LOCAL:
            url = f"{self.ppmroot}-{self.ppmtopdf_formated_number}.jpg"
        else:
            aux_dir = self.results_document_ep.aux_dir
            user_id = self.results_document_ep.user_id
            document_id = self.results_document_ep.document_id
            url = (
                f"s3:/{self.results_document_ep.remote_endpoint.bucketname}/"
                f"{aux_dir}/user_{user_id}/"
                f"document_{document_id}/{self.pages}/page_{self.page_num}/"
                f"{self.step.percent}/"
                f"page-{self.ppmtopdf_formated_number}.jpg"
            )

        return url
