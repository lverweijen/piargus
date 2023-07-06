class HierarchyCode:
    """Hierarchical code consisting of digits."""
    def __init__(self, levels, total_code='Total'):
        self._levels = [int(level) for level in levels]
        self.total_code = total_code

    def column_length(self) -> int:
        return sum(self)

    def __iter__(self):
        return iter(self._levels)

    def __len__(self):
        return len(self._levels)
