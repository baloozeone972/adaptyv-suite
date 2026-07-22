# adaptyv-kinetics

Adaptyv ships every binding customer a data package of raw sensorgrams, fitted
curves and QC metrics — and **no tool to read it**. This library reads the
package, re-fits the kinetics independently, flags artifacts, and produces a
report, in one command.

## Use

```bash
# No real package handy? Generate a schema-conformant synthetic one.
adaptyv-kinetics synth --out fake_package.zip

# One command: parse, re-fit, QC, and render a self-contained HTML report.
adaptyv-kinetics report fake_package.zip -o report.html

# Independent re-fit exported to CSV / Parquet / JSON.
adaptyv-kinetics refit fake_package.zip --out fits.csv

# QC verdicts; non-zero exit on any reject (usable in CI).
adaptyv-kinetics qc fake_package.zip --fail-on critical
```

```python
from adaptyv_kinetics import DataPackage

pkg = DataPackage.from_zip("package.zip")   # or .from_dir("package/")
pkg.summary()                 # polars DataFrame: name, replicate, method, MAE, rel_MAE, Rmax
pkg.refit(bootstrap=1000)     # independent kon/koff/KD + bootstrap CI
pkg.qc()                      # per-replicate verdict: pass / review / reject
pkg.report("report.html")     # self-contained HTML
```

## What it does

- **Parses** the documented layout (`raw_data/`, `fit_data/`, `aux/replicate_info.csv`),
  handling names that contain underscores.
- **Re-fits** a global Langmuir 1:1 model across a replicate's concentration
  series (shared kon/koff/Rmax, per-curve baseline), with a bootstrap CI on K_D.
- **Flags artifacts** with interpretable rules: `LOW_SNR`, `INCOMPLETE_DISSOCIATION`,
  `SPIKE`, `POOR_FIT`.
- **Reports** a self-contained HTML file (embedded plots, data-source banner).

## Positioning

An **independent verifier**, not a competitor to Adaptyv's fitting pipeline. Where
the re-fit agrees with their K_D it is evidence of quality; where it diverges it
is information. See [limitations](docs/limitations.md).

## Validation

The synthetic generator is also the validation harness — true parameters are
known, so recovery error is measured. On exact model data K_D recovery is <1%;
with realistic noise (rounded to 3 decimals as in real packages) median K_D error
stays under 15% when dissociation is adequate.
