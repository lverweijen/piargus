import abc
from abc import ABC

from .codelist import CodeList
from .hierarchy import Hierarchy
from .metadata import MetaData, Column

DEFAULT_COLUMN_LENGTH = 20


class InputData(ABC):
    def __init__(self, dataset, name=None, hierarchies=None, codelists=None, safety_rules=None,
                 column_lengths=None):
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
