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
    Returns a string with range format used by
    pdftk utility to delete pages.

    If document has 22 pages and page number 21 is to be
    deleted (i.e page_numbers = [21]) will return

        "1-20 22-end" string

    If page number 1 is to be deleted:

        "2-22" string will be returned.

    If page number is 22 is to be deleted:

        "1-21" will be returned.

    With page_count=22 and page_numbers=[1, 7, 10], result
    will be:

        2-6 8-9 11-22


    page_numbers is a list of page numbers (starting with 1).
    """
    pass


def delete_pages(doc_ep, page_numbers):
    ep_url = doc_ep.url()
    page_count = get_pagecount(ep_url)

    cat_ranges = cat_ranges_for_delete(
        page_count,
        page_numbers
    )

    doc_ep.inc_version()

    cmd = (
        "pdftk",
        ep_url,
        "cat",
        cat_ranges,
        "output",
        # because inc_version() was called
        # next version of url will be returned
        doc_ep.url()
    )
    run(cmd)
