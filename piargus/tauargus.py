import re
import subprocess
import tempfile
from pathlib import Path

from .batchwriter import BatchWriter
from .argusreport import ArgusReport


class TauArgus:
    DEFAULT_LOGBOOK = Path(tempfile.gettempdir()) / 'TauLogbook.txt'

    def __init__(self, program='TauArgus'):
        self.program = program

    def run(self, batch_or_job=None, check=True, *args, **kwargs) -> ArgusReport:
        """Run either a batch file or a job."""
        if batch_or_job is None:
            returncode, logbook = self._run_interactively()
        elif hasattr(batch_or_job, 'batch_filepath'):
            returncode, logbook = self._run_job(batch_or_job, *args, **kwargs)
        else:
            returncode, logbook = self._run_batch(batch_or_job, *args, **kwargs)

        result = ArgusReport(returncode, logbook)
        if check:
            result.check()

        return result

    def _run_batch(self, batch_file, logbook=None, tmpdir=None):
        cmd = [self.program, str(Path(batch_file).absolute())]

        if logbook is not None:
            cmd.append(str(Path(logbook).absolute()))
        if tmpdir is not None:
            cmd.append(str(Path(tmpdir).absolute()))

        subprocess_result = subprocess.run(cmd)
        if logbook is None:
            logbook = self.DEFAULT_LOGBOOK
        return subprocess_result.returncode, logbook

    def _run_job(self, job, *args, **kwargs):
        returncode, logbook = self._run_batch(job.batch_filepath, *args, **kwargs)
        if hasattr(job, 'logbook_filepath'):
            logbook = job.logbook_filepath
        return returncode, logbook

    def _run_interactively(self):
        subprocess_result = subprocess.run([self.program])
        return subprocess_result.returncode, self.DEFAULT_LOGBOOK

    def version_info(self) -> dict:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as versioninfo:
            pass

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as batch_file:
            writer = BatchWriter(batch_file)
            writer.version_info(versioninfo.name)

        result = self.run(batch_file.name)

        try:
            result.check()
            with open(versioninfo.name) as read_versioninfo:
                version_str = read_versioninfo.read()

            match = re.match(r"(?P<name>\S+) "
                             r"version: (?P<version>[0-9.]+)\; "
                             r"build: (?P<build>[0-9.]+)", version_str)
            return match.groupdict()

        finally:
            Path(batch_file.name).unlink()
            Path(versioninfo.name).unlink()
