# PyArgus

This package provides a python wrapper around [τ-ARGUS](https://research.cbs.nl/casc/tau.htm).
This is a program that can be used to protect statistical tables.
This package takes care of generating the required metadata and uses the TauArgus to protect its data.

## Features

- Generating tables from microdata
- Metadata
- Hierarchies
- Codelists

## Wishlist

- Generating tables from tabledata
- Apriori files

## Example

```python
import pandas as pd
import pyargus as pa

tau = pa.TauArgus(r'C:\Users\User\Programs\TauArgus4.2.0b5\TauArgus')
input_df = pd.read_csv('example/data/example.csv')
input_data = pa.MicroData(input_df, name='example')
input_data.safety_rules = {'NK(3,70)', 'FREQ(3,20)', 'ZERO(20)'}
tables = [pa.Table(['sbi', 'regio'], 'income', name='T2')]

job = pa.Job(input_data, tables, directory='example/tau', name='example')
tau_result = tau.run(job)
table_result = tables[0].load_result()

print(tau_result)
print(table_result)
```

Codelists and hierarchies can optionally be supplied to the constructor of MicroData.

## See also

The following packages in R offer similar functionality:

- https://github.com/sdcTools/sdcTable
- https://github.com/InseeFrLab/rtauargus
