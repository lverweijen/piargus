from .hierarchy import Hierarchy, DEFAULT_TOTAL_CODE


class LevelHierarchy(Hierarchy):
    """
    Hierarchical code consisting of digits.

    Can be used if the digits of the code make the hierarchy.
    For each hierarchical level the width in the code should be given.
    For example [1, 2, 1] means the code has format "x.yy.z".
    """
    __slots__ = "levels", "total_code"

    is_hierarchical = True

    def __init__(self, levels, *, total_code: str = DEFAULT_TOTAL_CODE):
        """Create a tree hierarchy."""
        self.levels = [int(level) for level in levels]
        self.total_code = total_code

    def __repr__(self):
        return f"{self.__class__.__name__}({self.levels}, total_code={self.total_code})"

    @property
    def code_length(self) -> int:
        return sum(self.levels)
