import abc
import io
import os
from collections.abc import Mapping, Sequence, Collection, Iterable, MutableMapping
from pathlib import Path
from typing import Optional, TextIO, Any, Union

import pandas as pd
from pandas.core.dtypes.common import is_string_dtype, is_bool_dtype, is_numeric_dtype, \
    is_float_dtype

from .codelist import CodeList
from .hierarchy import FlatHierarchy, Hierarchy, LevelHierarchy, TreeHierarchy
from ..constants import OPTIMAL, SAFE, UNSAFE, PROTECTED
from ..outputspec import Table, Apriori

DEFAULT_COLUMN_LENGTH = 20
DEFAULT_STATUS_MARKERS = {
    "SAFE": SAFE,
    "UNSAFE": UNSAFE,
    "PROTECT": PROTECTED,
}


class InputData(Mapping, metaclass=abc.ABCMeta):
    """Abstract base class for a dataset that needs to be protected by Tau Argus."""
    separator = ','

    def __init__(
        self,
        dataset,
        metadata: os.PathLike = None,
        *,
        hierarchies: Mapping[str, Hierarchy] = None,
        codelists: Mapping[str, CodeList] = None,
        column_lengths: Mapping[str, int] = None,
        total_codes: Mapping[str, str] = None,
    ):
        """
        Abstract class for input data. Either initialize MicroData or TableData.

        :param dataset: The dataset to make tables for.
        :param metadata: If a metadata file is supplied, it will be used. All other parameters will be ignored.
        :param hierarchies: The hierarchies to use for categorial data in the dataset.
        :param codelists: Codelists (dicts) for categorical data in the dataset.
        :param column_lengths: For each column the length.
        :param total_codes: Codes within explanatory that are used for the totals.
            The lengths can also be derived by calling resolve_column_lengths.
        """

        self._dataset = dataset
        self._columns: MutableMapping[str, InputColumn] = dict()
        self.filepath = None
        self.metadata = metadata

        for col, data in dataset.items():
            self._columns[col] = InputColumn(data)

        if hierarchies:
            for col, hierarchy in hierarchies.items():
                self._columns[col].hierarchy = hierarchy

        if codelists:
            for col, codelist in codelists.items():
                self._columns[col].codelist = codelist

        if column_lengths:
            for col, length in column_lengths.items():
                self._columns[col].code_length = length

        if total_codes:
            for col, total_code in total_codes.items():
                self._columns[col].total_code = total_code

    def __len__(self):
        return len(self._columns)

    def __iter__(self):
        return iter(self._columns)

    def __getitem__(self, col: str) -> "InputColumn":
        return self._columns[col]

    def get_dataset(self) -> pd.DataFrame:
        """Get original data back."""
        return pd.DataFrame({name: col.data for name, col in self._columns.items()})

    def write_data(self, path: os.PathLike | TextIO | None):
        """Save data to a file in the format which tau-argus requires."""
        if isinstance(path, os.PathLike):
            self.filepath = Path(path)

        return self.get_dataset().to_csv(path, index=False, header=False, na_rep="")

    def write_metadata(self, path: os.PathLike | TextIO | None):
        """Save metadata to a file in the format which tau-argus requires."""

        if not path:
            txt = io.StringIO()
            self._write_metadata(txt)
            return txt.getvalue()
        elif isinstance(path, os.PathLike):
            with open(path, "w", newline='') as writer:
                self._write_metadata(writer)
            self.metadata = Path(path)
        else:
            self._write_metadata(path)

    @abc.abstractmethod
    def _write_metadata(self, path: TextIO):
        pass


class InputColumn:
    """A single column of InputData."""
    def __init__(self, data: pd.Series):
        if is_bool_dtype(data.dtype):
            data = data.astype(int)

        self._data = data
        self.recodable: bool = False
        self._hierarchy = FlatHierarchy()
        self._codelist = None
        self._decimals = 15
        self._codelength = None
        self.missing = set()

    @property
    def data(self) -> pd.Series:
        """Return data in this column."""
        return self._data

    @property
    def name(self):
        """Name of column."""
        return self._data.name

    @property
    def hierarchy(self) -> Optional[Hierarchy]:
        """Hierarchy of column."""
        if self.recodable:
            return self._hierarchy
        else:
            return None

    @hierarchy.setter
    def hierarchy(self, value: Hierarchy | Sequence[int] | os.PathLike):
        if value:
            self.recodable = True

        self._hierarchy = Hierarchy(value)

    @hierarchy.deleter
    def hierarchy(self):
        self.hierarchy = None

    @property
    def total_code(self) -> Optional[str]:
        """Total code of column."""
        if self.recodable:
            return self.hierarchy.total_code
        else:
            return None

    @total_code.setter
    def total_code(self, value: str):
        if value is None:
            self._hierarchy.total_code = "Total"
            return

        self.recodable = True
        self._hierarchy.total_code = value

    @property
    def codelist(self) -> Optional[CodeList]:
        """Codelist of column."""
        return self._codelist

    @codelist.setter
    def codelist(self, value: Mapping[str, str] | os.PathLike | None):
        if value is None:
            self._codelist = None
        else:
            self._codelist = CodeList(value)

    @property
    def is_numeric(self) -> bool:
        """Whether column is numeric."""
        return is_numeric_dtype(self._data.dtype)

    @property
    def decimals(self) -> Optional[int]:
        """How many decimal places column has."""
        if is_float_dtype(self._data.dtype):
            return self._decimals
        else:
            return None

    @decimals.setter
    def decimals(self, value):
        if self.is_numeric:
            self._decimals = value
        else:
            raise ValueError(f"Column {self._data.name} is not numeric")

    @property
    def code_length(self):
        """Length of code in column."""
        length = self._codelength
        if not length:
            if hasattr(self.hierarchy, "code_length"):
                length = self.hierarchy.code_length
            elif self.codelist is not None:
                length = self.codelist.code_length
            else:
                data = self._data
                if isinstance(data.dtype, pd.CategoricalDtype):
                    length = data.cat.categories.str.len().max()
                elif is_string_dtype(data.dtype):
                    length = data.str.len().max()
                elif is_bool_dtype(data.dtype):
                    length = 1
                else:
                    length = DEFAULT_COLUMN_LENGTH

            self._codelength = length

        return length

    @code_length.setter
    def code_length(self, value):
        self._codelength = value

    @code_length.deleter
    def code_length(self):
        self._codelength = None

    def write_metadata(self, file, include_length):
        """Write metadata related to this column."""
        header = [self.name]
        if include_length:
            header.append(str(self.code_length))
        if self.missing:
            header.append(' '.join(map(str, self.missing)))
        file.write(" ".join(header) + "\n")

        if self.is_numeric:
            file.write("\t<NUMERIC>\n")

            if self.decimals:
                file.write(f"\t<DECIMALS> {self.decimals}\n")

        if self.recodable:
            file.write("\t<RECODABLE>\n")
            file.write(f"\t<TOTCODE> {self.hierarchy.total_code}\n")

            match self.hierarchy:
                case FlatHierarchy():
                    pass
                case LevelHierarchy(levels):
                    file.write("\t<HIERARCHICAL>\n")
                    hierlevels = " ".join(map(str, levels))
                    file.write(f"\t<HIERLEVELS> {hierlevels}\n")
                case TreeHierarchy(filepath, indent):
                    file.write("\t<HIERARCHICAL>\n")
                    file.write(f"\t<HIERCODELIST> {filepath}\n")
                    file.write(f"\t<HIERLEADSTRING> {indent}\n")
                case unknown_hierarchy:
                    raise TypeError(f"Unsupported Hierarchy-type: {type(unknown_hierarchy)}")


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


class TableData(InputData, Table):
    """
    A TableData instance contains data that has already been aggregated.

    It can be used for tables that are unprotected or partially protected.
    If it's already partially protected, this can be indicated by `status_indicator`.
    Most of the parameters are already explained either in InputData or in Table.
    """
    def __init__(
        self,
        dataset,
        explanatory: Sequence[str],
        response: str,
        shadow: Optional[str] = None,
        cost: Optional[str] = None,
        labda: Optional[int] = None,
        *,
        hierarchies: Mapping[str, Hierarchy] = None,
        total_codes: Union[str, Mapping[str, str]] = None,
        frequency: Optional[str] = None,
        top_contributors: Sequence[str] = (),
        lower_protection_level: Optional[str] = None,
        upper_protection_level: Optional[str] = None,
        status_indicator: Optional[str] = None,
        status_markers: Optional[Mapping[str, str]] = None,
        safety_rule: Union[str, Collection[str]] = (),
        apriori: Union[Apriori, Iterable[Sequence[Any]]] = (),
        suppress_method: Optional[str] = OPTIMAL,
        suppress_method_args: Sequence[Any] = (),
        **kwargs
    ):
        """
        Initialize a TableData instance.

        :param dataset: The dataset containing the table. This dataset should include totals.
        :param explanatory: See Table.
        :param response: See Table.
        :param shadow: See Table.
        :param cost: See Table.
        :param labda: See Table.
        :param total_codes: Codes within explanatory that are used for the totals.
        :param frequency: Column containing number of contributors to this cell.
        :param top_contributors: The columns containing top contributions for dominance rule.
            The columns should be in the same order as they appear in the dataset.
            The first of the these columns should describe the highest contribution,
            the second column the second-highest contribution.
        :param lower_protection_level: Column that denotes the level below which values are unsafe.
        :param upper_protection_level: Column that denotes the level above which values are unsafe.
        :param status_indicator: Column indicating the status of cells.
        :param status_markers: The meaning of each status.
            Should be dictionary mapping "SAFE", "UNSAFE" and "STATUS" to a code indicating status.
        :param kwargs: See InputData
        """

        Table.__init__(self,
                       explanatory=explanatory,
                       response=response,
                       shadow=shadow,
                       cost=cost,
                       labda=labda,
                       safety_rule=safety_rule,
                       apriori=apriori,
                       suppress_method=suppress_method,
                       suppress_method_args=suppress_method_args)

        InputData.__init__(self, dataset, hierarchies=hierarchies, total_codes=total_codes, **kwargs)

        if status_markers is None:
            status_markers = DEFAULT_STATUS_MARKERS

        self.lower_protection_level = lower_protection_level
        self.upper_protection_level = upper_protection_level
        self.frequency = frequency
        self.top_contributors = top_contributors
        self.status_indicator = status_indicator
        self.status_markers = status_markers

    def _write_metadata(self, file):
        """Generates a metadata file for tabular data."""

        file.write(f'\t<SEPARATOR> {self.separator}\n')

        if self.status_indicator:
            for status, marker in self.status_markers.items():
                file.write(f'\t<{status}> {marker}\n')

        for name, col in self._columns.items():
            col.write_metadata(file, include_length=False)

            if name in self.top_contributors:
                file.write("<\tMAXSCORE>\n")
            if name == self.lower_protection_level:
                file.write('\t<LOWERPL>\n')
            if name == self.upper_protection_level:
                file.write('\t<UPPERPL>\n')
            if name == self.frequency:
                file.write('\t<FREQUENCY>\n')
            if name == self.status_indicator:
                file.write('\t<STATUS>\n')
