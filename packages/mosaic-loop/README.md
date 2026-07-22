# mosaic-loop

Mosaic optimises a multi-objective function of **predicted** terms — affinity,
solubility, stability — and never sees a measured value. Adaptyv measures exactly
those three (binding, expression, thermostability). This connector closes the loop:
feed the measurements back to **recalibrate** Mosaic's objective terms, and report
**which predicted terms actually track reality**.

## Use

```bash
mosaic-loop analyze --report drift.html
```

```python
from mosaic_loop import analyze, synthetic_measurements
report = analyze(synthetic_measurements())
report.objective_agreement_raw, report.objective_agreement_calibrated
for c in report.calibrations:
    print(c.term, c.spearman, c.drift)
```

## What it reports

- **Per-term drift** — `1 − Spearman(predicted, measured)`. A high-drift term means
  Mosaic is optimising a proxy that doesn't track the measurement, so its optimisation
  pressure on that term is partly wasted. This is the single most useful thing to feed
  back.
- **Calibration** — a linear fit puts each predicted term on its measured scale, so the
  weighted objective combines terms that are actually comparable.
- **Objective realignment** — how much better the *calibrated* composite objective
  agrees (Spearman) with the measured composite than the raw one.

## The honest result

On the synthetic set, the three terms differ sharply, exactly as intended:

| term | Spearman(pred, meas) | drift |
|---|---|---|
| affinity | ~0.96 | ~0.04 |
| solubility | ~0.54 | ~0.46 |
| stability | ~0.0 | ~1.0 ⚠️ poor proxy |

…and recalibration lifts the objective's agreement with reality (e.g. 0.35 → 0.51).
The message: **stability is the term worth feeding measurements back into.** See
`docs/limitations.md`.
