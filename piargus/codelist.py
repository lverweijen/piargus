from pathlib import Path

import pandas as pd


class CodeList:
    """Describe a codelist for use with TauArgus"""

    @classmethod
    def from_cdl(cls, file):
        df = pd.read_csv(file, index_col=0, header=None)
        codelist = CodeList(df.iloc[:, 0])
        if isinstance(file, (str, Path)):
            codelist.filepath = Path(file)

        return codelist

    def __init__(self, codes):
        if hasattr(codes, 'keys'):
            self._codes = pd.Series(codes)
        else:
            self._codes = pd.Series(codes, index=codes)

        self._codes.index = self._codes.index.astype(str)
        self.filepath = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __str__(self):
        return self.to_cdl()

    def __getitem__(self, key):
        return self._codes[key]

    def __setitem__(self, key, value):
        self._codes[key] = value

    def __iter__(self):
        return iter(self.keys())

    def __eq__(self, other):
        if hasattr(other, 'to_dict'):
            other = other.to_dict()

        return self.to_dict() == other

    def keys(self):
        return self._codes.keys()

    def iter_codes(self):
        for code in self._codes.index:
            yield code

    def to_cdl(self, file=None, length=0):
        codes = self._codes.copy()
        codes.index = codes.index.str.rjust(length)
        result = codes.to_csv(file, header=False)

        if isinstance(file, (str, Path)):
            self.filepath = Path(file)

        return result

    def to_dict(self):
        return self._codes.to_dict()
