import os
from collections.abc import Mapping, Sequence
from os import PathLike
from typing import Any, Optional, TextIO

import numpy as np
import pandas as pd

from piargus import Hierarchy, TreeHierarchy

from abstracttree import MaxDepth

__all__ = ["recode", "read_grc"]


def recode(
    data: pd.Series,
    recoder: Sequence | Mapping[Any, Sequence | slice] | int | os.PathLike,
    hierarchy: Optional[Hierarchy] = None,
) -> pd.Series:
    """Recode a pandas Series.

    :param data: Data to be recoded
    :param recoder: How the data should be recoded.
        * {group1: codes, group2: codes}. This will make groups and each code will be give the group label.
            A group should be a sequence of codes or a sequence of slices to specify a range of codes.
        * level: int (requires hierarchy): Each code will be replaced by its ancestor at the given level.
        * [leaf1, leaf2]: int (requires hierarchy): Each code will be replaced by its nearest ancestor in the list given.
        * .GRC file: Data will be recoded according to the given .GRC file.
    :param hierarchy: Hierarchy of codes used in data if required by the recoder.
    :return: recoded data.
    """
    if isinstance(recoder, PathLike):
        recoder = read_grc(recoder)

    match recoder:
        case Mapping():
            return _recode_mapping(data, _preprocess_mapping(recoder))
        case Sequence() | int():
            if isinstance(hierarchy, TreeHierarchy):
                return _recode_tree(data, recoder, hierarchy)
            else:
                raise TypeError(f"This recorder requires a TreeHierarchy.")
        case _:
            raise TypeError(f"Unsupported recorder of type: {type(recoder)}")


def _recode_tree(data, recoder: Sequence | int, hierarchy: TreeHierarchy):
    if isinstance(recoder, int):
        mapping = _invert_tree_level(hierarchy, recoder)
    elif isinstance(recoder, Sequence):
        mapping = _invert_tree_leafs(hierarchy, recoder)
    else:
        raise TypeError("Unsupported hierarchy for recoding")

    return data.map(mapping)


def _preprocess_mapping(recoder: Mapping[Any, Sequence | slice]) -> Mapping[Any, Sequence[slice]]:
    result = {}
    for group, items in recoder.items():
        if isinstance(items, slice):
            items = [items]

        result[group] = [
            slice(item, item) if not isinstance(item, slice) else item for item in items
        ]
    return result


def _recode_mapping(data: pd.Series, recoder: Mapping[Any, Sequence[slice]]):
    criteria = []
    values = []

    for group, items in recoder.items():
        for interval in items:
            start = interval.start if interval.start is not None else data.min()
            stop = interval.stop if interval.stop is not None else data.max()
            criteria.append(data.between(start, stop))
            values.append(group)

    new_values = np.select(criteria, values, data)
    return pd.Series(new_values, index=data.index)


def _invert_tree_level(hierarchy: TreeHierarchy, level):
    mapping = {}
    for node, item in hierarchy.root.nodes.preorder(keep=MaxDepth(level)):
        if item.depth == level:
            for deeper_node in node.nodes:
                mapping[deeper_node.identifier] = node.identifier
    return mapping


def _invert_tree_leafs(hierarchy: TreeHierarchy, leafs):
    mapping = {leaf: leaf for leaf in leafs}
    for node, item in hierarchy.root.nodes.preorder():
        if node.identifier not in mapping:
            if parent := node.parent:
                if parent.identifier in mapping:
                    mapping[node.identifier] = mapping[parent.identifier]
    return mapping

def read_grc(path: os.PathLike | TextIO) -> Mapping[slice, str] | Sequence[str]:
    """Read a .GRC file and return its recoder."""
    if isinstance(path, PathLike):
        with open(path) as reader:
            lines = reader.readlines()
    else:
        lines = path.readlines()
    return _read_grc(lines)

def _read_grc(lines: Sequence[str]) -> Mapping[slice, str] | Sequence[str]:
    if lines[0].strip().upper() == "<TREERECODE>":
        lines.pop(0)
        return [line.rstrip() for line in lines]
    else:
        mapping = {}
        for line in lines:
            group, values = line.split(":")

            intervals = []
            for interval in values.split(","):
                parts = interval.split("-")
                if len(parts) == 1:
                    start, stop = interval, interval
                elif len(parts) == 2:
                    start, stop = parts
                else:
                    raise Exception(f"Interval can contain at most one '-': {interval!r}.")

                intervals.append(slice(start.strip(), stop.strip()))

            mapping[group.strip()] = intervals

        return mapping
