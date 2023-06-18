from typing import Mapping, Hashable, Union, Iterable

from .table import Table


class TableSet:
    """A collection of tables that can be used as frozen dictionary or list."""
    __slots__ = "_tables"

    def __init__(self, tables: Union[Mapping[Hashable, Table], Iterable[Table]]):
        if isinstance(tables, Mapping):
            tables = {key: table if isinstance(table, Table) else Table(**table)
                      for key, table in tables.items()}
        elif isinstance(tables, Iterable):
            tables = {index: table if isinstance(table, Table) else Table(**table)
                      for index, table in enumerate(tables)}
        else:
            raise TypeError("tables should be Dict or Iterable")

        self._tables = tables

    def __repr__(self):
        type_name = self.__class__.__qualname__
        return f"{type_name}({self._tables})"

    def __len__(self):
        return len(self._tables)

    def __getitem__(self, key):
        return self._tables[key]

    def __iter__(self):
        return iter(self._tables.values())

    def keys(self):
        return self._tables.keys()

    def values(self):
        return self._tables.values()

    def items(self):
        return self._tables.items()
