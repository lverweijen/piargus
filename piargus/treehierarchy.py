import io
import operator
import os
from pathlib import Path
from typing import Mapping, Sequence, Tuple, Iterable

import anytree

from .anytree_utils import from_indented, to_indented, from_rows, to_rows
from .hierarchy import Hierarchy, DEFAULT_TOTAL_CODE


class TreeHierarchy(Hierarchy):
    """Describe a hierarchy for use with TauArgus"""

    __slots__ = "root", "indent", "filepath"

    def __init__(self, tree=None, indent='@', total_code=DEFAULT_TOTAL_CODE):
        if not isinstance(tree, TreeHierarchyNode):
            tree = TreeHierarchyNode(total_code, data=tree)

        self.root = tree
        self.indent = indent
        self.filepath = None

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"{self.root}, indent={self.indent}, total_code={self.total_code})")

    def __str__(self):
        # Use ascii, so we are safe in environments that don't use utf8
        return anytree.RenderTree(self.root, style=anytree.AsciiStyle()).by_attr("code")

    def __eq__(self, other):
        return (self.root, self.indent) == (other.root, other.indent)

    def __hash__(self):
        raise TypeError

    @property
    def total_code(self) -> str:
        return self.root.code

    @total_code.setter
    def total_code(self, value):
        self.root.code = value

    def get_node(self, path=".") -> "TreeHierarchyNode":
        """Follow path to a new Node."""
        return TreeHierarchyNode.resolver.get(self.root, path)

    def column_length(self) -> int:
        codes = [descendant.code for descendant in self.root.descendants]
        return max(map(len, codes))

    @classmethod
    def from_hrc(cls, file, indent='@', total_code=DEFAULT_TOTAL_CODE):
        if isinstance(file, (str, Path)):
            with open(file) as reader:
                hierarchy = cls.from_hrc(reader, indent)
                hierarchy.filepath = Path(file)
                return hierarchy

        root = from_indented(file,
                             indent=indent, node_factory=TreeHierarchyNode, root_name=total_code)
        return cls(root, indent=indent)

    def to_hrc(self, file=None, length=0):
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self.to_hrc(file, length)
            return file.getvalue()
        elif not hasattr(file, 'write'):
            self.filepath = Path(file)
            with open(file, 'w', newline='\n') as writer:
                self.to_hrc(writer, length)
        else:
            return to_indented(self.root, file, self.indent,
                               str_factory=lambda node: str(node.code).rjust(length))

    @classmethod
    def from_rows(cls, rows: Iterable[Tuple[str, str]], indent='@', total_code=DEFAULT_TOTAL_CODE):
        """Construct from list of (code, parent) tuples."""
        return cls(from_rows(rows, TreeHierarchyNode, root_name=total_code), indent=indent)

    def to_rows(self) -> Iterable[Tuple[str, str]]:
        return to_rows(self.root, operator.attrgetter("code"), skip_root=True)


class TreeHierarchyNode(anytree.NodeMixin):
    __slots__ = "code"
    resolver = anytree.Resolver("code")

    def __init__(self, code=DEFAULT_TOTAL_CODE, data=None, children=()):
        self.code = code

        if data is None:
            self.children = children
        elif isinstance(data, Mapping):
            self.children = [TreeHierarchyNode(code=k, data=v) for k, v in data.items()]
        elif isinstance(data, Sequence):
            self.children = [TreeHierarchyNode(e) for e in data]
        else:
            raise TypeError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.code})"

    def __eq__(self, other):
        return self.code == other.code and self.children == other.children

    def to_dict(self):
        return {child.code: child.to_dict() for child in self.children}
