# Hierarchies #

For explanatory variables, it is recommended to supply a hierarchy.
There are 3 kinds of hierarchy supported by PiArgus.

## FlatHierarchy ##

This is the default if no hierarchy is supplied.
All labels are of the same level with a single total.

```python
import piargus as pa

datacol = ["A", "B", "C", "B", "A"]
hierarchy = pa.FlatHierarchy(total_code="Total")
```

```{mermaid}
graph LR;
Total --> A;
Total --> B;
Total --> C;
```

## LevelHierarchy ##

A level hierarchy is useful when the hierarchy is encoded within the code itself.

```python
import piargus as pa

datacol = ["11123", "11234", "23456"]
hierarchy = pa.LevelHierarchy(levels=[2, 3], total_code="Total")
```

```{mermaid}
graph LR;
Total --> 11;
Total --> 23;
11 --> 123;
11 --> 234;
23 --> 456;
```

## TreeHierarchy ##

For complex hierarchies, a TreeHierarchy can be used.
These are typically stored in a hrc-file.

```python
import piargus as pa

datacol = ["PV20", "PV21", "PV22"]
hierarchy = pa.TreeHierarchy.from_hrc("provinces.hrc", total_code="NL01")
```

```{mermaid}
graph LR;
NL01 --> LD01;
NL01 --> LD02;
LD01 --> PV20;
LD01 --> PV21;
LD02 --> PV22;
```

The file provinces.hrc may look like this:
```hrc
LD01
@PV20
@PV21
LD02
@PV22
```

It can also be created programmatically:
```python
import piargus as pa

hierarchy = pa.TreeHierarchy(total_code="NL01")
hierarchy.create_node(["NL01", "LD01", "PV20"])
hierarchy.create_node(["NL01", "LD01", "PV21"])
hierarchy.create_node(["NL01", "LD02", "PV22"])
hierarchy.to_hrc('provinces.hrc')
```
