from pathlib import Path
from typing import Optional, Sequence, Any

from pandas.core.dtypes.common import is_bool_dtype, is_numeric_dtype, is_float_dtype

from .metadata import MetaData
from .inputdata import InputData


class MicroData(InputData):
    """
    A MicroData instance contains the data at an individual level.

    From such microdata, tabular aggregates can be constructed.
    """

    def __init__(
        self,
        dataset,
        *,
        weight: Optional[str] = None,
        request: Optional[str] = None,
        request_values: Sequence[Any] = ("1", "2"),
        holding: Optional[str] = None,
        **kwargs
    ):
        """

        :param dataset: The dataset (pd.DataFrame) containing the microdata.
        :param weight: Column that contains the sampling weight of this record.
        :param request: Column that indicates if a respondent asks for protection.
        :param request_values: Parameters that indicate if request is asked.
            Two different request values can be specified for two different levels in the request_rule.
        :param holding: Column containing the group identifier.
        :param args: See InputData.
        :param kwargs: See InputData.

        See the Tau-Argus documentation for more details on these parameters.
        """
        super().__init__(dataset, **kwargs)
        self.weight = weight
        self.request = request
        self.request_values = request_values
        self.holding = holding

    def generate_metadata(self) -> MetaData:
        """Generates a metadata file for free format micro data."""
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

        if self.weight is not None:
            metadata[self.weight]["WEIGHT"] = True

        if self.request is not None:
            metadata[self.request]["REQUEST"] = ' '.join([f'"{v}"' for v in self.request_values])

        if self.holding is not None:
            metadata[self.holding]["HOLDING"] = True

        return metadata

    def to_csv(self, file=None, na_rep=""):
        dataset = self.dataset.copy(deep=False)
        for col in self.dataset.columns:
            if is_bool_dtype(col):
                dataset[col] = dataset[col].astype(int)

        result = dataset.to_csv(file, index=False, header=False, na_rep=na_rep)
        if isinstance(file, (str, Path)):
            self.filepath = Path(file)
        return result
