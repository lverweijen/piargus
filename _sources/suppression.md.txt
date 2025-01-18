# Safety methods and suppression #

Tau argus performs two kinds of suppression:

1. Primary suppression suppresses cells that violate safety rules.
2. Secondary suppression suppresses cells to protect other cells.

## Safety rules ##

Cells directly violating one of these rules are protected during primary suppression.

| Rule                    | Meaning                           |
|-------------------------|-----------------------------------|
| pa.percent_rule(p, n)   | $p%$-rule                         |
| pa.dominance_rule(n, k) | $N,K$ dominance rule              |
| pa.frequency_rule(n)    | Every cell needs $n$ contributors |

## Suppression methods ##

Methods for secondary suppression aim to minimize the suppression cost while protecting the data.

| Method       | Description                                       | Optimality | Speed  |  
|--------------|---------------------------------------------------|------------|--------|
| `pa.OPTIMAL` | Minimizes suppression costs (slowest)             | High       | Slow   |
| `pa.MOD`     | Protects sub-tables first and combines the result | Medium     | Medium |
| `pa.GH`      | Hypercube method                                  | Low        | Fast   |

## Specifying rules ##

Safety rules can be set for individual observations.
If some of the observations belong to the same unit, a safety rule can also be set on a holding-level.
In that case the microdata should have a `holding`-column.
If there is no holding information, safety rules can only be set on an individual level (per cell).
Suppression methods are also be set per table.

```python
import piargus as pa

table = pa.Table(response, explanatory, ...,
                 safety_rule={"individual": pa.percent_rule(20),
                              "holding": pa.percent_rule(30)},
                 suppress_method=pa.MODULAR)
```

If there are multiple linked tables, a safety rule can also be set on a job:

```python
job = pa.Job(tables, ...,
             linked_suppress_method=pa.MODULAR)
```

## Disclaimer

For a more official and theoretical explanation of suppression in argus, please consult the [tau-manual](https://research.cbs.nl/casc/Software/TauManualV4.1.pdf).
This page is meant as a practical overview, but is not authoritative.
