# Result analysis #

## Working directory

The job can accept a `directory` argument.
When provided, all temporary files and output tables will be created and stored in the specified location.
After the job completes, this directory can be inspected for further analysis.

```python
import piargus as pa

job = pa.Job(directory="argus_workdir")
```

If no directory is provided, a temporary directory will be created automatically.
This directory will be cleaned up once the job is finished.

## Report

When tau argus is run, it returns a result that can be printed.
It will display all output written to the logbook.

```python
import piargus as pa

tau = pa.TauArgus()
report = tau.run(job)
print(job)
```

## Table result

The resulting tables can be obtained from the specification `Table`.

```python
import piargus as pa

table_spec = pa.Table(...)

job = pa.Job(inputdata, [table_spec])

try:
    tau.run(job)
except pa.TauArgusException as err:
    print("An error occurred:")
    print(err.result)
else:
    print("Job completed succesfully")
    table_result = table_spec.load_result()
```

### TableResult methods

The `TableResult` object provides three key methods:

```python
table_result.safe()
table_result.status()
table_result.unsafe(unsafe_marker='X')
```

Each of these methods returns a Pandas [Series](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html).
The index is a multi-index containing the explanatory variables.
You can reshape the result into a preferred format using Pandas methods like `stack`, `unstack`, and `swaplevel`.

#### `unsafe()`

This returns the aggregated data in unprotected form.

#### `safe(unsafe_marker='X')`

This returns the aggregated data in its protected form.
Unsafe cells are marked by a special value, with `X` as the default marker.
Since this converts the resulting `pd.Series` to a string data type, you can pass `pd.NA` or a dummy value to keep the result in a numeric format.

#### `status()`

This method returns the safety status for each observation as a `pd.Series`.

The following status codes are used:

| Code | Meaning          |
|------|------------------|
| S    | Safe             |
| P    | Protected        |
| U    | Primary unsafe   |
| M    | Secondary unsafe |
| Z    | Empty            |
