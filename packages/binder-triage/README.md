# binder-triage

Replace "take the top-N by a single score" with **constrained, diversity-aware
selection** under a plate budget. Naive top-N piles the whole plate into the one
family the model likes best — a **monoculture** that fails catastrophically if the
model is wrong about that family (exactly what the TREM2 hackathon saw: agents
converged, pairwise identity 28.1% vs 22.4%).

## Use

```bash
binder-triage select --k 24 --diversity 0.8
```

```python
from binder_triage import synthetic_pool, compare

pool = synthetic_pool()                       # or your own scored candidates
top, diverse = compare(pool, k=24, diversity_weight=0.8)
diverse.mean_pairwise_identity                # much lower monoculture than top
```

## How it works

- **Selection** — a submodular greedy maximising
  `Σ p_bind_pred − diversity_weight · redundancy`, where redundancy is the k-mer
  identity to the already-selected set. Greedy has the classic (1−1/e) guarantee and,
  critically, stops the plate collapsing into one design family.
- **Evaluation** — expected binders (predicted), true binders (synthetic ground
  truth), mean pairwise identity (monoculture indicator), and families represented.
- **Pricing** — the plate tier and cost come from `adaptyv-core.pricing`.

## The honest result

On a clustered synthetic pool with a **per-family predictor bias**, at a 24-well
budget:

| | expected | true (mean / worst) | identity | families |
|---|---|---|---|---|
| top-N | higher | 11.0 / **3.8** | 0.72 | ~1 |
| diverse | slightly lower | 10.4 / **4.5** | **0.48** | ~4.5 |

Diversity trades a little *predicted* yield for a **much less monoculture selection
and a better worst case** — insurance against the model being confidently wrong about
one family. See `docs/limitations.md` (this is the honest, expected result; the
selection-bias caveat matters on real data).
