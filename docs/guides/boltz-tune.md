# boltz-tune — user guide

A reproducible learning-curve harness: does fine-tuning Boltz-2's affinity head on
Adaptyv's data help, and how much data would a real gain need? Framed as research, not
a product — see `docs/limitations.md` before reading too much into the numbers.

## How do I get the honest verdict?

```bash
$ uv run boltz-tune evaluate --target-lift 0.05
```

```
base model score:        0.660
at current n=1600:      0.698 (+0.038 vs base)
for +0.050 over base: ~6.3x more data

Verdict: needs about 6.3x more data to reach +0.050 over base
(Synthetic learning curve; declared. Real numbers need Adaptyv's data + compute.)
```

The verdict is always one of four honest outcomes: **already helps**, **needs ~N× more
data**, **unreachable** (above the fitted plateau), or **never beats the base model**
(domain shift dominates). Try different targets to see them:

```bash
$ uv run boltz-tune evaluate --target-lift 0.02    # already helps at n=1600
$ uv run boltz-tune evaluate --target-lift 0.10     # unreachable
```

## Using it as a library, on your own training-size sweep

```python
from boltz_tune import evaluate, TrainingObservation

sweep = [TrainingObservation(n_train=n, score=s) for n, s in real_measurements]
result = evaluate(sweep, base_score=0.66, target_lift=0.05)
result.verdict, result.data_multiple
```

`score` should be a single comparable metric (e.g. Spearman of predicted vs measured
affinity) from a **grouped, leakage-free** evaluation at each training size.

## Gotchas

- This harness does **not** fine-tune Boltz-2 — it fits and extrapolates a learning
  curve from `TrainingObservation` points you provide. The demo sweep is synthetic,
  declared, and built to have a plateau only modestly above the base model — the
  honest, expected shape given a modest data volume and a domain shift.
- The curve model is a single power law (`plateau − coef·n^(−alpha)`); it gives a point
  extrapolation, not a confidence band, on the current version.

See also: [README](../../packages/boltz-tune/README.md) ·
[technical](../../packages/boltz-tune/docs/technical.md) ·
[limitations](../../packages/boltz-tune/docs/limitations.md).
