import re


class HRCSerializer:
    def __init__(self, node_factory, indent='@', length=0):
        self.node_factory = node_factory
        self.indent = indent
        self.length = length

    def from_hrc(self, file, root=None):
        pattern = re.compile(rf"^(?P<prefix>({re.escape(self.indent)})*)(?P<code>.*)")

        if root is None:
            root = self.node_factory()
        stack = [root]

        for line in file:
            match = pattern.match(line)
            prefix, code = match['prefix'], match['code']
            depth = len(prefix) // len(self.indent)
            node = stack[depth][code] = self.node_factory()

            # Place node as last item on index depth + 1
            del stack[depth + 1:]
            stack.append(node)

        return root

    def to_hrc(self, root, file):
        indent, length = self.indent, self.length
        for node, item in root.iter_descendants(with_item=True):
            file.write((item.depth - 1) * indent + str(node.identifier).rjust(length) + "\n")
