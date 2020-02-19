import os
import logging

from pmworker.runcmd import run
from pmworker.pdfinfo import get_pagecount

logger = logging.getLogger(__name__)

#
#  Utilities around pdftk command line tool
#
#  https://www.pdflabs.com/docs/pdftk-man-page/
#


def cat_ranges_for_delete(page_count, page_numbers):
    """
    Returns a list of integers. Each number in the list
    is the number of page which will 'stay' in document.
    In other words, it returns a list with deleted pages.

    Examples:


    If document has 22 pages (page_count=22) and page number 21 is to be
    deleted (i.e page_numbers = [21]) will return

        [1, 2, 3, 4, ..., 19, 20, 22]

    If page number 1 is to be deleted:

        [2, 3, 4, ..., 22] list will be returned.

    If page number is 22 is to be deleted:

        [1, 2, 3,..., 21] will be returned.

    With  page_numbers=[1, 7, 10] and page_count=22 result
    will be:

        (2, 3, 4, 5, 6, 8, 9, 11, 12 , 13, ..., 22)


    page_numbers is a list of page numbers (starting with 1).
    """
    results = []

    for check in page_numbers:
        if not isinstance(check, int):
            err_msg = "page_numbers must be a list of strings"
            raise ValueError(err_msg)

    for number in range(1, page_count + 1):
        if number not in page_numbers:
            results.append(number)

    return results


def make_sure_path_exists(filepath):
    dirname = os.path.dirname(filepath)
    os.makedirs(
        dirname,
        exist_ok=True
    )


def delete_pages(doc_ep, page_numbers):
    ep_url = doc_ep.url()
    page_count = get_pagecount(ep_url)

    cat_ranges = cat_ranges_for_delete(
        page_count,
        page_numbers
    )

    doc_ep.inc_version()

    cmd = [
        "pdftk",
        ep_url,
        "cat"
    ]
    for page in cat_ranges:
        cmd.append(
            str(page)
        )

    cmd.append("output")
    make_sure_path_exists(doc_ep.url())
    cmd.append(doc_ep.url())

    run(cmd)

    return doc_ep.version
