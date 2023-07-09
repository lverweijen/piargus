from typing import Sequence

DEFAULT_TOTAL_CODE = "Total"


class Hierarchy:
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        if cls is Hierarchy:
            return cls._create_child_object(*args, **kwargs)
        else:
            return super().__new__(cls)

    @classmethod
    def _create_child_object(cls, hierarchy, total_code=DEFAULT_TOTAL_CODE):
        """
        Create either CodeHierarchy or ThreeHierarchy.

        It's usually better to create one of those directly.
        """
        # Prevent circular imports
        from .codehierarchy import CodeHierarchy
        from .treehierarchy import TreeHierarchy

        if isinstance(hierarchy, Hierarchy):
            return hierarchy
        elif isinstance(hierarchy, Sequence) and all(isinstance(x, int) for x in hierarchy):
            return CodeHierarchy(hierarchy, total_code=total_code)
        else:
            return TreeHierarchy(hierarchy, total_code=total_code)

    def column_length(self) -> int:
        raise NotImplementedError
