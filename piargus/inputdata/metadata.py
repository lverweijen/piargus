import io
import re
import shlex
from pathlib import Path
from typing import Optional

from .codelist import CodeList
from .hierarchy import Hierarchy, LevelHierarchy, TreeHierarchy, FlatHierarchy

PROPERTY_PATTERN = re.compile(r"\<(.*)\>")


class MetaData:
    """
    Metadata describing InputData.

    Usually it's not required for a user to create a MetaData themselves.
    If not provided to job one can be generated from inputdata.
    It's also possible to call:
    `metadata = inputdata.generate_metadata()`
    Then the resulting object can be modified.

    This class can be used directly when an existing rda file needs to be used.
    An existing file can be loaded by MetaData.from_rda and passed to Job.
    """
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
                    metadata.status_markers[variable] = value
            else:
                column = Column(head, *arguments)
                metadata[head] = column

        return metadata

    def __init__(self, columns=None, separator=',', status_markers=None):
        if columns is None:
            columns = dict()
        if status_markers is None:
            status_markers = dict()

        self._columns = columns
        self.status_markers = status_markers
        self.separator = separator
        self.filepath = None

    def __str__(self):
        return self.to_rda()

    def __getitem__(self, key):
        return self._columns[key]

    def __contains__(self, item):
        return item in self._columns

    def __setitem__(self, key, value):
        self._columns[key] = value
        self._columns[key].name = key

    def to_rda(self, file=None):
        if file is None:
            buffer = io.StringIO()
            self.to_rda(buffer)
            return buffer.getvalue()
        elif not hasattr(file, 'write'):
            filepath = Path(file)
            with open(file, 'w') as file:
                result = self.to_rda(file)

            self.filepath = filepath
            return result
        else:
            file.write(f'    <SEPARATOR> {self.separator}\n')
            for status, marker in self.status_markers.items():
                file.write(f'    <{status}> {marker}\n')
            file.writelines(str(column) + '\n' for column in self._columns.values())


class Column:
    def __init__(self, name=None, length=None, missing=None):
        if missing is None:
            missing = set()

        self.name = name
        self.width = length
        self.missing = missing
        self._data = dict()

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __str__(self):
        if self.missing:
            missing_str = ' '.join(map(str, self.missing))
            out = [f"{self.name} {self.width} {missing_str}"]
        else:
            out = [f"{self.name} {self.width}"]

        for key, value in self._data.items():
            if value is None or value is False:
                pass
            elif value is True:
                out.append(f"    <{key}>")
            else:
                out.append(f"    <{key}> {value}")

        return "\n".join(out)

    def set_hierarchy(self, hierarchy: Optional[Hierarchy]):
        if hasattr(hierarchy, "filepath") and hierarchy.filepath is None:
            raise TypeError("hierarchy.to_hrc needs to be called first.")
        elif hierarchy is not None and not isinstance(hierarchy, Hierarchy):
            raise TypeError(f"{hierarchy} should be a hierarchy")

        is_hierarchical = getattr(hierarchy, "is_hierarchical", False)

        # Handle ThreeHierarchy
        codelist = getattr(hierarchy, "filepath", None)
        leadstring = getattr(hierarchy, "indent", None)

        # Handle CodeHierarchy
        levels = getattr(hierarchy, "levels", None)

        self["HIERARCHICAL"] = is_hierarchical
        self['HIERCODELIST'] = codelist
        self['HIERLEADSTRING'] = leadstring

        if levels:
            self['HIERLEVELS'] = " ".join(map(str, levels))
        else:
            self['HIERLEVELS'] = None

        self["TOTCODE"] = getattr(hierarchy, "total_code", None)

    def get_hierarchy(self) -> Optional[Hierarchy]:
        total_code = self['TOTCODE']

        if self["RECODABLE"]:
            if self["HIERCODELIST"]:
                hierarchy = TreeHierarchy.from_hrc(self["HIERCODELIST"], indent=self["HIERLEADSTRING"])
            elif self["HIERLEVELS"]:
                levels = map(int, self['HIERLEVELS'].split())
                hierarchy = LevelHierarchy(levels)
            else:
                hierarchy = FlatHierarchy()

            if total_code is not None:
                hierarchy.total_code = total_code

            return hierarchy
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
