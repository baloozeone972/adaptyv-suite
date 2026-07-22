# sensorgram-triage — technical documentation

Auto-sort binding curves and quantify the human review that can be safely removed.
Builds on `adaptyv-kinetics`.

## Module map

```
features.py    per-replicate features + protein-level K_D disagreement
model.py       dependency-free logistic regression (deterministic GD)
labels.py      synthetic labelled dataset (good vs needs-review)
delegation.py  grouped stratified split, delegation curve, calibrate()
triage.py      classify a package into green/orange/red + reasons
report.py      delegation-curve plot + piles (self-contained HTML)
cli.py         calibrate / triage
```

## Features (order = `schemas.FEATURE_NAMES`)

`snr`, `rel_mae`, `decay_fraction`, `spike_sigma`, `converged`, `kd_log_spread`.
The last is protein-level: the spread of `log10(K_D)` across a protein's replicates
— the cross-replicate signal a per-replicate QC pass cannot produce.

## Model

Standardized logistic regression fit by full-batch gradient descent (zero init, L2,
2000 epochs). Deterministic and dependency-free, so training is reproducible and
100% testable. Constant features are handled (std clamped to 1). The point of spec
H is calibration and the delegation trade-off, not model sophistication.

## Delegation analysis

- **Grouped, stratified split** by protein name: replicates of one protein never
  straddle train/test, and both classes appear on each side (a class-sorted name
  set would otherwise make the curve trivial).
- **Curve**: for thresholds in [0,1], `auto_approved_fraction = mean(p < t)` and
  `false_negative_rate = P(p < t | needs-review)`. `operating_point(max_fnr)` returns
  the most auto-approving point within the target FNR.
- **Calibration**: Brier score on the held-out split.

## Triage

Per replicate: `needs_review_prob` from the model → pile (`green < 0.30 ≤ orange <
0.70 ≤ red`), plus interpretable reasons from feature thresholds (low_snr,
incomplete_dissociation, spike, poor_fit, replicate_disagree). Results are ordered
by descending review need.

## Data / honesty

Labels are synthetic and **declared** (banner on every report). To keep the curve
non-trivial, good binders span a range of measurement noise, so the noisiest good
curves overlap the problematic ones — a realistic trade-off. On real data the labels
are Adaptyv's review decisions.

## Testing

100% coverage. Fixtures compute the (costly) calibration once per session; a
`hypothesis`-free but deterministic model makes assertions stable.
