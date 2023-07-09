from .hierarchy import Hierarchy, DEFAULT_TOTAL_CODE


class CodeHierarchy(Hierarchy):
    """
    Hierarchical code consisting of digits.

    Can be used if the digits of the code make the hierarchy.
    For each hierarchical level the width in the code should be given.
    For example [3, 4, 1] means the code has format "xxxyyyyz".
    """
    __slots__ = "levels", "total_code"

    def __init__(self, levels, total_code=DEFAULT_TOTAL_CODE):
        self.levels = [int(level) for level in levels]
        self.total_code = total_code

    def column_length(self) -> int:
        return sum(self.levels)
