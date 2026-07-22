# Known limitations — boltz-tune

## No actual fine-tuning

The harness does **not** train Boltz-2. It measures and extrapolates a learning curve.
The real experiment — fine-tuning the affinity head on Proteinbase with grouped,
leakage-free splits and scoring at each training size — needs Adaptyv's data and GPU
compute. That is by design: the spec flags this as the highest-risk idea, so the
defensible deliverable is the reusable harness plus an honest, quantified result.

## Synthetic learning curve

The sweep is generated from a hidden power law with noise (declared). Its plateau is only
modestly above the base model — the honest, expected shape at a small data volume with a
protein-protein domain shift. On real data the curve's shape is the empirical unknown the
harness is built to characterise.

## Curve model assumptions

A single power law `plateau − coef·n^(−alpha)` is fitted. Real curves can be noisier,
non-monotone at small n, or have multiple regimes; a richer model (with CIs on the
extrapolation) is a natural extension. The current fit reports a point extrapolation.

## Single metric

Score is one number (e.g. Spearman of predicted vs measured affinity). The real evaluation
should also report calibration and selection metrics (see `insilico-bench`), and compare
against the current interface-metric filter, not just the base model.
