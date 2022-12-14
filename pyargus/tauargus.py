import re
import subprocess
import tempfile
from pathlib import Path

from .batchwriter import BatchWriter
from .result import TauArgusResult


class TauArgus:
    def __init__(self, program='TauArgus'):
        self.program = program

    def run(self, batch_or_job, check=True, *args, **kwargs) -> TauArgusResult:
        """Run either a batch file or a job."""
        if hasattr(batch_or_job, 'setup'):
            returncode, logbook = self._run_job(batch_or_job, *args, **kwargs)
        else:
            returncode, logbook = self._run_batch(batch_or_job, *args, **kwargs)

        result = TauArgusResult(returncode, logbook)
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
        return subprocess_result.returncode, logbook

    def _run_job(self, job, *args, **kwargs):
        job.setup()
        returncode, logbook = self._run_batch(job.batch_filepath, *args, **kwargs)
        if job.logbook:
            logbook = job.logbook_filepath
        return returncode, logbook

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
