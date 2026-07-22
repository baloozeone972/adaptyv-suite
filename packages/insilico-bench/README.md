# insilico-bench

Everyone filters designs by an in-silico score (ipSAE, ipTM, pLDDT, pAE, Boltz-2
confidence) before paying for wet-lab validation. **Which of those scores actually
predicts the outcome?** This is a reproducible harness that answers that,
campaign by campaign — not a one-off notebook.

## Use

```bash
# No Proteinbase export handy? Generate a synthetic, clearly-labelled dataset.
insilico-bench synth --out designs.csv

# Compute the benchmark and render a regenerable report.
insilico-bench run designs.csv --out report.html
```

```python
from insilico_bench import synthetic_dataset, analyze

records = synthetic_dataset()          # or load_csv("proteinbase_export.csv")
for r in analyze(records):
    print(r.score_name, r.cohort, r.auc_roc.as_row())
```

Point `run` at a real Proteinbase export (columns `name, campaign, method,
is_binder, pkd` + one column per score) and the same analysis runs on real data.

## What it measures (each with a bootstrap CI)

- **Discrimination** — AUC-ROC and average precision (binder vs non-binder).
- **Affinity** — Spearman rho between the score and measured pK_D (binders only).
- **Selection** — hit rate @ budget k ∈ {24, 48, 96}: the fraction of binders you'd
  get if you paid for the top-k by score. The **central figure**, because it maps
  directly onto a plate budget.
- **Cohorts** — pooled and per campaign, with a small-n warning so no CI is
  over-read.

## The trap it avoids

Shipping an analysis instead of a tool. The single command regenerates the whole
report on every new dataset. On the synthetic set the honest result already shows:
**ipSAE discriminates well (AUC ≈ 0.78) and tracks affinity (rho ≈ 0.9); pLDDT
barely beats random.** See `docs/limitations.md`.
