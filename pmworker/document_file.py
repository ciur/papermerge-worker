import os

class DocumentFile:

    def __init__(self, fmtdirstr, file_name, media_root):
        self.fmtdirstr = fmtdirstr
        self.file_name = file_name
        self.media_root = media_root

    @property
    def dir_path(self):
        return os.path.join(
            self.media_root,
            self.fmtdirstr
        )

    def __str__(self):
        return self.abspath

    def __repr__(self):
        return self.abspath

    @property
    def rootname(self):
        root, _ = os.path.splitext(
            os.path.basename(self.file_name)
        )

        return root

    @property
    def is_image(self):
        """
        """
        ext = os.path.splitext(self.abspath)[1]
        if ext.lower() in ('.png', '.jpeg', '.jpg'):
            return True

        return False

    @property
    def abspath(self):
        return os.path.join(
            self.dir_path,
            self.file_name
        )

    @property
    def exists(self):
        return os.path.exists(self.abspath)
