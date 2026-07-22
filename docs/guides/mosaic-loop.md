# mosaic-loop — user guide

Feed Adaptyv's measurements back to recalibrate Mosaic's predicted objective terms
(affinity, solubility, stability) — and flag which of them actually track reality.

## How do I see which terms are trustworthy?

```bash
$ uv run mosaic-loop analyze
```

```
affinity    Spearman +0.96  drift 0.04
solubility  Spearman +0.54  drift 0.46
stability   Spearman -0.03  drift 1.03  <-- poor proxy

Objective agreement with reality: 0.35 raw -> 0.51 calibrated.
```

`drift = 1 − Spearman(predicted, measured)`. High drift (stability, here) means Mosaic
is optimising a proxy that doesn't track what Adaptyv actually measures — the term
worth feeding real data back into first. The last line shows recalibration realigning
the composite objective with reality.

## How do I get the HTML report?

```bash
$ uv run mosaic-loop analyze --report drift.html
```

## How do I run it on your own paired data?

```python
from mosaic_loop import analyze, DesignMeasurement, ObjectiveTerm

records = [
    DesignMeasurement(
        name="design_001",
        predicted={ObjectiveTerm.AFFINITY: 0.71, ObjectiveTerm.SOLUBILITY: 0.55},
        measured={ObjectiveTerm.AFFINITY: 7.4, ObjectiveTerm.SOLUBILITY: 42.0},
    ),
    # ...
]
report = analyze(records)
```

`predicted` comes from Mosaic's objective terms; `measured` from Adaptyv's assays
(affinity↔binding, solubility↔expression, stability↔thermostability — the one-to-one
map that makes this loop possible).

## Gotchas

- No live Mosaic adapter is wired in — the analysis is Mosaic-agnostic and runs on a
  synthetic, **declared** paired dataset here. Point it at a real export and nothing
  else changes. See `docs/limitations.md`.
- Calibration is linear; it cannot fix **drift** (rank disagreement) — that needs a
  better predicted term, which is exactly what the report is telling you.

See also: [README](../../packages/mosaic-loop/README.md) ·
[technical](../../packages/mosaic-loop/docs/technical.md) ·
[limitations](../../packages/mosaic-loop/docs/limitations.md).
