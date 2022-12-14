import pandas as pd


class CodeList:
    """Describe a codelist for use with TauArgus"""
    def __init__(self, lst):
        self._codes = pd.Series(lst)
        self._codes.index = self._codes.index.astype(str)

    def codes(self):
        for code in self._codes.index:
            yield code

    def __getitem__(self, key):
        return self._codes[key]

    def to_cdl(self, file=None, length=0):
        codes = self._codes.copy()
        codes.index = codes.index.str.rjust(length)
        return codes.to_csv(file, header=None)
