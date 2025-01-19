import abc
import io
import os
from collections.abc import Sequence, MutableMapping, Mapping
from os import PathLike
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

        self.init_columns(
            dataset,
            hierarchies=hierarchies,
            codelists=codelists,
            column_lengths=column_lengths,
            total_codes=total_codes
        )

    def init_columns(
        self,
        data: pd.DataFrame,
        *,
        hierarchies: Dict[str, Hierarchy] = None,
        codelists: Dict[str, CodeList] = None,
        column_lengths: Dict[str, int] = None,
        total_codes: Dict[str, str] = None,
    ):
        for col, value in data.items():
            self._columns[col] = InputColumn(value)

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

    def write_data(self, path: os.PathLike):
        """Save data to a file in the csv-format which tau-argus requires."""
        with open(path, "w", newline='') as writer:
            self._write_data(writer)

        if isinstance(path, PathLike):
            self.filepath = Path(path)

    def write_metadata(self, path: os.PathLike | io.FileIO):
        """Save data to a file in the csv-format which tau-argus requires."""
        with open(path, "w") as writer:
            self._write_metadata(writer)

        if isinstance(path, PathLike):
            self.filepath_metadata = Path(path)

    @abc.abstractmethod
    def _write_data(self, file: TextIO):
        """Save data to a file in the csv-format which tau-argus requires."""

    @abc.abstractmethod
    def _write_metadata(self, path: TextIO):
        """Save data to a file in the csv-format which tau-argus requires."""



class InputColumn:
    def __init__(self, data: pd.Series):
        self._data = data
        self.recodable: bool = False
        self._hierarchy = FlatHierarchy()
        self._codelist = None
        self._decimals = 15
        self._codelength = None
        self.missing = set()

    @property
    def name(self):
        return self._data.name

    @property
    def hierarchy(self) -> Optional[Hierarchy]:
        if self.recodable:
            return self._hierarchy
        else:
            return None

    @hierarchy.setter
    def hierarchy(self, value: Hierarchy | Sequence[int] | os.PathLike):
        if value is None:
            self._hierarchy = FlatHierarchy()
            return
        else:
            if isinstance(value, Hierarchy):
                hierarchy = value
            elif isinstance(value, Sequence):
                hierarchy = LevelHierarchy(value)
            elif isinstance(value, os.PathLike):
                path = Path(value)
                if path.suffix == ".hrc":
                    hierarchy = TreeHierarchy.from_hrc(path)
                else:
                    raise ValueError("hierarchy path should end in .hrc")
            else:
                raise TypeError("Should be passed a Hierarchy.")

            self.recodable = True
            self._hierarchy = hierarchy

    @hierarchy.deleter
    def hierarchy(self):
        self.hierarchy = None

    @property
    def total_code(self) -> Optional[str]:
        if self.recodable:
            return self.hierarchy.total_code
        else:
            return None

    @total_code.setter
    def total_code(self, value: str):
        if value is None:
            self.total_code = "Total"
            return

        self.recodable = True
        self._hierarchy.total_code = value

    @property
    def codelist(self) -> Optional[CodeList]:
        return self._codelist

    @codelist.setter
    def codelist(self, value: CodeList | os.PathLike):
        if isinstance(value, CodeList):
            codelist = value
        elif isinstance(value, os.PathLike):
            path = Path(value)
            if path.suffix == ".cdl":
                codelist = CodeList.from_cdl(path)
            else:
                raise ValueError("Not a .cdl file")
        else:
            raise TypeError("A codelist was expected")

        self._codelist = codelist

    @property
    def is_numeric(self) -> bool:
        return is_numeric_dtype(self._data.dtype)

    @property
    def decimals(self) -> Optional[int]:
        if is_float_dtype(self._data):
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

    def write_metadata(self, file):
        if self.missing:
            missing_str = ' '.join(map(str, self.missing))
            file.write(f"{self.name} {self.code_length} {missing_str}\n")
        else:
            file.write(f"{self.name} {self.code_length}\n")

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
