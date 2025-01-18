# Getting started

Ensure that piargus and TauArgus are installed.
If both are installed, you can start by importing piargus along with pandas:

```python
import pandas as pd
import piargus as pa
```

## Loading data

There are two primary ways to use piargus:
starting from **microdata** or **table data**.
In both cases, your data must be in the form of a pandas `Dataframe`.
If your data is stored in a CSV file, it can be loaded using `pd.read_csv()`.

```python
input_df = pd.read_csv('data.csv')
```

For more options to load data, consult the [pandas documentation](https://pandas.pydata.org/docs/reference/io.html).

## Starting from Microdata

First, convert your `input_df` into a microdata-object:

```python
input_data = pa.MicroData(input_df)
```

If any columns are hierarchical, specify them.
For example, if `regio` is hierarchical and its hierarchy is stored in a file `regio.hrc`,
you can load the hierarchy as follows:

```python
regio_hierarchy = pa.TreeHierarchy.load_hrc("regio.hrc")

input_data = pa.MicroData(
    input_df,
    hierarchies={"regio": regio_hierarchy},
)
```

### Setting up a Table

Set up a table with `sbi` and `regio` as explanatory variables and `income` as the response variable.
Use the [p%-rule](https://link.springer.com/chapter/10.1007/978-3-642-33627-0_1) as a safety rule and `OPTIMAL` as a method for secondary suppression:

```python
output_table = pa.Table(explanatory=['sbi', 'regio'],
                        reponse='income',
                        safety_rule="P(10)",
                        suppression_method=pa.OPTIMAL)
```

### Running the Job

To run the table generation job with `TauArgus`:

```python
tau = pa.TauArgus(r'<Insert path to argus.exe here>')
job = pa.Job(input_data, [output_table], directory='tau', name="my-microdata")
report = tau.run(job)
table_result = output_table.load_result()

print(report)
print(table_result)

table_result.dataframe().to_csv('output/microdata_result.csv')
```

The output will look like this:

```
<ArgusReport>
status: success <0>
batch_file: tau\basic-example.arb
workdir: tau\work\basic-example
logbook_file: tau\basic-example_logbook.txt
logbook:
        25-Aug-2023 16:49:24 : <OPENMICRODATA> "tau\input\basic-example_microdata.csv"
        25-Aug-2023 16:49:24 : <OPENMETADATA> "tau\input\basic-example_microdata.rda"
        25-Aug-2023 16:49:24 : <SPECIFYTABLE> "symbol""regio"|"income"||
        25-Aug-2023 16:49:24 : <SAFETYRULE> P(10, 1)
        25-Aug-2023 16:49:24 : <READMICRODATA>
        25-Aug-2023 16:49:24 : Start explore file: tau\input\basic-example_microdata.csv
        25-Aug-2023 16:49:24 : Start computing tables
        25-Aug-2023 16:49:24 : Table: symbol x regio | income has been specified
        25-Aug-2023 16:49:24 : Tables have been computed
        25-Aug-2023 16:49:24 : Micro data file read; processing time 0 seconds
        25-Aug-2023 16:49:24 : Tables from microdata have been read
        25-Aug-2023 16:49:24 : <SUPPRESS> OPT(1)
        25-Aug-2023 16:49:25 : End of Optimal protection. Time used 0 seconds
                               Number of suppressions: 4
        25-Aug-2023 16:49:25 : <WRITETABLE> (1, 2, AS+, "tau\output\basic-example_table-1.csv")
        25-Aug-2023 16:49:25 : Table: symbol x regio | income has been written
                               Output file name: tau\output\basic-example_table-1.csv
        25-Aug-2023 16:49:25 : End of TauArgus run

Response: income
                      safe status  unsafe
symbol regio
Total  Total        264.43      S  264.43
        ExampleDam       x      M  141.57
       ExampleCity       x      M  122.86
A      Total             x      M  142.59
        ExampleDam       x      U   93.13
       ExampleCity       x      U   49.46
C      Total             x      M  121.84
        ExampleDam       x      U   48.44
       ExampleCity       x      U   73.40
```

### Interpreting Status codes

| Status | Meaning                         |
|--------|---------------------------------|
| S      | Safe                            |
| P      | Protected                       |
| U      | Unsafe by primary suppression   |
| M      | Unsafe by secondary suppression |
| Z      | Empty cell                      |

## Starting from TableData

To work with tabular data, convert `input_df` into a `TableData` object:

```python
input_data = pa.TableData(
    input_df,
    explanatory=["activity", "size"],
    reponse="value",
    safety_rule="P(10)",
    suppression_method=pa.OPTIMAL,
)
```

You can also specify additional parameters to `TableData`:

| Parameter          | Meaning                                         | Example                   |
|--------------------|-------------------------------------------------|---------------------------|
| `total_codes`      | Total code for each explanatory variable.       | `{"regio": "US"}`         |
| `frequency`        | Column with number of contributors to response. | `"n_obs"`                 |
| `top_contributors` | Columns with top contributors.                  | `["max", "max2", "max3"]` |

To run the data protection job:

```python
job = pa.Job(table, directory='tau', name='my-table-data')
result = tau.run(job)
table_result = table.load_result()

print(result)
print(table_result)
table_result.dataframe().to_csv('output/tabledata_result.csv')
```
