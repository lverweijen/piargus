# Apriori

Apriori files can be used to control how TauArgus suppresses cells.
These files can mark individual cells as protected, safe, or modify the suppression cost.

## Use an existing file

```python
import piargus as pa

apriori = pa.Apriori.from_hst("apriori.hst")
```

## Create an apriori file programmatically

```python
import piargus as pa

apriori = pa.Apriori(expand_trivial=True)
apriori.set_status(['A', 'ExampleDam'], pa.SAFE)
apriori.set_status(['A', 'ExampleCity'], pa.SAFE)
apriori.set_cost(['C', 'ExampleDam'], 10)
apriori.set_protection_level(['C', 'ExampleCity'], 5)

apriori.to_hist("apriori.hst")
```

## Attaching apriori to a table

Simply pass it as a parameter when creating a `Table` or `TableData` instance:

```python
table = pa.Table(['symbol', 'regio'], 'income', ...,
                 apriori=apriori)
```
