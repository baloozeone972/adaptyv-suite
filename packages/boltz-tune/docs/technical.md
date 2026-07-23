# boltz-tune — technical documentation

A reproducible learning-curve harness for affinity fine-tuning. It does **not** train
Boltz-2 (compute + data it can't reach); it measures the shape of the learning curve and
extrapolates honestly.

## Module map

```
schemas.py   TrainingObservation, LearningCurve (predict, n_for), TuneResult
curve.py     fit_curve (scipy), evaluate (+ verdict)
data.py      synthetic training-size sweep (declared)
cli.py       evaluate
```

## Learning curve

`score(n) = plateau − coef · n^(−alpha)`, fitted by `scipy.optimize.curve_fit` with
bounds (`plateau ∈ [max observed, 1]`, `coef > 0`, `alpha ∈ [0.05, 2]`). `predict(n)`
gives the score at any size; `n_for(target)` inverts it — `n = (coef / (plateau − target))
^ (1/alpha)`, or `None` when `target ≥ plateau` (unreachable at any data volume).

## The four verdicts

`evaluate` fits the curve, reads the current score at the largest observed size, and
returns exactly one honest verdict:

1. **plateau ≤ base** → fine-tuning never beats the base model (domain shift dominates).
2. **current ≥ base + target** → already helps, with the measured lift.
3. **target ≥ plateau** → unreachable above the plateau.
4. otherwise → **needs ~(n_for/current) × more data** to reach the target.

## Why this is the right deliverable

The spec flags this as the highest-risk idea (modest data, domain shift, non-trivial
compute). A trained model would be a fragile claim; a **reproducible harness plus a
quantified answer** — "at this volume you get +X; +Y needs ~Z× more data" — is robust and
useful even when the answer is "not yet".

## Testing

100% coverage: the fit recovers the true plateau; `n_for` reachable/unreachable; all four
verdict branches (already-helps, needs-more-data, unreachable, never-beats-base); the CLI.

## Not built (documented)

The actual fine-tuning of Boltz-2's affinity head on Proteinbase, the grouped
leakage-free splitting of real data, and the true per-size scoring. Those need Adaptyv's
data and GPU compute; the harness is the reusable scaffold around them.

## Domain model

Bounded context: **Fine-tuning Research** — a standalone **Customer/Supplier**
consumer of the shared base plus a declared synthetic size sweep. Core
aggregates: `TrainingObservation`, `LearningCurve`, `TuneResult`. No
relationship to the Foundry ACL — it measures learning-curve shape, not live
experiments. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
