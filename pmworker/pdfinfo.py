import os
import re
import subprocess
import logging

"""
Uses command line pdfinfo utility (from poppler pakage) for various
small operations (e.g. get pdf page count).
"""

logger = logging.getLogger(__name__)


def get_pagecount(filepath):
    """
    Returns the number of pages in a PDF document as integer.

    filepath - is filesystem path to a PDF document
    """
    if not os.path.isfile(filepath):
        raise ValueError("Filepath %s is not a file" % filepath)

    if os.path.isdir(filepath):
        raise ValueError("Filepath %s is a directory!" % filepath)

    base, ext = os.path.splitext(filepath)

    # pure images (png, jpeg) have only one page :)
    if ext and ext.lower() in ('.jpeg', '.png', '.jpg'):
        # whatever png/jpg image is there - it is
        # considered by default one page document.
        return 1

    if ext and ext.lower() not in ('.pdf',):
        raise ValueError(
            "Only jpeg, png and pdf are handlerd by this"
            " method"
        )

    # pdfinfo "${PDFFILE}" | grep Pages

    cmd = ["/usr/bin/pdfinfo", filepath]
    compl = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if compl.returncode:

        logger.error(
            "get_pagecount: cmd=%s args=%s stdout=%s stderr=%s code=%s",
            cmd,
            compl.args,
            compl.stdout,
            compl.stderr,
            compl.returncode,
            stack_info=True
        )

        raise Exception("Error occured while getting document page count.")

    lines = compl.stdout.decode('utf-8').split('\n')
    # look up for the line containing "Pages: 11"
    for line in lines:
        x = re.match("Pages:\W+(\d+)$", line.strip())
        if x:
            return int(x.group(1))

    return 0
