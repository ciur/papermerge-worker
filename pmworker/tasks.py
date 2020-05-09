from __future__ import absolute_import, unicode_literals
import logging
import time

from pmworker import mime
from pmworker.pdfinfo import get_pagecount
from pmworker.storage import (
    upload_txt,
    upload_img,
    upload_hocr,
    download
)
from pmworker.endpoint import (
    DocumentEp,
    PageEp,
    Endpoint
)
from pmworker.step import (Step, Steps)
from pmworker.shortcuts import (
    extract_img,
    extract_hocr,
    extract_txt
)
from pmworker import pdftk
from celery import shared_task

logger = logging.getLogger(__name__)


def upload_page(page_url):

    upload_txt(page_url)

    for step in Steps():
        if not step.is_thumbnail:
            page_url.step = step
            upload_hocr(page_url)
            upload_img(page_url)


def ocr_page_pdf(
    doc_ep,
    page_num,
    lang
):
    page_count = get_pagecount(doc_ep.url())
    logger.debug(f"page_count={page_count}")
    if page_num <= page_count:
        page_url = PageEp(
            document_ep=doc_ep,
            page_num=page_num,
            step=Step(1),
            page_count=page_count
        )
        extract_img(page_url)
        extract_txt(
            page_url,
            lang=lang
        )

        for step in Steps():
            page_url.step = step
            extract_img(page_url)
            # tesseract unterhalt-1.jpg page-1 -l deu hocr
            if not step.is_thumbnail:
                extract_hocr(
                    page_url,
                    lang=lang
                )

    return page_url


@shared_task(bind=True)
def ocr_page(
    self,
    user_id,
    document_id,
    file_name,
    page_num,
    lang,
    s3_upload=True,
    s3_download=True,
    test_local_alternative=None
):
    # A task being bound (bind=True) means the first argument
    # to the task will always be the
    # task instance (self).
    # https://celery.readthedocs.io/en/latest/userguide/tasks.html#bound-tasks
    logger.info(
        f"worker_log task_id={self.request.id}"
        f" user_id={user_id} doc_id={document_id}"
        f" page_num={page_num}"
    )
    t1 = time.time()
    lang = lang.lower()

    doc_ep = DocumentEp(
        user_id=user_id,
        document_id=document_id,
        file_name=file_name,
    )

    logger.debug(
        f"Received document_url={doc_ep.url(Endpoint.S3)}"
    )

    if not doc_ep.exists():
        logger.debug((
            f"doc_ep={doc_ep.url()} does not exists."
            f"Processing with download."
        ))
        download(
            doc_ep,
            s3_download=s3_download,
            test_local_alternative=test_local_alternative
        )
    else:
        logger.debug(f"Local copy {doc_ep.url()} exists.")

    mime_type = mime.Mime(doc_ep.url())

    page_ep = None
    page_type = ''
    if mime_type.is_pdf():
        tx1 = time.time()
        page_ep = ocr_page_pdf(
            doc_ep=doc_ep,
            page_num=page_num,
            lang=lang
        )
        page_type = 'pdf'
        tx2 = time.time()
        logger.info(
            f"worker_log task_id={self.request.id}"
            f" user_id={user_id}"
            f" doc_id={document_id}"
            f" page_num={page_num} page_type=pdf page_ocr_time={tx2-tx1:.2f}"
        )
    else:
        logger.info(
            f"worker_log task_id={self.request.id}"
            f" user_id={user_id}"
            f" doc_id={document_id}"
            f" page_num={page_num} error=Unkown file type"
        )
        return True

    if page_ep and s3_upload:
        upload_page(page_ep)
        logger.info(
            f"worker_log task_id={self.request.id}"
            f" user_id={user_id}"
            f" doc_id={document_id}"
            f" page_num={page_num} uploaded={page_ep.url(Endpoint.S3)}"
        )

    t2 = time.time()
    logger.info(
        f"worker_log success task_id={self.request.id}"
        f" user_id={user_id} doc_id={document_id}"
        f" page_num={page_num} page_type={page_type}"
        f" total_exec_time={t2-t1:.2f}"
    )

    return True
