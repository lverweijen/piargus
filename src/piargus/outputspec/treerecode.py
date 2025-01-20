import io
import os
from collections.abc import Sequence
from pathlib import Path


class TreeRecode:
    """
    Hierarchical codes can be recoded to make the output less detailed.

    Maybe this can later be implemented in python directly.
    """
    HEADER = "<TREERECODE>"

    def __init__(self, codes: "TreeRecode" | os.PathLike | Sequence[str]):
        if isinstance(codes, TreeRecode):
            self.codes = codes.codes
            self.filepath = codes.filepath
        elif isinstance(codes, os.PathLike):
            self.filepath = Path(codes)
            with open(codes) as file:
                codes = list()
                for line in file:
                    if line.strip().upper() != self.HEADER:
                        codes.append(line)
                self.codes = codes
        else:
            self.codes = list(str(code) for code in codes)
            self.filepath = None

    @classmethod
    def from_grc(cls, file):
        """Load from grc file."""
        if isinstance(file, os.PathLike):
            return TreeRecode(file)
        else:
            raise TypeError("A file is expected")

    def to_grc(self, file=None, length=0):
        """Write to grc file."""
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self.to_grc(file, length)
            return file.getvalue()

        elif not hasattr(file, 'write'):
            self.filepath = Path(file)
            with open(file, 'w', newline='\n') as writer:
                self.to_grc(writer, length)

        else:
            file.write(f"{self.HEADER}\n")
            for code in self.codes:
                file.write(code.rjust(length) + "\n")
