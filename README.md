# PiArgus

This package provides a python wrapper around [τ-ARGUS](https://research.cbs.nl/casc/tau.htm), a program to protect statistical tables.
This package takes care of generating all the required metadata and runs τ-ARGUS in the background to do the heavy work.

For this package to work, it is required to install τ-ARGUS locally first.
It's also recommended to read the [TauArgus manual](https://research.cbs.nl/casc/Software/TauManualV4.1.pdf) to understand how it should be used.

## Features

- Generate output tables from microdata or tabledata. It is recommended to generate from microdata.
- Metadata can be generated automatically, although using an existing rda-file is also possible.
- It's possible to create hierarchies, codelists, apriori files, recode files all from code or from existing files.
- Basic error checking of input is done before input is supplied to argus.

Feel free to [contribute](https://github.com/lverweijen/piargus) for other TauArgus-features.
[Feedback](https://github.com/lverweijen/piargus/issues) is welcome too.

## Installing

- Download and install the latest version of [τ-ARGUS](https://github.com/sdcTools/tauargus/releases).
- Then use [pip](https://pip.pypa.io/en/stable/getting-started/) to install piargus:

```sh
$ pip install --upgrade piargus
```

## Example

```python
import pandas as pd
import piargus as pa

tau = pa.TauArgus(r'C:\Users\User\Programs\TauArgus4.2.0b5\TauArgus.exe')
input_df = pd.read_csv('data/microdata.csv')
input_data = pa.MicroData(input_df)
output_table = pa.Table(['sbi', 'regio'], 'income', safety_rule="P(10)")

job = pa.Job(input_data, [output_table], directory='tau')
report = tau.run(job)
table_result = output_table.load_result()

print(report)
print(table_result)
```

Change `C:\Users\User\Programs\TauArgus4.2.0b5\TauArgus.exe` to the location where argus is installed.
See [tutorial](https://github.com/lverweijen/tree/main/tutorial.md) for a general introduction.
See [Examples](https://github.com/lverweijen/tree/main/examples) for more examples.

## See also

The following packages in R offer similar functionality:

- https://github.com/sdcTools/sdcTable
- https://github.com/InseeFrLab/rtauargus
