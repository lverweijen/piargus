import abc
import io
import os
from collections.abc import Sequence, MutableMapping, Mapping
from pathlib import Path
from typing import Dict, Optional, TextIO

import pandas as pd
from pandas.core.dtypes.common import is_string_dtype, is_bool_dtype, is_numeric_dtype, \
    is_float_dtype

from .codelist import CodeList
from .hierarchy import FlatHierarchy, Hierarchy, LevelHierarchy, TreeHierarchy

DEFAULT_COLUMN_LENGTH = 20


class InputData(Mapping, metaclass=abc.ABCMeta):
    """Abstract base class for a dataset that needs to be protected by Tau Argus."""
    separator = ','

    def __init__(
        self,
        dataset,
        *,
        hierarchies: Dict[str, Hierarchy] = None,
        codelists: Dict[str, CodeList] = None,
        column_lengths: Dict[str, int] = None,
        total_codes: Dict[str, str] = None,
    ):
        """
        Abstract class for input data. Either initialize MicroData or TableData.

        :param dataset: The dataset to make tables for.
        :param hierarchies: The hierarchies to use for categorial data in the dataset.
        :param codelists: Codelists (dicts) for categorical data in the dataset.
        :param column_lengths: For each column the length.
        :param total_codes: Codes within explanatory that are used for the totals.
            The lengths can also be derived by calling resolve_column_lengths.
        """

        self._dataset = dataset
        self._columns: MutableMapping[str, InputColumn] = dict()
        self.filepath = None
        self.filepath_metadata = None

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
        return pd.DataFrame({name: col.get_data() for name, col in self._columns.items()})

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
            self.filepath_metadata = Path(path)
        else:
            self._write_metadata(path)

    @abc.abstractmethod
    def _write_metadata(self, path: TextIO):
        pass


class InputColumn:
    """A single column of InputData."""
    def __init__(self, data: pd.Series):
        self._data = data
        self.recodable: bool = False
        self._hierarchy = FlatHierarchy()
        self._codelist = None
        self._decimals = 15
        self._codelength = None
        self.missing = set()

    def get_data(self) -> pd.Series:
        """Return data in this column."""
        d = self._data
        if is_bool_dtype(d.dtype):
            return d.astype(int)
        else:
            return d

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
