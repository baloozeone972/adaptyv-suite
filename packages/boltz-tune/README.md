# boltz-tune

Boltz-2 is Adaptyv's reference model, used **generic**. Adaptyv continuously produces
exactly the data that could specialise its affinity head — protein-protein measurements
with negatives included. **Does fine-tuning on that data actually help, and how much data
would a real gain need?** This is a reproducible harness that answers honestly.

> ⚠️ Treat as a **tooled research project, not a product** — the defensible deliverable is
> the harness plus an honest, quantified result, including "it doesn't help enough yet."

## Use

```bash
boltz-tune evaluate --target-lift 0.05
```

```python
from boltz_tune import evaluate, synthetic_sweep, BASE_SCORE
result = evaluate(synthetic_sweep(), base_score=BASE_SCORE, target_lift=0.05)
result.verdict          # e.g. "needs about 6.3x more data to reach +0.050 over base"
result.data_multiple
```

## What it does

1. Takes a **training-size sweep** — model quality (Spearman of predicted vs measured
   affinity) at increasing amounts of training data, from grouped, leakage-free splits.
   (Here it is synthetic and declared; the real sweep needs Adaptyv's data + compute.)
2. **Fits a power-law learning curve** `score(n) = plateau − coef·n^(−alpha)`.
3. **Extrapolates** the data needed to reach a target lift over the generic base model,
   and returns one of four honest verdicts.

## The honest verdict

On the synthetic sweep (plateau ≈ 0.72, base 0.66):

- `+0.02` over base → **already helps** at the current volume;
- `+0.05` over base → **needs ~6× more data**;
- `+0.10` over base → **unreachable** (above the plateau);
- if the plateau were below the base → **fine-tuning never beats the base model**.

That quantified "here's the factor by which the data would need to grow" is the result
worth delivering — see `docs/limitations.md`.
