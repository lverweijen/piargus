import io
import re
import shlex
from pathlib import Path
from typing import Optional

from .codelist import CodeList
from .hierarchy import Hierarchy

PROPERTY_PATTERN = re.compile(r"\<(.*)\>")


class MetaData:
    @classmethod
    def from_rda(cls, file):
        if not hasattr(file, 'read'):
            with open(file) as reader:
                metadata = cls.from_rda(reader)
                metadata.filepath = Path(file)
                return metadata

        column = None
        metadata = MetaData()
        for line in file:
            arguments = shlex.split(line, posix=False)
            head = arguments.pop(0)

            match = PROPERTY_PATTERN.match(head)
            if match:
                variable = match.group(1)

                if arguments:
                    [value] = arguments
                else:
                    value = True

                if column:
                    column[variable] = value
                elif variable == 'SEPARATOR':
                    metadata.separator = value
                else:
                    raise ValueError(f"Unknown global property: {variable}")
            else:
                column = Column(head, *arguments)
                metadata[head] = column

        return metadata

    def __init__(self, columns=None, separator=','):
        if columns is None:
            columns = dict()

        self._columns = columns
        self.separator = separator
        self.filepath = None

    def __str__(self):
        buffer = io.StringIO()
        self.to_rda(buffer)
        return buffer.getvalue()

    def __getitem__(self, key):
        return self._columns[key]

    def __setitem__(self, key, value):
        self._columns[key] = value
        self._columns[key].name = key

    def to_rda(self, file):
        if not hasattr(file, 'write'):
            filepath = Path(file)
            with open(file, 'w') as file:
                result = self.to_rda(file)

            self.filepath = filepath
            return result

        file.write(f'    <SEPARATOR> {self.separator}\n')
        file.writelines(str(column) + '\n' for column in self._columns.values())


class Column:
    def __init__(self, name=None, length=None, missing=None):
        self.name = name
        self.width = length
        self.missing = missing
        self._data = dict()

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __str__(self):
        out = [f"{self.name} {self.width} {self.missing}"]
        for key, value in self._data.items():
            if value is None or value is False:
                pass
            elif value is True:
                out.append(f"    <{key}>")
            else:
                out.append(f"    <{key}> {value}")

        return "\n".join(out)

    def set_hierarchy(self, hierarchy: Optional[Hierarchy], indent='@'):
        if hierarchy is not None:
            if hierarchy.filepath is None:
                raise TypeError("hierarchy.to_hrc needs to be called first.")

            self['HIERARCHICAL'] = True
            self['HIERCODELIST'] = hierarchy.filepath
            self['HIERLEADSTRING'] = indent
        else:
            self['HIERARCHICAL'] = False
            self['HIERCODELIST'] = None
            self['HIERLEADSTRING'] = None

    def get_hierarchy(self) -> Optional[Hierarchy]:
        if self["HIERCODELIST"]:
            return Hierarchy.from_hrc(self["HIERCODELIST"], self["HIERLEADSTRING"])
        else:
            return None

    def set_codelist(self, codelist: Optional[CodeList]):
        if codelist:
            if codelist.filepath is None:
                raise TypeError("codelist.to_cdl needs to be called first.")

            self['CODELIST'] = codelist.filepath
        else:
            self['CODELIST'] = None

    def get_codelist(self) -> Optional[CodeList]:
        if self["CODELIST"]:
            return CodeList.from_cdl(self["CODELIST"])
        else:
            return None
