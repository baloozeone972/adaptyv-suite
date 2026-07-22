# insilico-bench — user guide

Measure which in-silico score (ipSAE, ipTM, pLDDT, …) actually predicts wet-lab
outcome — a reproducible harness, not a one-off notebook analysis.

## How do I try it without a real Proteinbase export?

```bash
$ uv run insilico-bench synth --out designs.csv
Wrote synthetic dataset to designs.csv
```

## How do I run the benchmark?

```bash
$ uv run insilico-bench run designs.csv --out report.html
```

```
ipsae    AUC-ROC 0.779 [0.712, 0.847] (n=180)
iptm     AUC-ROC 0.716 [0.644, 0.791] (n=180)
plddt    AUC-ROC 0.546 [0.467, 0.631] (n=180)
Wrote report to report.html
```

Ranked by discrimination, each with a **bootstrap 95% CI** and `n` — never a bare
number. On this (synthetic, declared) set: ipSAE clearly discriminates, pLDDT is barely
above chance (0.5).

## How do I read the full report?

Open `report.html`: hit-rate@budget (24/48/96) per score against a random baseline, and
a table with AUC-ROC, average precision, and Spearman correlation with measured pK_D —
per score, pooled and per campaign, with a small-n warning where it applies.

## How do I run it on a real Proteinbase export?

```bash
$ uv run insilico-bench run my_proteinbase_export.csv --out report.html
```

Same command — the CSV just needs columns `name, campaign, method, is_binder, pkd` plus
one column per score (see `docs/technical.md` for the exact contract).

## Gotchas

- Real-data AUCs run optimistic: published designs already passed an in-silico filter,
  so the model partly learns "outcome | passed the filter" — see `docs/limitations.md`.
- Cohorts under n=30 are flagged `small_n_warning` — read those intervals with care.

See also: [README](../../packages/insilico-bench/README.md) ·
[technical](../../packages/insilico-bench/docs/technical.md) ·
[limitations](../../packages/insilico-bench/docs/limitations.md).
