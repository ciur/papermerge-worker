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


def cat_ranges_for_reorder(page_count, new_order):
    """
    Returns a list of integers. Each number in the list
    is correctly positioned (newly ordered) page.

    Examples:

    If in document with 4 pages first and second pages were
    swapped, then returned list will be:

        [2, 1, 3, 4]

    If first page was swapped with last one (also 4 paegs document)
    result list will look like:

        [4, 2, 3, 1]
    """
    results = []
    # key = page_num
    # value = page_order
    page_map = {}

    for item in new_order:
        k = int(item['page_num'])
        v = int(item['page_order'])
        page_map[k] = v

    for number in range(1, page_count + 1):
        results.append(
            page_map[number]
        )

    return results


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
    logger.debug(f"make_sure_path_exists {filepath}")
    dirname = os.path.dirname(filepath)
    os.makedirs(
        dirname,
        exist_ok=True
    )


def split_ranges(total, after=False, before=False):
    """
    Given a range 1, 2, ..., total (page numbers of a doc).
    Split it in two lists.
    Example:
    Input: total = 9, after=1, before=False
    Output: list1 = [1]; list2 = [2, 3, 4, ..., 9].

    Input: total = 9; after=False, before=1
    Output: list1 = [], list2 = [1, 2, 3, 4, ..., 9]

    Input: total = 5; after=4; before=False
    Output: list1 = [1, 2, 3, 4] list2 = [5]

    Input: total = 5; after=False; before=False;
    Output: list1 = [1, 2, 3, 4, 5], list2 = []
    (it means, by default, all pages are inserted at the end of the doc)
    """
    if after and not before:
        if not isinstance(after, int):
            raise ValueError(
                "argument 'after' is supposed to be an int"
            )
        list1 = list(range(1, after + 1))
        list2 = list(range(after + 1, total + 1))
        return list1, list2

    if not after and before:
        if not isinstance(before, int):
            raise ValueError(
                "argument 'before' is supposed to be an int"
            )
        list1 = list(range(1, before))
        list2 = list(range(before, total + 1))
        return list1, list2

    list1 = list(range(1, total + 1))
    list2 = []

    return list1, list2


def paste_pages_into_existing_doc(
    dest_doc_ep,
    src_doc_ep_list,
    after_page_number=False,
    before_page_number=False
):
    page_count = get_pagecount(dest_doc_ep.url())
    list1, list2 = split_ranges(
        total=page_count,
        after=after_page_number,
        before=before_page_number
    )
    # notice missing A
    # Letter A is assignent to current folder and
    # pages from list1 and list2
    letters = "BCDEFGHIJKLMNOPQRSTUVWXYZ"
    letters_2_doc_map = []
    letters_pages = []
    letters_pages_before = []
    letters_pages_after = []

    letters_2_doc_map.append(
        f"A={dest_doc_ep.url()}"
    )

    for idx in range(0, len(src_doc_ep_list)):
        letter = letters[idx]
        doc_ep = src_doc_ep_list[idx]['doc_ep']
        pages = src_doc_ep_list[idx]['page_nums']

        letters_2_doc_map.append(
            f"{letter}={doc_ep.url()}"
        )
        for p in pages:
            letters_pages.append(
                f"{letter}{p}"
            )

    dest_doc_ep.inc_version()

    for p in list1:
        letters_pages_before.append(
            f"A{p}"
        )

    for p in list2:
        letters_pages_after.append(
            f"A{p}"
        )

    cmd = [
        "pdftk",
    ]
    # add A=doc1_path, B=doc2_path
    cmd.extend(letters_2_doc_map)

    cmd.append("cat")

    # existing doc pages (may be empty)
    cmd.extend(letters_pages_before)
    # newly inserted pages
    cmd.extend(letters_pages)
    # existing doc pages (may be empty)
    cmd.extend(letters_pages_after)

    cmd.append("output")

    make_sure_path_exists(dest_doc_ep.url())

    cmd.append(dest_doc_ep.url())

    run(cmd)

    return dest_doc_ep.version


def paste_pages(
    dest_doc_ep,
    src_doc_ep_list,
    dest_doc_is_new=True,
    after_page_number=False,
    before_page_number=False
):
    """
    dest_doc_ep = endpoint of the doc where newly created
        file will be placed.
    src_doc_ep_list is a list of following format:
        [
            {
                'doc_ep': doc_ep,
                'page_nums': [page_num_1, page_num_2, page_num_3]
            },
            {
                'doc_ep': doc_ep,
                'page_nums': [page_num_1, page_num_2, page_num_3]
            },
            ...
        ]
    src_doc_ep_list is a list of documents where pages
    (with numbers page_num_1...) will be paste from.

    dest_doc_is_new = True well.. destination document was just created,
    we are pasting here cutted pages into some folder as new document.

    In this case 'after' and 'before' arguments are ignored

    dest_doc_is_new = False, pasting pages into exiting document.
    If before_page_number > 0 - paste pages before page number
        'before_page_number'
    If after_page_number > 0 - paste pages after page number
        'after_page_number'

    before_page_number argument has priority over after_page_number.

    If both before_page_number and after_page_number are < 0 - just paste
    pages at the end of the document.
    """

    if not dest_doc_is_new:
        return paste_pages_into_existing_doc(
            dest_doc_ep=dest_doc_ep,
            src_doc_ep_list=src_doc_ep_list,
            after_page_number=after_page_number,
            before_page_number=before_page_number
        )
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letters_2_doc_map = []
    letters_pages = []

    for idx in range(0, len(src_doc_ep_list)):
        letter = letters[idx]
        doc_ep = src_doc_ep_list[idx]['doc_ep']
        pages = src_doc_ep_list[idx]['page_nums']

        letters_2_doc_map.append(
            f"{letter}={doc_ep.url()}"
        )
        for p in pages:
            letters_pages.append(
                f"{letter}{p}"
            )

    dest_doc_ep.inc_version()

    cmd = [
        "pdftk",
    ]
    # add A=doc1_path, B=doc2_path
    cmd.extend(letters_2_doc_map)

    cmd.append("cat")

    cmd.extend(letters_pages)

    cmd.append("output")

    make_sure_path_exists(dest_doc_ep.url())

    cmd.append(dest_doc_ep.url())

    run(cmd)

    return dest_doc_ep.version


def reorder_pages(doc_ep, new_order):
    """
    new_order is a list of following format:

        [
            {'page_num': 2, page_order: 1},
            {'page_num': 1, page_order: 2},
            {'page_num': 3, page_order: 3},
            {'page_num': 4, page_order: 4},
        ]
    Example above means that in current document of 4 pages,
    first page was swapped with second one.
    page_num    = older page order
    page_order  = current page order
    So in human language, each hash is read:
        <page_num> now should be <page_order>
    """
    ep_url = doc_ep.url()
    page_count = get_pagecount(ep_url)

    cat_ranges = cat_ranges_for_reorder(
        page_count=page_count,
        new_order=new_order
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
