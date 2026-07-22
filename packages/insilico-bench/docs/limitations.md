# Known limitations — insilico-bench

## Synthetic by default

The bundled dataset is **synthetic and declared** (banner on every report). Its
scores are built with known, differing predictive power so the harness is
verifiable. Real conclusions require a real Proteinbase export through `load_csv` —
the analysis code is identical.

## Selection bias (state it out loud)

Published designs have usually already passed an in-silico filter, so a model
trained or evaluated on them learns "outcome | passed the filter", not "outcome".
On real Proteinbase data, AUCs are optimistic for exactly this reason; the honest
framing is comparative (score A vs score B on the same cohort) rather than absolute.

## Scope vs the full spec

The spec lists seven questions. The MVP ships four: discrimination (AUC-ROC / AP),
affinity (Spearman on pK_D), selection (hit-rate@k), and cohort breakdown with a
small-n guard. Not yet built: calibration (ECE / reliability), leave-one-campaign-out
generalization of a combined model, design-method effects, and score combination.
Each slots onto the same `MetricScore` + bootstrap machinery.

## Statistics

- Always show n and a bootstrap CI; cohorts under n=30 are flagged. Small campaigns
  still produce wide intervals — read them as such.
- Ties in scores are handled (average ranks); pK_D correlation uses binders only.
