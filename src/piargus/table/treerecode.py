import io
import os
from pathlib import Path


class TreeRecode:
    """
    Hierarchical codes can be recoded to make the output less detailed.
    """
    HEADER = "<TREERECODE>"

    def __init__(self, codes):
        self.codes = list(str(code) for code in codes)
        self.filepath = None

    @classmethod
    def from_grc(cls, file):
        if isinstance(file, (str, Path)):
            with open(file) as reader:
                graph_recode = cls.from_grc(reader)
                graph_recode.filepath = Path(file)
                return graph_recode

        codes = list()
        for line in file:
            if line.strip().upper() != cls.HEADER:
                codes.append(line)

        return cls(codes)

    def to_grc(self, file=None, length=0):
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
