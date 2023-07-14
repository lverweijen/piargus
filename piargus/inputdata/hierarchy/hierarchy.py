from typing import Sequence, Optional

DEFAULT_TOTAL_CODE = "Total"


class Hierarchy:
    __slots__ = ()

    is_hierarchical: bool = None
    total_code: str

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
        from .levelhierarchy import LevelHierarchy
        from .flathierarchy import FlatHierarchy
        from .treehierarchy import TreeHierarchy

        if isinstance(hierarchy, Hierarchy):
            return hierarchy
        elif hierarchy is None:
            return FlatHierarchy(total_code=total_code)
        elif isinstance(hierarchy, Sequence) and all(isinstance(x, int) for x in hierarchy):
            return LevelHierarchy(hierarchy, total_code=total_code)
        else:
            return TreeHierarchy(hierarchy, total_code=total_code)

    @property
    def code_length(self) -> Optional[int]:
        raise NotImplementedError
