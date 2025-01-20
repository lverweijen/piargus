import os
from pathlib import Path
from typing import Sequence

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
    def _create_child_object(cls, value):
        """
        Create either CodeHierarchy or ThreeHierarchy.

        It's usually better to create one of those directly.
        """
        # Prevent circular imports
        from .levelhierarchy import LevelHierarchy
        from .flathierarchy import FlatHierarchy
        from .treehierarchy import TreeHierarchy

        if not value:
            hierarchy = FlatHierarchy()
        elif isinstance(value, Hierarchy):
            hierarchy = value
        elif isinstance(value, Sequence):
            hierarchy = LevelHierarchy(value)
        elif isinstance(value, os.PathLike):
            path = Path(value)
            if path.suffix == ".hrc":
                hierarchy = TreeHierarchy.from_hrc(path)
            else:
                raise ValueError("hierarchy path should end in .hrc")
        else:
            raise TypeError("Should be passed a Hierarchy.")

        return hierarchy
