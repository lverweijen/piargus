import io
import os
import re
from pathlib import Path


class Hierarchy:
    """Describe a hierarchy for use with TauArgus"""

    @classmethod
    def from_hrc(cls, file, indent='@'):
        if isinstance(file, (str, Path)):
            with open(file) as reader:
                hierarchy = cls.from_hrc(reader)
                hierarchy.filepath = Path(file)
                return hierarchy

        pattern = re.compile(rf"^(?P<prefix>[{indent}]*)(?P<code>.*)")

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

    def __str__(self):
        return self.to_hrc()

    def keys(self):
        return self._data.keys()

    def codes(self):
        for key in self.keys():
            yield key
            yield from self[key].codes()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def to_hrc(self, file=None, indent='@', length=0):
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self._to_hcr(file, indent, length)
            return file.getvalue()
        elif hasattr(file, 'write'):
            self._to_hcr(file, indent, length)
        else:
            self.filepath = Path(file)
            with open(file, 'w', newline='\n') as writer:
                self._to_hcr(writer, indent, length)

    def _to_hcr(self, file, indent, length, _level=0):
        for key in self.keys():
            file.write(indent * _level + str(key).rjust(length) + '\n')
            self[key]._to_hcr(file, indent, length, _level=_level+1)
