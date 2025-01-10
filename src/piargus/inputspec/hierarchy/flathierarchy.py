from .hierarchy import DEFAULT_TOTAL_CODE, Hierarchy


class FlatHierarchy(Hierarchy):
    """
    Hierarchy where all nodes are the same level.

    This is used as a default when no hierarchy is specified.
    """
    __slots__ = "total_code"

    is_hierarchical = False

    def __init__(self, *, total_code=DEFAULT_TOTAL_CODE):
        """Create a FlatHierarchy."""
        self.total_code = total_code

    def __repr__(self):
        return f"{self.__class__.__name__}(total_code={self.total_code})"
