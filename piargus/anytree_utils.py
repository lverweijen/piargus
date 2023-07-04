"""
Helper functions which one day might be added to anytree itself.
"""

import re

import anytree


def from_indented(file, indent=' ', node_factory=anytree.Node, root_name="root"):
    # Each line consists of indent and code
    pattern = re.compile(rf"^(?P<prefix>({re.escape(indent)})*)(?P<code>.*)")

    root = node_factory(root_name)
    stack = [root]

    for line in file:
        match = pattern.match(line)
        prefix, code = match['prefix'], match['code']
        depth = len(prefix) // len(indent)
        node = node_factory(code)
        node.parent = stack[depth]

        # Place node as last item on index depth + 1
        del stack[depth + 1:]
        stack.append(node)

    return root


def to_indented(root, file, indent=" ", depth=0, str_factory=str):
    for child in root.children:
        file.write(indent * depth + str_factory(child) + '\n')
        to_indented(child, file, indent=indent, str_factory=str_factory, depth=depth + 1)


def from_rows(rows, node_factory=anytree.Node, root_name="root"):
    created_nodes = {}

    root = node_factory(root_name)
    for row in rows:
        parent_node = root
        for depth, col in enumerate(row):
            if (depth, col) in created_nodes:
                node = created_nodes[depth, col]
            else:
                node = node_factory(col)
                node.parent = parent_node
                created_nodes[depth, col] = node

            parent_node = node

    return root


def to_rows(root, str_factory=str, skip_root=True):
    index = 1 if skip_root else 0
    for leaf in root.leaves:
        yield [str_factory(node) for node in leaf.path[index:]]
