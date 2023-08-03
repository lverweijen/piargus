import io
import os
from pathlib import Path
from typing import Mapping, Sequence, Tuple, Iterable, Optional

import itertree

from .hierarchy import Hierarchy, DEFAULT_TOTAL_CODE
from .itertree_utils import from_indented, to_indented, from_rows, to_rows


class TreeHierarchy(Hierarchy):
    """A hierarchy where the codes are built as a tree."""

    __slots__ = "root", "indent", "filepath", "_code_length"

    is_hierarchical = True

    def __init__(self, tree=None, *, total_code: str = DEFAULT_TOTAL_CODE, indent='@'):
        if not isinstance(tree, itertree.iTree):
            tree = TreeHierarchyNode(total_code, tree)

        self.root = tree
        self.indent = indent
        self.filepath = None
        self._code_length = None

    def __repr__(self):
        return (f"{self.__class__.__name__}({list(self.root)}, "
                f"total_code={self.total_code!r}, indent={self.indent!r})")

    def __str__(self):
        # Use ascii, so we are safe in environments that don't use utf8
        # return anytree.RenderTree(self.root, style=anytree.AsciiStyle()).by_attr("code")
        return self.root.renders()

    def __eq__(self, other):
        return (self.root, self.indent) == (other.root, other.indent)

    def __hash__(self):
        raise TypeError

    @property
    def total_code(self) -> str:
        return self.root.code

    @total_code.setter
    def total_code(self, value):
        self.root.rename(value)

    def get_node(self, *path) -> Optional[itertree.iTree]:
        """Return single Node, None if it doesn't exist, ValueError if path not unique."""
        if path:
            try:
                return self.root.get.single(*path)
            except (IndexError, KeyError):
                return None
        else:
            return self.root

    def create_node(self, *path) -> itertree.iTree:
        """Recursively create a path to a Node or return an existing node."""
        node = self.root

        path = iter(path)

        for segment in path:
            try:
                node = node.get.by_tag_idx((segment, 0))
            except KeyError:
                node = node.append(TreeHierarchyNode(segment))

                for new_segment in path:
                    node = node.append(TreeHierarchyNode(new_segment))
                break

        return node

    @property
    def code_length(self) -> int:
        if self._code_length is None:
            codes = [descendant.code for descendant in self.root.deep]
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
        return to_rows(self.root)


class TreeHierarchyNode(itertree.iTree):
    __slots__ = ()

    @classmethod
    def _to_tree(cls, tree) -> "TreeHierarchyNode":
        if isinstance(tree, cls):
            return tree
        elif isinstance(tree, itertree.iTree):
            return cls(tree.tag, iter(tree))
        elif isinstance(tree, str):
            return cls(tree)
        else:
            raise TypeError(f"Unexpected type {type(tree)}")

    def __init__(self, code=DEFAULT_TOTAL_CODE, children=()):
        if isinstance(children, Mapping):
            children = [TreeHierarchyNode(code=k, children=v) for k, v in children.items()]
        elif isinstance(children, Sequence):
            children = [self._to_tree(child) for child in children]

        super().__init__(tag=code, subtree=children)

    def __repr__(self):
        if len(self):
            return f"{self.__class__.__name__}({self.code, list(self)})"
        else:
            return f"{self.__class__.__name__}({self.code!r})"

    @property
    def code(self):
        return self.tag

    @property
    def is_leaf(self) -> bool:
        """Return if node is leaf. Equivalent to bool(node)."""
        return len(self) == 0

    # Did we overwrite them all?
    def append(self, item):
        return super().append(self._to_tree(item))

    def appendleft(self, item):
        return super().appendleft(self._to_tree(item))

    def insert(self, target, item):
        return super().insert(target, self._to_tree(item))

    def __setitem__(self, target, item):
        if isinstance(item, str):
            super()[target].rename(item)
        else:
            super()[target] = self._to_tree(item)
