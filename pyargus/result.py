import textwrap


SEP_MARKER = '--------------------'
END_MARKER = "End of TauArgus run"


class TauArgusResult:
    def __init__(self, returncode=None, logbook_file=None):
        self.returncode = returncode
        self.logbook_file = logbook_file
        self.logbook = None

    def read_log(self):
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
                        else:
                            if END_MARKER in line:
                                is_end = True
            except FileNotFoundError:
                self.logbook = None

        return self.logbook

    def check(self):
        if self.is_failed:
            raise TauArgusException(self)

    @property
    def status(self) -> str:
        if self.is_succesful:
            return "success"
        else:
            return "failed"

    @property
    def is_succesful(self) -> bool:
        return self.returncode == 0

    @property
    def is_failed(self) -> bool:
        return self.returncode != 0

    def __str__(self):
        out = [f"# {self.__class__.__name__} #",
               f"status: {self.status} <{self.returncode}>"]

        if self.logbook_file:
            out.append("logbook_file: " + str(self.logbook_file))

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
