import os
import pwd
import grp
from pathlib import Path
import shutil
import boto3
import botocore
import tempfile
import logging

from pmworker.endpoint import (
    Endpoint,
    get_keyname,
    get_bucketname,
    s3_key_exists
)

BASE_DIR = Path(__file__).parent.parent
logger = logging.getLogger(__name__)


def upload_txt(page_url):
    s3_url = page_url.txt_url(ep=Endpoint.S3)
    txt_url = page_url.txt_url()
    bucketname = get_bucketname(s3_url)
    keyname = get_keyname(s3_url)
    s3_client = boto3.client('s3')

    logger.debug(
        f"Uploading to bucket={bucketname} "
        f"Keyname={keyname} "
        f"txt_url={txt_url} "
        f"s3_url={s3_url}."
    )
    s3_client.upload_file(
        page_url.txt_url(),
        bucketname,
        keyname
    )


def upload_hocr(page_url):
    s3_url = page_url.hocr_url(ep=Endpoint.S3)
    hocr_url = page_url.hocr_url()
    bucketname = get_bucketname(s3_url)
    keyname = get_keyname(s3_url)
    s3_client = boto3.client('s3')

    logger.debug(
        f"Uploading to bucket={bucketname} "
        f"Keyname={keyname} "
        f"hocr_url={hocr_url} "
        f"s3_url={s3_url}."
    )
    s3_client.upload_file(
        hocr_url,
        bucketname,
        keyname
    )


def upload_img(page_url):
    s3_url = page_url.img_url(ep=Endpoint.S3)
    img_url = page_url.img_url()
    bucketname = get_bucketname(s3_url)
    keyname = get_keyname(s3_url)
    s3_client = boto3.client('s3')

    logger.debug(
        f"Uploading to bucket={bucketname} "
        f"Keyname={keyname} "
        f"img_url={img_url} "
        f"s3_url={s3_url}."
    )
    s3_client.upload_file(
        img_url,
        bucketname,
        keyname
    )


def upload_document_to_s3(doc_ep):
    s3_url = doc_ep.url(ep=Endpoint.S3)
    local_url = doc_ep.url()
    bucketname = get_bucketname(s3_url)
    keyname = get_keyname(s3_url)
    s3_client = boto3.client('s3')

    if not os.path.exists(local_url):
        raise ValueError(f"{local_url} path does not exits")

    logger.debug(
        f"upload_document {local_url} to s3:/{bucketname}{keyname}"
    )

    s3_client.upload_file(
        local_url,
        bucketname,
        keyname
    )


def download_hocr(page_ep):

    if page_ep.hocr_exists():
        return True

    remote_abspath = page_ep.hocr_url(ep=Endpoint.S3)
    local_abspath = page_ep.hocr_url()
    local_dirname = os.path.dirname(local_abspath)

    if not os.path.exists(
        os.path.dirname(local_abspath)
    ):
        logger.debug(f"{local_dirname} does not exists. Creating.")
        os.makedirs(
            local_dirname, exist_ok=True
        )
    else:
        logger.debug(f"{local_dirname} already exists.")

    s3_client = boto3.client('s3')

    bucketname = get_bucketname(
        page_ep.hocr_url(ep=Endpoint.S3)
    )

    keyname = get_keyname(
        page_ep.hocr_url(ep=Endpoint.S3)
    )

    if not s3_key_exists(remote_abspath):
        logger.info(
            f"Endpoint s3:/{bucketname}/{keyname} missing"
        )
        return False

    try:
        logger.debug((
            f"Downloading {remote_abspath} to {local_abspath}"
        ))
        logger.debug(
            f"Uploading to bucket={bucketname} "
            f"Keyname={keyname} "
            f"Local={local_abspath}."
        )
        s3_client.download_file(
            bucketname,
            keyname,
            local_abspath
        )
    except botocore.exceptions.ClientError:
        logger.error(
            f"Error while downloading "
            f" {remote_abspath} to {local_abspath}"
            f" bucketname={bucketname} keyname={keyname}",
            exc_info=True
        )
        return False

    return True


def download(
    model_endpoint
):
    """
    model_endpoint is instance of one of:

        * pmworker.endpoint.DocumentUrl
        * pmworker.endpoint.PageUrl.

    Will download Document original file or Page associated .txt file
    from remote S3 location (shared storage) to local MEDIA_ROOT.

    This function makes sense only in case of settings.S3=True i.e.
    only if S3 media storage is enabled.
    """

    if model_endpoint.exists():
        return True

    remote_abspath = model_endpoint.url(ep=Endpoint.S3)
    local_abspath = model_endpoint.url()
    local_dirname = os.path.dirname(local_abspath)

    if not os.path.exists(
        os.path.dirname(local_abspath)
    ):
        logger.debug(f"{local_dirname} does not exists. Creating.")
        os.makedirs(
            local_dirname, exist_ok=True
        )
    else:
        logger.debug(f"{local_dirname} already exists.")

    # if not s3_download:
    #    logger.debug("s3_download=False. Use test data dir.")
    #    logger.debug(f"Using file {test_local_alternative}")
    #    copy2doc_url(
    #        src_file_path=test_local_alternative,
    #        doc_url=model_endpoint.url()
    #    )

    s3_client = boto3.client('s3')

    bucketname = get_bucketname(
        model_endpoint.url(ep=Endpoint.S3)
    )

    keyname = get_keyname(
        model_endpoint.url(ep=Endpoint.S3)
    )

    if not model_endpoint.exists(ep=Endpoint.S3):
        logger.info(
            f"Endpoint s3:/{bucketname}/{keyname} missing"
        )
        return False

    try:
        logger.debug((
            f"Downloading {remote_abspath} to {local_abspath}"
        ))
        logger.debug(
            f"Uploading to bucket={bucketname} "
            f"Keyname={keyname} "
            f"Local={local_abspath}."
        )
        s3_client.download_file(
            bucketname,
            keyname,
            local_abspath
        )
    except botocore.exceptions.ClientError:
        logger.error(
            f"Error while downloading "
            f" {remote_abspath} to {local_abspath}"
            f" bucketname={bucketname} keyname={keyname}",
            exc_info=True
        )
        return False

    return True


def copy2doc_url(
    src_file_path,
    doc_url,
    user="dgl",
    group="www-dgl"
):
    dirname = os.path.dirname(doc_url)

    if not os.path.exists(
        dirname
    ):
        os.makedirs(
            dirname, exist_ok=True
        )
        try:
            # if provided user/group exsits
            # change owner of the dir to given user/group
            pwd.getpwnam(user)
            grp.getgrnam(group)
            shutil.chown(
                dirname,
                user=user,
                group=group
            )
        except KeyError:
            # otherwise leave current process' user/group
            pass
    logger.debug(
        f"copy2doc_url {src_file_path} to {doc_url}"
    )
    shutil.copyfile(
        src_file_path,
        doc_url
    )
    try:
        # if provided user/group exsits
        # change owner of the dir to given user/group
        pwd.getpwnam(user)
        grp.getgrnam(group)
        shutil.chown(
            src_file_path,
            user=user,
            group=group
        )
    except KeyError:
        # otherwise leave current process's user/group
        pass


class Storage:
    """
    Storage class binds endpoints with local tmp file
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.tmpfile = None

    def download_to(self, local_abspath):
        """
        Downloads file from remote storge to local
        """
        logger.info("download_to endpoint({}) to {}".format(
            self.endpoint,
            local_abspath
        ))
        s3_client = boto3.client('s3')

        if not os.path.exists(
            os.path.dirname(local_abspath)
        ):
            os.makedirs(
                os.path.dirname(local_abspath), exist_ok=True
            )

        # Download the file from S3
        try:
            s3_client.download_file(
                self.endpoint.bucketname,
                self.endpoint.key,
                local_abspath
            )
        except botocore.exceptions.ClientError:
            logger.error(
                "Error while downloading endpoint {} to {}".format(
                    self.endpoint,
                    local_abspath
                ),
                exc_info=True
            )

    def download(self, filename=None):
        """
        Returns NameTemporarayFile instance
        """
        logger.debug("Storage.download for {}".format(self.endpoint))

        if not self.endpoint.is_s3:
            return None

        if not filename:
            filename = self.endpoint.key

        if not filename:
            raise ValueError("s3keyname missing")

        tmpfile = tempfile.NamedTemporaryFile()

        s3_client = boto3.client('s3')
        logger.debug("Downloading {}/{} -> to local {}".format(
            self.endpoint.bucketname,
            filename,
            tmpfile.name
        ))
        # Download the file from S3
        s3_client.download_file(
            self.endpoint.bucketname,
            filename,
            tmpfile.name
        )

        self.tmpfile = tmpfile

        logger.debug("Storage.download OK -> {}".format(tmpfile))
        return tmpfile

    def __enter__(self):
        return self.download()

    def __exit__(self, *args):
        self.tmpfile.close()

    def upload(self, filename, content):
        tmp_local = tempfile.NamedTemporaryFile(
            mode='w+',
            encoding='utf-8'
        )
        tmp_local.write(content)
        tmp_local.flush()

        s3_client = boto3.client('s3')
        s3_client.upload_file(
            tmp_local.name,
            self.endpoint.bucketname,
            filename
        )
        tmp_local.close()

    def remove(self, filename):
        s3_client = boto3.client('s3')
        s3_client.delete_object(
            Bucket=self.endpoint.bucketname,
            Key=filename
        )

    @property
    def exists(self):
        s3 = boto3.resource('s3')
        try:
            s3.Object(
                self.endpoint.bucketname,
                self.endpoint.key
            ).load()
        except botocore.exceptions.ClientError as e:
            # Hopefully I am not masking any bad ass errors here
            return False

        return True

    def get_text_content(self):
        tmp_local = self.download()
        with open(tmp_local.name, 'r+', encoding='utf-8') as f:
            text = f.read()

        return text
