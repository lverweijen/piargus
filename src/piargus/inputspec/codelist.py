import os
from collections.abc import Mapping, MutableMapping
from pathlib import Path

import pandas as pd


class CodeList(MutableMapping):
    """Describe a codelist for use with TauArgus.

    It can be used to attach labels to code lists.
    It only has effect when running TauArgus interactively.
    """

    @classmethod
    def from_cdl(cls, file):
        """Read cdl file."""
        if isinstance(file, os.PathLike):
            return cls(file)

    def __init__(self, codes: Mapping[str, str] | os.PathLike):
        """Create a codelist."""
        match codes:
            case CodeList():
                self._codes = codes._codes
                self.file = codes.filepath
            case Mapping():
                self._codes = pd.Series(codes)
                self.filepath = None
            case os.PathLike():
                codes = Path(codes)
                if codes.suffix == ".cdl":
                    df = pd.read_csv(codes, index_col=0, header=None)
                    self._codes = CodeList(df.iloc[:, 0])
                    self.filepath = Path(codes)
                else:
                    raise ValueError("Not a .cdl file")
            case _:
                raise TypeError("Codelist should be a mapping or .cdl file")

        self._codes.index = self._codes.index.astype(str)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __str__(self):
        return self.to_cdl()

    def __getitem__(self, key):
        """Get label of a code."""
        return self._codes[key]

    def __setitem__(self, key, value):
        """Set label of a code."""
        self._codes[key] = value

    def __delitem__(self, key, /):
        del self._codes[key]

    def __len__(self):
        return len(self._codes)

    def __iter__(self):
        return iter(self.keys())

    def __eq__(self, other):
        if hasattr(other, 'to_dict'):
            other = other.to_dict()

        return self.to_dict() == other

    @property
    def code_length(self) -> int:
        return max(map(len, self.keys()))

    def keys(self):
        return self._codes.keys()

    def to_cdl(self, file=None, length=0):
        """Store codelist in cdl file."""
        codes = self._codes.copy()
        codes.index = codes.index.str.rjust(length)
        result = codes.to_csv(file, header=False)

        if isinstance(file, (str, Path)):
            self.filepath = Path(file)

        return result

    def to_dict(self):
        return self._codes.to_dict()
