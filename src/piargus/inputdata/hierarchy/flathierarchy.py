from .hierarchy import DEFAULT_TOTAL_CODE, Hierarchy


class FlatHierarchy(Hierarchy):
    __slots__ = "total_code"

    is_hierarchical = False

    def __init__(self, *, total_code=DEFAULT_TOTAL_CODE):
        self.total_code = total_code

    def __repr__(self):
        return f"{self.__class__.__name__}(total_code={self.total_code})"
