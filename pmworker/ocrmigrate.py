import shutil
from os import listdir
from os.path import isfile, join
from pmworker.endpoint import (DocumentEp, PageEp)
from pmworker.step import Steps

"""
OCR operations are per page. Cut/Paste/Delete/Reorder are per page as well.
So it does not make sense to rerun such a heavy operation as OCR again, instead
we can do some magic tricks (copy them from one location to another)
on already extracted txt and hocr files.

OcrMigrate class takes care of this sort of txt/hocr files moves.
"""


def get_pagecount(doc_ep):
    """
    Returns total number of pages for this endpoint.
    Total number of pages = number of page_xy.txt files
    in pages_dirname folder.
    """
    pages_dir = doc_ep.pages_dirname
    onlyfiles = [
        f for f in listdir(pages_dir) if isfile(join(pages_dir, f))
    ]
    return len(onlyfiles)


def get_assigns_after_delete(total_pages, deleted_pages):
    """
    given total pages and a list of deleted pages - returns
    a list of assignations of pages:
        [new_version_page_num, old_version_page_num]
    Example 1:
    total_pages: 6
    deleted_pages: [1, 2]
    returns: [
        [(1, 3),  (2, 4), (3, 5), (4, 6)]
        # page #1 gets info from prev page #3
        # page #2 ... #4
        ...
        # page #4 ... #6
    ]

    Example 2:
    total pages: 5
    deleted_pages [1, 5]
    returns: [
        [(1, 2), (2, 3), (3, 4)
    ]

    Example 3:
    total pages: 5
    deleted_pages [2, 3]
    returns: [
        [(1, 1), (2, 4), (3, 5)
        # page #1 stays unaffected
        # page #2 gets the info from page number 4
        # page #3 gets info from page #5
    ]
    """
    if total_pages < len(deleted_pages):
        err_msg = f"total_pages < deleted_pages"
        raise ValueError(err_msg)

    # only numbers of pages which were not deleted
    pages = [
        page for page in list(range(1, total_pages + 1))
        if page not in deleted_pages
    ]

    page_numbers = range(1, len(pages) + 1)

    return list(zip(page_numbers, pages))


def copy_page(src_page_ep, dst_page_ep):
    err_msg = "copy_page accepts only PageEp instances"

    for inst in [src_page_ep, dst_page_ep]:
        if not isinstance(inst, PageEp):
            raise ValueError(err_msg)

    # copy .txt file
    if src_page_ep.txt_exists():
        shutil.copy(
            src_page_ep.txt_url(),
            dst_page_ep.txt_url()
        )
    # hocr
    if src_page_ep.hocr_exists():
        shutil.copy(
            src_page_ep.hocr_url(),
            dst_page_ep.hocr_url()
        )

    if src_page_ep.img_exists():
        shutil.copy(
            src_page_ep.img_url(),
            dst_page_ep.img_url()
        )


class OcrMigrate:
    """
    Insead of running again OCR operation on changed document AGAIN
    (e.g. after pages 2 and 3 were deleted)
    text files which are result of first (and only!) OCR are moved
    (moved = migrated) inside new version's folder.
    Basically migrate/move files instead of rerunning OCR operation.

    For each affected page (page_x), following files will need to be migrated:
        * <version>/pages/page_x.txt
        * <version>/pages/page_x/50/*.hocr
        * <version>/pages/page_x/75/*.hocr
        * <version>/pages/page_x/100/*.hocr
        * <version>/pages/page_x/125/*.hocr
        from <old_version> to <new_version>

    Which pages are affected depends on the operation.
    """

    def __init__(self, src_ep, dst_ep):
        # Both endpoints shoud be instance of DocumentEp

        for inst in [src_ep, dst_ep]:
            if not isinstance(inst, DocumentEp):
                raise ValueError(
                    "OcrMigrate args must be DocumentEp instances"
                )

        self.src_ep = src_ep
        self.dst_ep = dst_ep

    def migrate_delete(self, deleted_pages):
        page_count = get_pagecount(self.src_ep)

        if len(deleted_pages > page_count):
            raise ValueError(
                f"deleted_pages({deleted_pages}) > page_count({page_count})"
            )
        assigns = get_assigns_after_delete(
            total_pages=page_count,
            deleted_pages=deleted_pages
        )
        for a in assigns:
            for step in Steps():
                src_page_ep = PageEp(
                    document_ep=self.src_ep,
                    page_num=a[0],
                    step=step,
                    page_count=page_count
                )
                dst_page_ep = PageEp(
                    document_ep=self.dst_ep,
                    page_num=a[1],
                    step=step,
                    page_count=page_count - deleted_pages
                )
                copy_page(
                    src_page_ep=src_page_ep,
                    dst_page_ep=dst_page_ep
                )
