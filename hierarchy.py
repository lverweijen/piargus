import io
import os


class Hierarchy:
    def __init__(self, data):
        self._data = {}
        if hasattr(data, 'keys'):
            for key in data.keys():
                self._data[key] = Hierarchy(data[key])
        else:
            for key in data:
                self._data[key] = Hierarchy(dict())

    def keys(self):
        return self._data.keys()

    def codes(self):
        for key in self.keys():
            yield key
            yield from self[key].codes

    def __getitem__(self, key):
        return self._data[key]

    def to_hrc(self, file=None, indent='@', length=0):
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self._to_hcr(file, indent, length)
            return file.getvalue()
        elif hasattr(file, 'write'):
            self._to_hcr(file, indent, length)
        else:
            with open(file, 'w', newline='\n') as writer:
                self._to_hcr(writer, indent, length)

    def _to_hcr(self, file, indent, length, _level=0):
        for key in self.keys():
            file.write(indent * _level + str(key).rjust(length) + '\n')
            self[key]._to_hcr(file, indent, length, _level=_level+1)
