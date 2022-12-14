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

    def __init__(self, lst):
        self._codes = pd.Series(lst)
        self._codes.index = self._codes.index.astype(str)
        self.filepath = None

    def __str__(self):
        return self.to_cdl()

    def codes(self):
        for code in self._codes.index:
            yield code

    def __getitem__(self, key):
        return self._codes[key]

    def to_cdl(self, file=None, length=0):
        codes = self._codes.copy()
        codes.index = codes.index.str.rjust(length)
        result = codes.to_csv(file, header=False)

        if isinstance(file, (str, Path)):
            self.filepath = Path(file)

        return result
