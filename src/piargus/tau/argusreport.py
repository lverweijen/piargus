import textwrap
from collections.abc import Sequence

SEP_MARKER = '--------------------'
END_MARKER = "End of TauArgus run"


class ArgusReport:
    """Report of argus run."""
    def __init__(self, returncode: int, batch_file=None, logbook_file=None, workdir=None):
        self.returncode = returncode
        self.batch_file = str(batch_file)
        self.logbook_file = str(logbook_file)
        self.workdir = str(workdir)
        self.batch = None
        self.logbook = None

    def read_batch(self) -> Sequence[str]:
        """Read batchfile and return lines."""
        if self.batch_file and self.batch is None:
            self.batch = []
            with open(self.batch_file) as reader:
                self.batch = reader.readlines()

        return self.batch

    def read_log(self) -> Sequence[str]:
        """Read logfile and return lines."""
        if self.logbook_file and self.logbook is None:
            self.logbook = []
            try:
                is_end = False
                with open(self.logbook_file) as reader:
                    for line in reader:
                        self.logbook.append(line)
                        if SEP_MARKER in line or is_end:
                            self.logbook.clear()
                            is_end = False
                        elif END_MARKER in line:
                            is_end = True
            except FileNotFoundError:
                self.logbook = None

        return self.logbook

    def check(self):
        """Raise an exception if the run failed."""
        if self.is_failed:
            raise TauArgusException(self)

    @property
    def status(self) -> str:
        """Return whether the run succeeded or failed as text."""
        if self.is_succesful:
            return "success"
        else:
            return "failed"

    @property
    def is_succesful(self) -> bool:
        """Return whether the run succeeded."""
        return self.returncode == 0

    @property
    def is_failed(self) -> bool:
        """Return whether the run failed."""
        return self.returncode != 0

    def __str__(self):
        out = [f"<{self.__class__.__name__}>",
               f"status: {self.status} <{self.returncode}>"]

        if self.batch_file:
            out.append("batch_file: " + self.batch_file)

        if self.workdir:
            out.append("workdir: " + self.workdir)

        if self.logbook_file:
            out.append("logbook_file: " + self.logbook_file)
            log = self.read_log()
            if log is not None:
                log = [textwrap.indent(line, '\t') for line in self.read_log()]
                out.append("logbook:\n" + "".join(log))

        return "\n".join(out)


class TauArgusException(Exception):
    def __init__(self, result):
        self.result = result

    def __str__(self):
        return str(self.result)
