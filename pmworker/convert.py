import logging
from pmworker import wrapper

logger = logging.getLogger(__name__)


class Convert(wrapper.Wrapper):
    def __init__(
        self,
        density='300',
        background='white',
        depth='8',
        alpha=False,
        strip=True,
        dry_run=False,
    ):
        super().__init__(exec_name="convert", dry_run=dry_run)
        self.density = density
        self.depth = depth
        self.background = background
        self.alpha = alpha
        self.strip = strip

    def get_cmd_conv_tiff(self, filepath, fout):
        """
        returns an array suitable as first agument to
        subprocess.run() (first argument is name of utility followed by
        utility arguments with their values)

        filepath - path to a local file
        fin - an instance of tempfile.NamedTemporaryFile
        """

        cmd = self.get_cmd()

        if self.density:
            cmd.extend(['-density', self.density])

        if filepath:
            cmd.extend([filepath])

        if self.depth:
            cmd.extend(['-depth', self.depth])

        if self.strip:
            cmd.extend(['-strip'])

        if self.background:
            cmd.extend(['-background', self.background])

        if self.alpha:
            cmd.extend(['-alpha', 'on'])
        else:
            cmd.extend(['-alpha', 'off'])

        cmd.extend([fout.name])

        return cmd

    def __call__(self, filepath=None, fout=None):
        """
        fout is instances of tempfile.NamedTemporaryFile
        """
        if not filepath:
            return self.call_no_args()

        cmd = self.get_cmd_conv_tiff(filepath=filepath, fout=fout)

        logger.debug("Executing command {}".format(
            ' '.join(cmd)
        ))
        result = self.run(cmd)

        if result.returncode:
            raise Exception(
                "Error occured during convert: %s " % result.stderr
            )
