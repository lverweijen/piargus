import io
import operator
import os
from pathlib import Path
from typing import Mapping, Sequence, Tuple, Iterable, Optional

import littletree
from littletree.exporters import DotExporter, StringExporter
from littletree.serializers import RowSerializer

from .hierarchy import Hierarchy, DEFAULT_TOTAL_CODE
from .hrcserializer import HRCSerializer


class TreeHierarchy(Hierarchy):
    """A hierarchy where the codes are built as a tree."""

    __slots__ = "root", "indent", "filepath", "_code_length"

    is_hierarchical = True

    def __init__(self, tree=None, *, total_code: str = DEFAULT_TOTAL_CODE, indent='@'):
        if not isinstance(tree, TreeHierarchyNode):
            tree = TreeHierarchyNode(total_code, tree)
        self.root = tree
        self.indent = indent
        self.filepath = None
        self._code_length = None

    def __repr__(self):
        return (f"{self.__class__.__name__}({list(self.root.children)}, "
                f"total_code={self.total_code!r}, indent={self.indent!r})")

    def __str__(self) -> Optional[str]:
        return self.to_string(style="ascii")

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

    def get_node(self, path) -> Optional["TreeHierarchyNode"]:
        """Return single Node, None if it doesn't exist, ValueError if path not unique."""
        return self.root.path.get(path)

    def create_node(self, path) -> "TreeHierarchyNode":
        """Return single Node, None if it doesn't exist, ValueError if path not unique."""
        return self.root.path.create(path)

    @property
    def code_length(self) -> int:
        if self._code_length is None:
            codes = [descendant.code for descendant in self.root.iter_descendants()]
            self._code_length = max(map(len, codes))
        return self._code_length

    @code_length.setter
    def code_length(self, value):
        self._code_length = value

    @code_length.deleter
    def code_length(self):
        self._code_length = None

    @classmethod
    def from_hrc(cls, file, indent='@', total_code=DEFAULT_TOTAL_CODE):
        if isinstance(file, (str, Path)):
            with open(file) as reader:
                hierarchy = cls.from_hrc(reader, indent, total_code)
                hierarchy.filepath = Path(file)
                return hierarchy
        serializer = HRCSerializer(TreeHierarchyNode, indent)
        root = serializer.from_hrc(file)
        root.code = total_code
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
            serializer = HRCSerializer(TreeHierarchyNode, self.indent, length)
            return serializer.to_hrc(self.root, file)

    @classmethod
    def from_rows(cls, rows: Iterable[Tuple[str, str]], indent='@', total_code=DEFAULT_TOTAL_CODE):
        """Construct from list of (code, parent) tuples."""

        if hasattr(rows, "itertuples"):
            rows = rows.itertuples(index=False)
        serializer = RowSerializer(TreeHierarchyNode, path_name=None)
        tree = serializer.from_rows(rows)
        tree.code = total_code
        return cls(tree, indent=indent)

    def to_rows(self) -> Iterable[Tuple[str, str]]:
        serializer = RowSerializer(TreeHierarchyNode, path_name=None)
        return serializer.to_rows(self.root, leaves_only=True)

    def to_image(self, filename=None, **kwargs):
        exporter = DotExporter(name_factory=lambda n: hex(id(n)),
                               node_attributes={"label": operator.attrgetter("code")},
                               **kwargs)
        return exporter.to_image(self.root, filename)

    def to_string(self, str_factory="code", **kwargs) -> Optional[str]:
        exporter = StringExporter(str_factory, **kwargs)
        return exporter.to_string(self.root)


class TreeHierarchyNode(littletree.BaseNode):
    __slots__ = ()

    def __init__(self, code=None, children=(), parent=None):
        if code is None:
            code = DEFAULT_TOTAL_CODE
        if isinstance(children, Mapping):
            children = [TreeHierarchyNode(code=k, children=v) for k, v in children.items()]
        elif isinstance(children, Sequence):
            children = [child if isinstance(child, TreeHierarchyNode) else TreeHierarchyNode(child)
                        for child in children]
        super().__init__(identifier=code, children=children, parent=parent)

    @property
    def code(self):
        return self.identifier

    @code.setter
    def code(self, new_code):
        self.identifier = new_code

    def __repr__(self):
        if self.is_leaf:
            return f"Node({self.code!r})"
        else:
            return f"Node({self.code, list(self.children)})"

    def __str__(self):
        return self.code


# Alias for easier use
Node = TreeHierarchyNode
