# binder-triage — user guide

Pick which designs to test with a **diversity-aware** selection instead of naive
top-N — so one plate is never a monoculture of near-identical designs.

## How do I compare top-N against the diversity-aware pick?

```bash
$ uv run binder-triage select --k 24 --diversity 0.8
```

```
top_n           $  4,056  expected 18.6  true  8.8  identity 0.76  families 1
diverse_greedy  $  4,056  expected 17.4  true  8.6  identity 0.58  families 4

(Synthetic pool; 'true binders' is generated ground truth for evaluation.)
```

Same cost, almost the same predicted yield — but naive top-N puts everything in **one**
design family (identity 0.76), while the diverse pick spreads across four. If the model
is confidently wrong about that one family, top-N's real yield can collapse; the diverse
pick is insurance against exactly that.

## How do I control the diversity/yield trade-off?

`--diversity` (0 to 1) is the redundancy penalty weight: `0` reduces to pure top-N;
higher values spread the selection across more families at a small predicted-yield cost.

## How do I change the plate size or the pool?

```bash
$ uv run binder-triage select --k 96 --n-clusters 5 --per-cluster 40 --seed 1
```

## Using it as a library (on your own scored candidates)

```python
from binder_triage import Candidate, compare

pool = [Candidate(name="d1", sequence="MKT...", p_bind_pred=0.62, cluster=3), ...]
top, diverse = compare(pool, k=96, diversity_weight=0.5)
diverse.mean_pairwise_identity   # lower = less monoculture
```

`cluster` is your own grouping (e.g. sequence-identity clusters); the algorithm only
needs `p_bind_pred` and `cluster` per candidate — the model itself is not built here
(see `docs/limitations.md`).

## Gotchas

- `p_bind_pred` is an **input** you supply (from your own model, or `insilico-bench` /
  `expression-rescue`); this tool does not train a binding predictor.
- The demo pool is synthetic with a deliberate **per-family predictor bias**, so the
  monoculture trap is visible; on real data the effect size is an empirical question.

See also: [README](../../packages/binder-triage/README.md) ·
[technical](../../packages/binder-triage/docs/technical.md) ·
[limitations](../../packages/binder-triage/docs/limitations.md).
