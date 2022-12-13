from pathlib import Path


class MetaData:
    def __init__(self, columns=None, separator=','):
        if columns is None:
            columns = dict()

        self._columns = columns
        self.separator = separator

    def __getitem__(self, key):
        return self._columns[key]

    def __setitem__(self, key, value):
        self._columns[key] = value
        self._columns[key].name = key

    def to_rdb(self, file):
        if not hasattr(file, 'write'):
            with open(file, 'w') as file:
                return self.to_rdb(file)

        file.write(f'    <SEPARATOR> {self.separator}\n')
        file.writelines(str(column) + '\n' for column in self._columns.values())


class Column:
    def __init__(self, name=None, width=None, missing=None):
        self.name = name
        self.width = width
        self.missing = missing
        self.body = dict()

    def __getitem__(self, key):
        return self.body[key]

    def __setitem__(self, key, value):
        self.body[key] = value

    def __str__(self):
        out = [f"{self.name} {self.width} {self.missing}"]
        for key, value in self.body.items():
            if value is None or value is False:
                pass
            elif value is True:
                out.append(f"    <{key}>")
            elif isinstance(value, (str, int)):
                out.append(f"    <{key}> {value}")

        return "\n".join(out)
