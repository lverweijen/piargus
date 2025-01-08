import re
import subprocess
import tempfile
from pathlib import Path
from typing import Union, Sequence

from .batchwriter import BatchWriter
from .argusreport import ArgusReport


class TauArgus:
    """Representation of the tau argus program that is run in the background."""
    DEFAULT_LOGBOOK = Path(tempfile.gettempdir()) / 'TauLogbook.txt'

    def __init__(self, program: Union[str, Path] = 'TauArgus'):
        self.program = str(program)

    def run(self, batch_or_job=None, check: bool = True, *args, **kwargs) -> ArgusReport:
        """Run either a batch file or a job."""
        if batch_or_job is None:
            result = self._run_interactively()
        elif isinstance(batch_or_job, str):
            result = self._run_batch(batch_or_job, *args, **kwargs)
        elif hasattr(batch_or_job, 'batch_filepath'):
            result = self._run_job(batch_or_job, *args, **kwargs)
        elif hasattr(batch_or_job, '__iter__'):
            result = self._run_parallel(batch_or_job, *args, **kwargs)
        else:
            raise TypeError

        if check:
            if hasattr(result, '__iter__'):
                for res in result:
                    res.check()
            else:
                result.check()

        return result

    def _run_interactively(self):
        cmd = self.program
        subprocess_result = subprocess.run(cmd)
        return ArgusReport(subprocess_result.returncode, logbook_file=self.DEFAULT_LOGBOOK)

    def _run_job(self, job):
        return self._run_batch(job.batch_filepath, job.logbook_filepath, job.workdir)

    def _run_batch(self, batch_file: Union[str, Path], logbook_file=None, workdir=None):
        """Run a batchfile str or Path"""
        cmd = [self.program, str(Path(batch_file).absolute())]

        if logbook_file is not None:
            cmd.append(str(Path(logbook_file).absolute()))
        if workdir is not None:
            cmd.append(str(Path(workdir).absolute()))

        subprocess_result = subprocess.run(cmd)
        if logbook_file is None:
            logbook_file = self.DEFAULT_LOGBOOK
        return ArgusReport(
            subprocess_result.returncode,
            batch_file=batch_file,
            logbook_file=logbook_file,
            workdir=workdir,
        )

    def _run_parallel(self, jobs: Sequence, timeout=None):
        """Run multiple jobs at the same time (experimental)"""
        jobs = list(jobs)
        processes = []

        try:
            for job in jobs:
                batch_file = str(job.batch_filepath.absolute())
                log_file = str(job.logbook_filepath.absolute())
                workdir = str(job.workdir.absolute())
                cmd = [self.program, batch_file, log_file, workdir]
                process = subprocess.Popen(cmd)
                processes.append((cmd, process))

            results = []
            for cmd, process in processes:
                result = ArgusReport(
                    process.wait(timeout),
                    batch_file=Path(process.args[1]),
                    logbook_file=Path(process.args[2]),
                    workdir=Path(process.args[3]),
                )
                results.append(result)
                if timeout is not None:
                    timeout = 1
        finally:
            for _, process in processes:
                if process.poll() is None:
                    process.kill()

        return results

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
