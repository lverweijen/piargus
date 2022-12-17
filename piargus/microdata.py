from pathlib import Path

from pandas.core.dtypes.common import is_bool_dtype, is_numeric_dtype, is_float_dtype

from .metadata import MetaData
from .inputdata import InputData


class MicroData(InputData):
    """
    A MicroData instance contains the data at an individual level.

    From such microdata, tabular aggregates can be constructed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_metadata(self) -> MetaData:
        metadata = super().generate_metadata()
        for col in self.dataset.columns:
            metacol = metadata[col]
            col_dtype = self.dataset[col].dtype
            metacol['NUMERIC'] = is_numeric_dtype(col_dtype)
            metacol['RECODABLE'] = True
            if is_float_dtype(col_dtype):
                metacol['DECIMALS'] = 10

            if col in self.hierarchies:
                metacol.set_hierarchy(self.hierarchies[col])

            if col in self.codelists:
                metacol.set_codelist(self.codelists[col])

        return metadata

    def to_csv(self, file=None, na_rep=""):
        dataset = self.dataset.copy(deep=False)
        for col in self.dataset.columns:
            if is_bool_dtype(col):
                dataset[col] = dataset[col].astype(int)

        result = dataset.to_csv(file, index=False, header=False, na_rep=na_rep)
        if isinstance(file, (str, Path)):
            self.filepath = file
        return result
