import os
import logging

from pmworker.runcmd import run

logger = logging.getLogger(__name__)


def cat_ranges_for_delete(page_count, page_numbers):
    """
    Returns a string with range format used by
    pdftk utility to delete pages.

    Example 1:

    If document has 22 pages and page number 21 is to be
    deleted (i.e page_numbers = [21]) will return

        "1-20 22-end" string

    If page number 1 is to be deleted:

        "2-end" string will be returned.
    """
    pass


def delete_pages(doc_ep, page_numbers):
    page_count = get_pagecount(doc_ep.url())

    cat_ranges_for_delete(page_count, page_numbers)

