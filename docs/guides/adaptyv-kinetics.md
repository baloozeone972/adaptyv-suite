# adaptyv-kinetics — user guide

The flagship: reads a binding data package, re-fits the kinetics independently, flags
artifacts, and renders a report — in one command.

## How do I try it without a real package?

```bash
$ uv run adaptyv-kinetics synth --out package.zip
Wrote synthetic package to package.zip
```

Generates a schema-conformant package (5 proteins, including a non-binder and two
injected artifacts) so every command below works with no real data.

## How do I get the full report?

```bash
$ uv run adaptyv-kinetics report package.zip -o report.html
```

Open `report.html`: per-replicate verdicts, raw sensorgrams with the independent re-fit
overlaid, and (see below) a comparison against the package's own numbers. Every report
carries a "synthetic data" banner unless built from a real package.

## How do I just see the QC verdicts (e.g. in CI)?

```bash
$ uv run adaptyv-kinetics qc package.zip --bootstrap 0
PASS    binder_001 rep1: clean
PASS    binder_001 rep2: clean
PASS    binder_002 rep1: clean
PASS    binder_002 rep2: clean
REJECT  binder_003 rep1: LOW_SNR, POOR_FIT
REJECT  binder_003 rep2: LOW_SNR, POOR_FIT
REJECT  binder_004 rep1: INCOMPLETE_DISSOCIATION
REJECT  binder_004 rep2: INCOMPLETE_DISSOCIATION
REVIEW  binder_005 rep1: SPIKE
REVIEW  binder_005 rep2: SPIKE
```

Add `--fail-on critical` to exit non-zero when anything is rejected — the gate for a
pipeline. `--bootstrap 0` skips the confidence-interval resampling for a fast check;
drop it (or set a value like `--bootstrap 1000`) when you want the real CI on K_D.

## How do I check the re-fit against the package's own numbers?

```bash
$ uv run adaptyv-kinetics compare package.zip
```

```
┌────────────┬───────────┬─────────────┬────────────┬───────────────┬───────────────┬───────────────┬──────────────────┐
│ name       ┆ replicate ┆ kd_nM_refit ┆ rmax_refit ┆ rmax_reported ┆ rmax_pct_diff ┆ rel_mae_refit ┆ rel_mae_reported │
╞════════════╪═══════════╪═════════════╪════════════╪═══════════════╪═══════════════╪═══════════════╪══════════════════╡
│ binder_001 ┆ 1         ┆ 29.34       ┆ 1.28       ┆ 0.8           ┆ 59.5          ┆ 0.078         ┆ 0.01             │
```

This is the **independent-verifier** view: where the re-fit agrees, that's confidence;
where it diverges (like the R_max gap above, expected when concentrations don't
saturate binding), that's information to look into — not an error.

## How do I export the kinetic parameters?

```bash
$ uv run adaptyv-kinetics refit package.zip --out fits.csv
```

`--out` accepts `.csv`, `.parquet`, or `.json` (format inferred from the extension).

## Using it as a library

```python
from adaptyv_kinetics import DataPackage

pkg = DataPackage.from_zip("package.zip")   # or .from_dir("package/")
pkg.summary()                # name, replicate, method, MAE, rel_MAE, Rmax
pkg.refit(bootstrap=1000)    # independent kon/koff/K_D + bootstrap CI
pkg.qc()                     # per-replicate verdict
pkg.compare_fits()           # re-fit vs the package's own values
```

## Gotchas

- `INCOMPLETE_DISSOCIATION` means the curve didn't decay enough for k_off to be
  identifiable — the tool refuses to print a confident K_D rather than guessing.
- `.zip` and a plain directory both work everywhere `package` is accepted.

See also: [README](../../packages/adaptyv-kinetics/README.md) ·
[technical](../../packages/adaptyv-kinetics/docs/technical.md) ·
[limitations](../../packages/adaptyv-kinetics/docs/limitations.md).
