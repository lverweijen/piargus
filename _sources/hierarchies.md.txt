# Hierarchies #

Hierarchies are important for explanatory variables.
There are three types supported by PiArgus.

## FlatHierarchy ##

The `FlatHierarchy` is used by default if no hierarchy is specified.
All codes add up to a single total.

```python
import piargus as pa

datacol = ["A", "B", "C", "B", "A"]
hierarchy = pa.FlatHierarchy(total_code="Total")
```

This creates a simple structure where all values are aggregated into one total.

```{mermaid}
graph LR;
Total --> A;
Total --> B;
Total --> C;
```

## LevelHierarchy ##

A `LevelHierarchy` is used when the hierarchical relationships are encoded directly within the data.

```python
import piargus as pa

datacol = ["11123", "11234", "23456"]
hierarchy = pa.LevelHierarchy(levels=[2, 3], total_code="Total")
```

In this example, the first two digits represent a higher-level grouping,
and the next 3 digits represent a more detailed level within that group.

```{mermaid}
graph LR;
Total --> 11;
Total --> 23;
11 --> 123;
11 --> 234;
23 --> 456;
```

## TreeHierarchy ##

A `TreeHierarchy` is used for complex hierarchies, typically stored in `.hrc` files.

```python
import piargus as pa

datacol = ["PV20", "PV21", "PV22"]
hierarchy = pa.TreeHierarchy.from_hrc("provinces.hrc", total_code="NL01")
```

These hierarchies have a tree-like structure.

```{mermaid}
graph LR;
NL01 --> LD01;
NL01 --> LD02;
LD01 --> PV20;
LD01 --> PV21;
LD02 --> PV22;
```

### Creating a TreeHierarchy programmatically

You can also create a TreeHierarchy programmatically, without relying on an external `.hrc` file.

```python
import piargus as pa

hierarchy = pa.TreeHierarchy(total_code="NL01")
hierarchy.create_node(["LD01", "PV20"])
hierarchy.create_node(["LD01", "PV21"])
hierarchy.create_node(["LD02", "PV22"])
hierarchy.to_hrc('provinces.hrc')
```

## Attaching a hierarchy to inputdata

To apply a hierarchy to your data, simply pass the hierarchy as part of the 
`MicroData` or `TableData` constructor:

```python
import piargus as pa

pa.MicroData(data_df, ...,
             hierarchies = {"region": region_hierarchy})
```

This will apply the specified `region_hierarchy` to the `region` column in your data.
