

class OcrMigrate:
    """
    Insead of running again OCR operation on changed document AGAIN
    (e.g. after pages 2 and 3 were deleted)
    text files which are result of first (and only!) OCR are moved
    (moved = migrated) inside new version's folder.

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
        self.src_ep = src_ep
        self.dst_ep = dst_ep

    def migrate_delete(self, deleted_pages):
        pass
