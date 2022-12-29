# PiArgus

This package provides a python wrapper around [τ-ARGUS](https://research.cbs.nl/casc/tau.htm), a program that is commonly used to protect statistical tables.
This package takes care of generating all the required metadata and runs the TauArgus program in the background to do the heavy work.

## Features

- Generate tables from microdata or tabledata.
- Automatically generate metadata from inputdata or load an existing one using `Metadata.from_rda('data.rda')`.
- Codelists and hierarchies.

Not all features have been extensively tested yet. [Feedback](https://github.com/lverweijen/piargus/issues) is welcome.
For now generating tables from microdata (over tabledata) is recommended.

## Wishlist

Other TauArgus features not yet supported but useful to someone.

## Example

```python
import pandas as pd
import piargus as pa

tau = pa.TauArgus(r'C:\Users\User\Programs\TauArgus4.2.0b5\TauArgus')
input_df = pd.read_csv('data/microdata.csv')
input_data = pa.MicroData(input_df, name='example')
tables = [pa.Table(['sbi', 'regio'], 'income', name='T1',
                   safety_rules={'NK(3,70)', 'FREQ(3,20)', 'ZERO(20)'},
                   suppress_method='OPT')]

job = pa.Job(input_data, tables, directory='tau', name='example')
report = tau.run(job)
table_result = tables[0].load_result()

print(report)
print(table_result)
```

See [Examples](examples) for more examples.

## See also

The following packages in R offer similar functionality:

- https://github.com/sdcTools/sdcTable
- https://github.com/InseeFrLab/rtauargus
