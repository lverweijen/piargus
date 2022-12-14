from pandas.core.dtypes.common import is_numeric_dtype, is_categorical_dtype, is_string_dtype, is_float_dtype

from .codelist import CodeList
from .hierarchy import Hierarchy
from .metadata import MetaData, Column

NA_REP = "<NA>"
HIERARCHY_LEADSTRING = '@'
DEFAULT_COLUMN_LENGTH = 20
MIN_COLUMN_LENGTH = 5


class MicroData:
    def __init__(self, dataset, name=None, column_lengths=None, hierarchies=None, codelists=None, safety_rules=None):
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

    def metadata(self, hierarchies_paths=None, codelists_paths=None) -> MetaData:
        self.resolve_column_lengths()

        metadata = MetaData()
        for col in self.dataset.columns:
            metacol = metadata[col] = Column(col, length=self.column_lengths[col], missing=NA_REP)

            col_dtype = self.dataset[col].dtype
            metacol['NUMERIC'] = is_numeric_dtype(col_dtype)
            metacol['RECODABLE'] = (is_categorical_dtype(col_dtype)
                                    or is_string_dtype(col_dtype))
            if is_float_dtype(col_dtype):
                metacol['DECIMALS'] = 10

            if col in self.hierarchies:
                metacol['HIERARCHICAL'] = True
                metacol['HIERCODELIST'] = hierarchies_paths[col]
                metacol['HIERLEADSTRING'] = HIERARCHY_LEADSTRING

            if col in self.codelists:
                metacol['CODELIST'] = codelists_paths[col]

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

                self.column_lengths[col] = max(column_length, MIN_COLUMN_LENGTH)

    def to_csv(self, file, na_rep=NA_REP):
        self.dataset.to_csv(file, index=False, header=False, na_rep=na_rep)

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
