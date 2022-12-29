import abc
from abc import ABC

from .codelist import CodeList
from .hierarchy import Hierarchy
from .metadata import MetaData, Column

DEFAULT_COLUMN_LENGTH = 20


class InputData(ABC):
    def __init__(self, dataset, name=None, hierarchies=None, codelists=None, safety_rules=None,
                 column_lengths=None):
        """
        Abstract class for input data. Either initialize MicroData or TableData.

        :param dataset: The dataset to make tables for.
        :param name: The name to use when write the data to a file.
        :param hierarchies: The hierarchies to use for categorial data in the dataset.
        :param codelists: Codelists (dicts) for categorical data in the dataset.
        :param safety_rules: Safety rules to apply to the data.
        Options are:
        - P(p, n) - For p-rule
        - NK(n, k) - Dominance rule
        - ZERO(safety_range)
        - FREQ(minfreq, safety_range)
        - REQ(proc1, proc2, safety_margin)
        See the Tau-Argus manual for details on those rules.
        :param column_lengths: For each column the length. If not given, a length will be derived from the data.
        For strings, it will look at hierarchies and codelists.
        For numbers, it will default to 20.
        """

        if name is None:
            name = f'data_{id(self)}'

        if column_lengths is None:
            column_lengths = dict()

        self.dataset = dataset
        self.name = name
        self.hierarchies = hierarchies
        self.codelists = codelists
        self.safety_rules = safety_rules
        self.column_lengths = column_lengths
        self.filepath = None

    @abc.abstractmethod
    def generate_metadata(self) -> MetaData:
        """Generate metadata corresponding to the input data."""
        self.resolve_column_lengths()

        metadata = MetaData()
        for col in self.dataset.columns:
            metadata[col] = Column(col, length=self.column_lengths[col])

        return metadata

    def resolve_column_lengths(self, default=DEFAULT_COLUMN_LENGTH):
        """Make sure each column has a length."""
        for col in self.dataset.columns:
            if col not in self.column_lengths:
                if col in self.codelists:
                    column_length = max(map(len, self.codelists[col].codes()))
                elif col in self.hierarchies:
                    column_length = max(map(len, self.hierarchies[col].codes()))
                else:
                    column_length = default

                self.column_lengths[col] = column_length

    @property
    def hierarchies(self):
        return self._hierarchies

    @hierarchies.setter
    def hierarchies(self, value):
        if value is None:
            value = dict()
        self._hierarchies = {col: hierarchy if isinstance(hierarchy, Hierarchy) else Hierarchy(hierarchy)
                             for col, hierarchy in value.items()}

    @property
    def codelists(self):
        return self._codelists

    @codelists.setter
    def codelists(self, value):
        if value is None:
            value = dict()
        self._codelists = {col: codelist if isinstance(codelist, CodeList) else CodeList(codelist)
                           for col, codelist in value.items()}

    @property
    def safety_rules(self):
        return self._safety_rules

    @safety_rules.setter
    def safety_rules(self, value):
        if value is None:
            value = set()
        elif isinstance(value, str):
            value = set(value.split('|'))
        else:
            value = set(value)

        self._safety_rules = value
