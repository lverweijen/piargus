from typing import Optional, Sequence, Any

from pandas.core.dtypes.common import is_bool_dtype

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
        Initialize MicroData.

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

    def _write_data(self, file):
        dataset = self._dataset.copy(deep=False)
        for col in self._dataset.columns:
            if is_bool_dtype(col):
                dataset[col] = dataset[col].astype(int)

        result = dataset.to_csv(file, index=False, header=False, na_rep="")
        return result

    def _write_metadata(self, file):
        file.write(f'\t<SEPARATOR> {self.separator}\n')
        for name, col in self._columns.items():
            col.write_metadata(file, include_length=True)

            if name == self.weight:
                file.write("\t<WEIGHT>\n")

            if name == self.request:
                request_str = ' '.join([f'"{v}"' for v in self.request_values])
                file.write(f"\t<REQUEST> {request_str}\n")

            if name == self.holding:
                file.write("\t<HOLDING>\n")
