# insilico-bench — technical documentation

A reproducible harness measuring which in-silico scores predict wet-lab outcome.

## Module map

```
schemas.py   DesignRecord, MetricScore (value + CI + n), MetricReport
data.py      synthetic_dataset (declared), load_csv, write_csv (round-trips)
metrics.py   auc_roc, auc_pr (average precision), spearman, hit_rate_at_k, bootstrap
analysis.py  evaluate_score / analyze (pooled + per campaign)
report.py    hit-rate@k figure + AUC table (self-contained HTML)
cli.py       synth / run
```

## Metrics (numpy, no sklearn — deterministic, dependency-light)

- **AUC-ROC** via the Mann-Whitney statistic on average ranks (tie-correct).
- **Average precision** (PR-AUC): `Σ precision_i · (recall_i − recall_{i−1})`,
  which gives 1.0 for a perfect ranking (a naive recall-trapezoid does not).
- **Spearman rho**: Pearson on average ranks.
- **Hit rate @ k**: fraction of binders among the top-k by score.
- **Paired bootstrap**: resample row indices (not values) so score/label pairing is
  preserved; 95% percentile CI + sample size on every metric.

## Analysis

`evaluate_score` computes discrimination, affinity (binders with pK_D only) and
hit-rate@k for one score over one cohort. `analyze` runs every score pooled and
within each campaign. Cohorts under `SMALL_N=30` set `small_n_warning`, surfaced in
the report so no CI is over-interpreted.

## Data contract

CSV columns: `name, campaign, method, is_binder, pkd` plus one column per score.
`is_binder` accepts `1/true/yes`; `pkd` may be blank for non-binders. `write_csv`
round-trips with `load_csv`, so the synthetic set is a faithful stand-in for a real
Proteinbase export.

## Honesty

The synthetic generator builds scores of **known, differing** predictive power
(ipSAE > ipTM > pLDDT) so the harness is verifiable end to end; every report is
stamped synthetic. The seven-question analysis from the spec (calibration,
leave-one-campaign-out, method effects, score combination) extends this core; the
MVP ships discrimination + affinity + selection + cohorts.

## Testing

100% coverage; metric edge cases (perfect/reversed/single-class/ties), CSV
round-trip, the ipSAE > pLDDT ranking, small-n handling, and the CLI.

## Domain model

Bounded context: **Predictive Benchmark** — a supporting subdomain, standalone
**Customer/Supplier** consumer of the shared base plus a declared synthetic
dataset. Core aggregates: `DesignRecord`, `MetricReport`, `MetricScore`. No
relationship to the Foundry ACL — it scores in-silico predictions against
declared ground truth, not live experiments. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
