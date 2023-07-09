import abc
import warnings
from typing import Dict

from pandas.core.dtypes.common import is_string_dtype, is_categorical_dtype, is_bool_dtype

from .codelist import CodeList
from .hierarchy import Hierarchy, DEFAULT_TOTAL_CODE
from .metadata import MetaData, Column

DEFAULT_COLUMN_LENGTH = 20


class InputData(metaclass=abc.ABCMeta):
    def __init__(
        self,
        dataset,
        name: str = None,
        hierarchies: Dict[str, Hierarchy] = None,
        codelists: Dict[str, CodeList] = None,
        column_lengths: Dict[str, int] = None,
        total_codes: Dict[str, str] = None,
    ):
        """
        Abstract class for input data. Either initialize MicroData or TableData.

        :param dataset: The dataset to make tables for.
        :param name: (unused)
        :param hierarchies: The hierarchies to use for categorial data in the dataset.
        :param codelists: Codelists (dicts) for categorical data in the dataset.
        :param column_lengths: For each column the length.
        :param total_codes: Codes within explanatory that are used for the totals.
        The lengths can also be derived by calling resolve_column_lengths.
        """

        if name is not None:
            warnings.warn("Name on input_data is no longer used.")

        if hierarchies is None:
            hierarchies = dict()

        if codelists is None:
            codelists = dict()

        if column_lengths is None:
            column_lengths = dict()

        if total_codes is None:
            total_codes = dict()
        elif isinstance(total_codes, str):
            # This is allowed on TableData, but not in general
            raise TypeError("Total codes must be a dict.")

        self.dataset = dataset
        self.codelists = codelists
        self.column_lengths = column_lengths
        self.total_codes = total_codes
        self.hierarchies = hierarchies  # Needs to be done after total_codes are created

        self.filepath = None

    @abc.abstractmethod
    def generate_metadata(self) -> MetaData:
        """Generate metadata corresponding to the input data."""
        self.resolve_column_lengths()

        metadata = MetaData()
        for col in self.dataset.columns:
            metacol = metadata[col] = Column(col, length=self.column_lengths[col])

            if col in self.total_codes:  # Normal way
                total_code = metacol['TOTCODE'] = self.total_codes[col]
            elif col in self.hierarchies:  # Use hierarchy as alternative
                total_code = self.hierarchies[col].total_code
            else:  # Reasonable default
                total_code = DEFAULT_TOTAL_CODE

            metacol['TOTCODE'] = total_code

        return metadata

    @abc.abstractmethod
    def to_csv(self, target):
        raise NotImplementedError

    def resolve_column_lengths(self, default=DEFAULT_COLUMN_LENGTH):
        """Make sure each column has a length.

        For strings, it will look at hierarchies and codelists or max string.
        For categorical, it will look at the longest label.
        For booleans 1/0 is used with code length of 1.
        For numbers, it will default to 20.

        :param default: The length to use for numbers and other datatypes.
        """
        dataset = self.dataset

        for col in dataset.columns:
            if col not in self.column_lengths:
                if col in self.hierarchies:
                    column_length = self.hierarchies[col].column_length()
                elif col in self.codelists:
                    column_length = self.codelists[col].column_length()
                elif is_categorical_dtype(dataset[col].dtype):
                    column_length = dataset[col].cat.categories.str.len().max()
                elif is_string_dtype(dataset[col].dtype):
                    column_length = dataset[col].str.len().max()
                elif is_bool_dtype(dataset[col].dtype):
                    column_length = 1
                else:
                    column_length = default

                self.column_lengths[col] = column_length

    @property
    def hierarchies(self):
        return self._hierarchies

    @hierarchies.setter
    def hierarchies(self, value):
        def m_hierarchy(value, col):
            if isinstance(value, Hierarchy):
                return value
            else:
                return Hierarchy(value, total_code=self.total_codes.get(col, DEFAULT_COLUMN_LENGTH))

        self._hierarchies = {col: hrc if isinstance(hrc, Hierarchy) else m_hierarchy(hrc, col)
                             for col, hrc in value.items()}

    @property
    def codelists(self):
        return self._codelists

    @codelists.setter
    def codelists(self, value):
        self._codelists = {col: codelist
                           if isinstance(codelist, CodeList) else CodeList(codelist)
                           for col, codelist in value.items()}
