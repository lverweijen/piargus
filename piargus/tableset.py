# TODO Remove

import warnings
from typing import Mapping, Hashable, Union, Iterable, Optional, Sequence

from .table import Table


class TableSet:
    """A collection of tables that can be used as frozen dictionary or list."""
    __slots__ = "_tables", "suppress_method", "suppress_method_args"

    def __init__(
        self,
        tables: Union[Mapping[Hashable, Table], Iterable[Table]],
        suppress_method: Optional[str] = None,  # Experimental
        suppress_method_args: Sequence = ()  # Experimental
    ):
        """
        Create a tableset

        Parameters:
        :param tables: Either a mapping or an iterable containing the Tables.
        :param suppress_method: Method to use for linked suppression.
        Options are:
        - `GHMITER` ("GH"): Hypercube
        - `MODULAR` ("MOD"): Modular
        Warning: The Tau-Argus manual doesn't document this. Therefore, usage is not recommended.
        :param suppress_method_args: Parameters to pass to suppress_method.
        """
        if isinstance(tables, TableSet):
            suppress_method = tables.suppress_method
            suppress_method_args = tables.suppress_method_args

        if isinstance(tables, (TableSet, Mapping)):
            tables = {key: table if isinstance(table, Table) else Table(**table)
                      for key, table in tables.items()}
        elif isinstance(tables, Iterable):
            tables = {index: table if isinstance(table, Table) else Table(**table)
                      for index, table in enumerate(tables)}
        else:
            raise TypeError("tables should be Dict or Iterable")

        if suppress_method:
            warnings.warn("Protection of linked tables by batchfile isn't officially documented. "
                          "Therefore, correct results are NOT guaranteed.")

        self._tables = tables
        self.suppress_method = suppress_method
        self.suppress_method_args = suppress_method_args

    def __repr__(self):
        type_name = self.__class__.__qualname__
        return f"{type_name}({self._tables})"

    def __len__(self):
        return len(self._tables)

    def __getitem__(self, key):
        return self._tables[key]

    def __iter__(self):
        return iter(self._tables.values())

    def __contains__(self, item):
        return item in self._tables

    def keys(self):
        return self._tables.keys()

    def values(self):
        return self._tables.values()

    def items(self):
        return self._tables.items()
