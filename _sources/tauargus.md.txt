# TauArgus

The `TauArgus` class wraps the `tauargus.exe` program.
You can either add the directory containing `tauargus.exe` to your `PATH` environment variable or pass the executable’s location as follows:

```python
import piargus as pa

tau = pa.TauArgus(r"C:\\path\to\argus.exe")
```

To test the setup:

```python
print("Tau:", tau.version_info())
```

## Running jobs

If you have created a job, it can be run as follows:

```python
job = pa.Job(...)
tau.run(job)
```

Multiple jobs can be run at the same time by passing them as a list:

```python
tau.run([job1, job2, ...])
```

## Running batch files

If you have created a batch file, it can be run as follows:

```python
tau.run("myjob.arb")
```

To simplify the creation of batch files, `BatchWriter` may be used.

```python
with open("myjob.arb", "w") as output_file:
    batch_writer = pa.BatchWriter(output_file)
    
    batch_writer.open_microdata("microdata.csv")
    batch_writer.open_metadata("metadata.rda")
    batch_writer.specify_table(["explanator1", "explanatory2"], "response")
    batch_writer.safety_rule(individual="NK(3, 70)")
    batch_writer.read_microdata()
    batch_writer.suppress("MOD")
    batch_writer.write_table(1, 2, "AS+", "protected.csv")
```
