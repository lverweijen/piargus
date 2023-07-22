"""
Helper functions which one day might be added to anytree itself.
"""

import re
from typing import Iterable, Tuple

import itertree


def from_indented(file, indent=' ', node_factory=itertree.iTree, root_name="root"):
    # Each line consists of indent and code
    pattern = re.compile(rf"^(?P<prefix>({re.escape(indent)})*)(?P<code>.*)")

    root = node_factory(root_name)
    stack = [root]

    for line in file:
        match = pattern.match(line)
        prefix, code = match['prefix'], match['code']
        depth = len(prefix) // len(indent)
        node = node_factory(code)
        stack[depth].append(node)

        # Place node as last item on index depth + 1
        del stack[depth + 1:]
        stack.append(node)

    return root


def to_indented(root, file, indent=" ", depth=0, str_factory=str):
    for child in root:
        file.write(indent * depth + str_factory(child) + '\n')
        to_indented(child, file, indent=indent, str_factory=str_factory, depth=depth + 1)


def from_rows(rows: Iterable[Tuple], node_factory=itertree.iTree, root_name="root"):
    # Special-case pandas dataframe
    if hasattr(rows, "itertuples"):
        rows = rows.itertuples(index=False)

    created_nodes = {}

    root = node_factory(root_name)
    for row in rows:
        parent_node = root
        for depth, col in enumerate(row):
            if (depth, col) in created_nodes:
                node = created_nodes[depth, col]
            else:
                node = node_factory(col)
                parent_node.append(node)
                created_nodes[depth, col] = node

            parent_node = node

    return root


def to_rows(root: itertree.iTree) -> Iterable[Tuple]:
    for node in root.deep:
        if not len(node):
            yield tuple(tag for (tag, _idx) in node.tag_idx_path)
