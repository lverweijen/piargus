import io
import os
import re
from pathlib import Path
from typing import Mapping, Sequence, Hashable, Optional, Iterable


class Hierarchy:
    """Describe a hierarchy for use with TauArgus"""

    __slots__ = "tree", "indent", "filepath"

    def __init__(self, tree=None, indent='@'):
        if not isinstance(tree, Node):
            tree = Node(tree)

        self.tree = tree
        self.indent = indent
        self.filepath = None

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.tree, self.indent})"

    def __str__(self):
        return self.to_hrc()

    @classmethod
    def from_hrc(cls, file, indent='@'):
        if isinstance(file, (str, Path)):
            with open(file) as reader:
                hierarchy = cls.from_hrc(reader, indent)
                hierarchy.filepath = Path(file)
                return hierarchy

        # Each line consists of indent and code
        pattern = re.compile(rf"^(?P<prefix>({re.escape(indent)})*)(?P<code>.*)")

        root = Node()
        stack = [root]

        for line in file:
            match = pattern.match(line)
            prefix, code = match['prefix'], match['code']
            depth = len(prefix) // len(indent)
            parent_node = stack[depth]
            node = parent_node.add(code)

            # Place node as last item on index depth + 1
            del stack[depth + 1:]
            stack.append(node)

        return Hierarchy(root)

    def to_hrc(self, file=None, length=0):
        if file is None:
            file = io.StringIO(newline=os.linesep)
            self._node_to_hrc(self.tree, file, length)
            return file.getvalue()
        elif hasattr(file, 'write'):
            self._node_to_hrc(self.tree, file, length)
        else:
            self.filepath = Path(file)
            with open(file, 'w', newline='\n') as writer:
                self._node_to_hrc(self.tree, writer, length)

    def _node_to_hrc(self, node: "Node", file, length=0, depth=0):
        for key in node.children:
            file.write(self.indent * depth + str(key).rjust(length) + '\n')
            self._node_to_hrc(node.get(key), file, length, depth=depth + 1)


class Node:
    __slots__ = "_children"

    def __init__(self, children=None):
        if children is None:
            children = dict()
        elif isinstance(children, Mapping):
            children = {k: v if isinstance(v, Node) else Node(v)
                        for k, v in children.items()}
        elif isinstance(children, Sequence):
            children = {e: Node() for e in children}
        else:
            raise TypeError

        self._children = children

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.to_dict()})"

    def __eq__(self, other):
        if hasattr(other, 'to_dict'):
            other = other.to_dict()

        return self.to_dict() == other

    def __getitem__(self, item) -> "Node":
        return self._children[item]

    @property
    def children(self) -> Iterable[Hashable]:
        return self._children.keys()

    @property
    def is_leaf(self) -> bool:
        return not self._children

    def add(self, key: Hashable) -> "Node":
        if key not in self._children:
            self._children[key] = Node()

        return self._children[key]

    def get(self, key: Hashable) -> Optional["Node"]:
        return self._children.get(key)

    def remove(self, key: Hashable) -> Optional["Node"]:
        return self._children.pop(key)

    def add_path(self, path: Sequence[Hashable]) -> "Node":  # noqa
        node = self
        for child in path:
            node = node.add(child)
        return node

    def get_path(self, path: Sequence[Hashable]) -> "Node":  # noqa
        node = self
        for child in path:
            if node:
                node = node.get(child)

        return node

    def to_dict(self):
        return {key: value.to_dict() for key, value in self._children.items()}

    def iterate_codes(self, only_leaves=True) -> Iterable[Hashable]:
        for child in self.children:
            child_node = self.get(child)

            if child_node.is_leaf or not only_leaves:
                yield child
            yield from child_node.iterate_codes(only_leaves)

    def iterate_paths(self, only_leaves=True) -> Iterable[Sequence[Hashable]]:
        if self.is_leaf or not only_leaves:
            yield ()
        else:
            for child in self.children:
                for subpath in self.get(child).iterate_paths(only_leaves):
                    yield (child,) + subpath
