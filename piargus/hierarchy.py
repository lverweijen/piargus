import io
import os
import re
from pathlib import Path

import pandas as pd


class Hierarchy:
    """Describe a hierarchy for use with TauArgus"""

    @classmethod
    def from_hrc(cls, file, indent='@'):
        if isinstance(file, (str, Path)):
            with open(file) as reader:
                hierarchy = cls.from_hrc(reader)
                hierarchy.filepath = Path(file)
                return hierarchy

        pattern = re.compile(rf"^(?P<prefix>({re.escape(indent)})*)(?P<code>.*)")

        last_prefix = ''
        last_hierarchy = Hierarchy()
        stack = [last_hierarchy]

        for line in file:
            prefix_code = pattern.match(line)
            prefix = prefix_code['prefix']
            code = prefix_code['code']

            if len(prefix) > len(last_prefix):
                stack.append(last_hierarchy)
            elif len(prefix) < len(last_prefix):
                stack.pop(-1)

            last_hierarchy = Hierarchy()
            stack[-1][code] = last_hierarchy
            last_prefix = prefix

        return stack[0]

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        hierarchy = Hierarchy()
        mi = pd.MultiIndex.from_frame(df)

        for row in mi:
            nested_hierarchy = hierarchy
            for col in row:
                nested_hierarchy[col] = True
                nested_hierarchy = nested_hierarchy[col]

        return hierarchy

    def __init__(self, data=None):
        self._data = {}
        if data is None:
            pass
        elif hasattr(data, 'keys'):
            for key in data.keys():
                self._data[key] = Hierarchy(data[key])
        else:
            for key in data:
                self._data[key] = Hierarchy(dict())

        self.filepath = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __str__(self):
        return self.to_hrc()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if isinstance(value, bool):
            if value is True and key not in self._data:
                self._data[key] = Hierarchy()
            elif value is False and key in self._data:
                del self._data[key]
        else:
            if not isinstance(value, Hierarchy):
                value = Hierarchy(value)

            self._data[key] = value

    def __eq__(self, other):
        if hasattr(other, 'to_dict'):
            other = other.to_dict()

        return self.to_dict() == other

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        return self._data.keys()

    def codes(self, totals=True):
        for key in self.keys():
            if totals or not self[key].keys():
                yield key
            yield from self[key].codes(totals=totals)

    def to_dict(self):
        return {key: value.to_dict() for key, value in self._data.items()}

    def to_hrc(self, file=None, indent='@', length=0):
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self.to_hrc(file)
            return file.getvalue()
        elif hasattr(file, 'write'):
            self._to_hrc(file, indent, length)
        else:
            self.filepath = Path(file)
            with open(file, 'w', newline='\n') as writer:
                self._to_hrc(writer, indent, length)

    def _to_hrc(self, file, indent, length, _level=0):
        for key in self.keys():
            file.write(indent * _level + str(key).rjust(length) + '\n')
            self[key]._to_hrc(file, indent, length, _level=_level + 1)

    def to_dataframe(self, names) -> pd.DataFrame:
        if not self._data:
            return pd.DataFrame()

        names = list(names)
        name = names.pop(0)

        df_parts = []
        for key, value in self._data.items():
            df_part = value.to_dataframe(names)

            if df_part.empty:
                df_part = pd.DataFrame([{name: key}])
            else:
                df_part.insert(0, column=name, value=key)

            df_parts.append(df_part)

        return pd.concat(df_parts)
