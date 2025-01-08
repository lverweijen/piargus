# Tutorial

Make sure to install piargus and pandas (dependency).
If you have both installed, make sure to import them:

```python
import pandas as pd
import piargus as pa
```

## Loading data

You should initially get your data in the form of a pandas dataframe.
The easiest way to do this is by `pd.read_csv()`.

```python
input_df = pd.read_csv('dataset.csv')
print(input_df)  # To see if it looks correct.
```
Consult the [pandas reference](https://pandas.pydata.org/docs/reference/io.html) for more options.

It's possible to work on microdata or tabledata.
Depending on your choice, continue in the appropriate section below.

## Starting from microdata

First convert `input_df` to a microdata-object:
```python
input_data = pa.MicroData(input_df)
```

If one of more of the columns is hierarchical, it is important to specify this.
In this example, it is assumed regio is hierarchical and its hierarchy is stored in a file "regio.hrc".
Depending on your data, there can also be other considerations that you may need to apply.

```python
regio_hierarchy = pa.TreeHierarchy.load_hrc("regio.hrc")

input_data = pa.MicroData(
    input_df,
    hierarchies={"regio": regio_hierarchy},
)
```

Now, we want to set up a table to generate.
We want the table to use `sbi` and `regio` as independent variables and `income` as response variable.
As primary suppression we will use the [p%-rule](https://link.springer.com/chapter/10.1007/978-3-642-33627-0_1).
For secondary suppression, we will use `optimal`.
This algorithm is generally slow for bigger datasets, but minimizes the suppression cost when the data is small.
By default the suppression cost is the sum of the values, but this can be configured by a parameter `cost`.

```python
output_table = pa.Table(explanatory=['sbi', 'regio'],
                        reponse='income',
                        safety_rule="P(10)",
                        suppression_method=pa.OPTIMAL)
```

Now we can set up a job and run the problem:
```python
tau = pa.TauArgus(r'<Insert path to argus.exe here>')
job = pa.Job(input_data, [output_table], directory='tau', name="my-microdata")
report = tau.run(job)
table_result = output_table.load_result()

print(report)
print(table_result)

table_result.dataframe().to_csv('output/microdata_result.csv')
```

And we're mostly done.
Output will look something like this:

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

The status can be interpreted as follows:

| Status | Meaning                         |
|--------|---------------------------------|
| S      | Safe                            |
| P      | Protected                       |
| U      | Unsafe by primary suppression   |
| M      | Unsafe by secondary suppression |
| Z      | Empty cell                      |

So nearly everything but the total has been suppressed.

## Starting from tabular data

First convert `input_df` to a tabledata-object:
```python
input_data = pa.TableData(
    input_df,
    explanatory=["activity", "size"],
    reponse="value",
    safety_rule="P(10)",
    suppression_method=pa.OPTIMAL,
)
```

The additional parameters to TableData are the same as those to Table when supplying microdata.
More parameters can be set:

| Parameter          | Meaning                                         | Example                   |
|--------------------|-------------------------------------------------|---------------------------|
| `total_codes`      | Total code for each explanatory variable.       | `{"regio": "US"}`         |
| `frequency`        | Column with number of contributors to response. | `"n_obs"`                 |
| `top_contributors` | Columns with top contributors.                  | `["max", "max2", "max3"]` |

Now to run this:

```python
job = pa.Job(table, directory='tau', name='my-table-data')
result = tau.run(job)
table_result = table.load_result()

print(result)
print(table_result)
table_result.dataframe().to_csv('output/tabledata_result.csv')
```
