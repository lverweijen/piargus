import io
import os
from pathlib import Path


class GraphRecode:
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
            if line.strip().upper() == cls.HEADER:
                continue
            else:
                codes.append(line)

        return cls(codes)

    def to_grc(self, file=None):
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self.to_grc(file)
            return file.getvalue()
        elif not hasattr(file, 'write'):
            self.filepath = Path(file)
            with open(file, 'w', newline='\n') as writer:
                return self.to_grc(writer)

        file.write(f"{self.HEADER}\n")
        for code in self.codes:
            file.write(code)
