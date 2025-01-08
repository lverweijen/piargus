import io
from pathlib import Path


class Apriori:
    """
    Apriori can be used to mark cells as safe or to specify that cells should not be suppressed.
    """
    @classmethod
    def from_hst(cls, file, separator=','):
        """Read from apriori-file (extension .hst)."""
        if not hasattr(file, 'read'):
            with open(file) as fp:
                apriori = cls.from_hst(fp)
            apriori.filepath = Path(file)
            return apriori

        apriori = cls(separator=separator)
        for line in file:
            elements = line.split(separator)
            last_element = elements[-1].casefold().strip()
            butlast_element = elements[-2].casefold().strip()
            if last_element in set("spu"):
                apriori.change_status(elements[:-1], last_element)
            elif butlast_element == 'c':
                apriori.change_cost(elements[:-2], last_element)
            elif butlast_element == 'pl':
                apriori.change_protection_level(elements[:-2], last_element)
            else:
                raise Exception(f"Neither {last_element} nor {butlast_element} contains a valid apriori-code.")

        return apriori

    def __init__(self, changes=(), separator=',', ignore_error=False, expand_trivial=True):
        self.changes = list()
        self.separator = separator
        self.ignore_error = ignore_error
        self.expand_trivial = expand_trivial
        self.filepath = None

        for change in changes:
            if isinstance(change, AprioriChange):
                self._add_change(change)
            else:
                self._add_change(*change)

    def __repr__(self):
        changes_repr = ",\n".join([str(change) for change in self.changes])
        return f"{self.__class__.__name__}([{changes_repr}])"

    def __str__(self):
        return self.to_hst()

    def __bool__(self):
        """Whether the apriori file contains at least one change."""
        return bool(self.changes)

    def _add_change(self, cell, code=None, *args):
        if isinstance(cell, AprioriChange):
            change = cell
        else:
            change = AprioriChange(cell=cell, code=code.strip().casefold(), parameters=args)

        self.changes.append(change)

    def change_status(self, cell, status):
        """
        Change status of cell to status.

        Status can be:
        - S mark safe
        - U mark unsafe
        - P mark protected
        """
        status = status.casefold().strip()
        if status not in {'s', 'u', 'p'}:
            raise ValueError("Status should be S, U or P")

        self._add_change(cell, status)

    def change_cost(self, cell, cost):
        """
        Change costs of cell.

        The higher the cost, the less likely this cell will be used for secondary suppression.
        """
        self._add_change(cell, 'C', int(cost))

    def change_protection_level(self, cell, protection_level):
        """Change protection level of cell."""
        self._add_change(cell, 'PL', int(protection_level))

    def to_hst(self, file=None):
        """Write to hst-file."""
        if file is None:
            file = io.StringIO()
            self.to_hst(file)
            return file.getvalue()
        elif not hasattr(file, 'write'):
            with open(file, 'w') as fp:
                self.to_hst(fp)
            self.filepath = Path(file)
        else:
            for change in self.changes:
                change.write(file, sep=self.separator)


class AprioriChange:
    def __init__(self, cell, code, parameters=()):
        self.cell = cell
        self.code = code
        self.parameters = parameters

    def __repr__(self):
        return f"{self.__class__.__name__}{self}"

    def __str__(self):
        return f"{(self.cell, self.code, *self.parameters)}"

    def write(self, file, sep):
        file.write(sep.join(self.cell))
        file.write(sep)
        file.write(self.code)

        if self.parameters:
            file.write(sep)
            file.write(sep.join(map(str, self.parameters)))
        file.write('\n')
