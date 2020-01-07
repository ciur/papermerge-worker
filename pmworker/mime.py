import logging
from pmworker import wrapper


logger = logging.getLogger(__name__)


class Mime(wrapper.Wrapper):
    def __init__(self, filepath):
        super().__init__(exec_name="file")
        self.filepath = filepath

    def get_cmd(self):
        cmd = super().get_cmd()

        cmd.extend(['--mime-type'])
        cmd.extend(['-b'])
        cmd.extend([self.filepath])

        return cmd

    def is_pdf(self):
        return self.guess() == 'application/pdf'

    def is_image(self):
        """
        Returns true if MIME type is one of following:
            * image/png
            * image/jpg
            * image/tiff
        """

        return 'image' in self.guess()

    def guess(self):
        cmd = self.get_cmd()
        complete = self.run(cmd)

        return complete.stdout.strip()
