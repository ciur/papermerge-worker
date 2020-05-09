import os
import logging

from pmworker.runcmd import run

logger = logging.getLogger(__name__)


def extract_img(page_url):
    local_abspath = page_url.document_path.url()
    ppmroot_dirname = os.path.dirname(page_url.ppmroot)
    page_num = page_url.page_num
    width = page_url.step.width

    if not os.path.exists(ppmroot_dirname):
        logger.debug(f"{ppmroot_dirname} does not exists. Creating.")
        os.makedirs(
            ppmroot_dirname, exist_ok=True
        )
    else:
        logger.debug(f"{ppmroot_dirname} already exists.")

    cmd = (
        "pdftoppm",
        "-jpeg",
        "-f",
        str(page_num),
        "-l",  # generate only one page
        str(page_num),
        "-scale-to-x",
        str(width),
        "-scale-to-y",
        "-1",  # it will adjust height according to img ratio
        local_abspath,
        # output directory path
        page_url.ppmroot,
    )

    run(cmd)


def extract_hocr(page_url, lang):
    page_abspath = page_url.img_url()
    hocr_root, hocr_ext = os.path.splitext(
        page_url.hocr_url()
    )
    cmd = (
        "tesseract",
        "-l",
        lang,
        page_abspath,
        hocr_root,
        "hocr"
    )
    run(cmd)


def extract_txt(page_url, lang):
    page_abspath = page_url.img_url()
    txt_root, txt_ext = os.path.splitext(page_url.txt_url())
    cmd = (
        "tesseract",
        "-l",
        lang,
        page_abspath,
        txt_root
    )
    run(cmd)


#def text_from_pdf(filepath, lang, dry_run=False):
#
#    # suffix .tiff in file name is required by conver utility, otherwise
#    # it won't convert to tiff format!
#    tiff = tempfile.NamedTemporaryFile(suffix=".tiff")
#    conv = convert.Convert(dry_run=dry_run)
#    conv(filepath=filepath, fout=tiff)
#    try:
#        tsact = tesseract.Tesseract()
#        text = tsact(filepath=tiff.name, lang=lang)
#    except subprocess.CalledProcessError as e:
#        print(e)
#        print(e.stderr)
#        return
#
#    return text
#
#
#def text_from_image(filepath, lang, dry_run=False):
#
#    tsact = tesseract.Tesseract(dry_run=dry_run)
#    text = tsact(filepath=filepath, lang=lang)
#
#    return text
#
