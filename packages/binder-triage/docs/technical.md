# binder-triage — technical documentation

Constrained, diversity-aware selection of designs under a plate budget.

## Module map

```
schemas.py     Candidate (p_bind_pred, p_bind_true, cluster), Selection
similarity.py  k-mer Jaccard identity, max-to-set, mean pairwise
pool.py        synthetic clustered pool with a per-family predictor bias
select.py      top_n; diverse_greedy (submodular)
evaluate.py    score a selection; compare strategies
cli.py         select
```

## Selection objective

`diverse_greedy` maximises, at each step, the marginal gain
`p_bind_pred − diversity_weight · max_identity_to_set(candidate, selected)`. This is
a monotone submodular objective (predicted mass + a diversity/coverage term), so the
greedy algorithm carries the standard (1 − 1/e) approximation guarantee. With
`diversity_weight = 0` it reduces exactly to top-N (tested). Identity is alignment-free
k-mer Jaccard — fast and adequate as a redundancy proxy.

## Why diversity matters (the pool)

`synthetic_pool` builds families (clusters) of near-identical sequences. Each family
has a true binding quality and, crucially, a **per-family predictor bias**: the model
is systematically over- or under-confident about whole families. Naive top-N loads the
plate with the single highest-*predicted* family; if that family is over-predicted, the
true yield craters. Diversity hedges across families, trading a little predicted yield
for a much better worst case.

## Evaluation

`Selection` reports: expected binders (Σ predicted), true binders (Σ ground truth, only
for synthetic pools), mean pairwise identity (monoculture indicator), families
represented, plate tier and cost (`adaptyv-core.pricing`). `compare` runs top-N and
diverse-greedy side by side.

## Testing

100% coverage. Deterministic assertions at a fixed seed: top-N maximises predicted;
`diversity_weight=0` equals top-N; diverse selection lowers pairwise identity and
spans more families. Similarity edge cases (empty, disjoint, identical) covered.

## Not built (documented extensions)

Real bind-probability model (LightGBM + ESM on Proteinbase, calibrated), grouped CV by
sequence cluster **and** campaign, DPP/ILP selection variants, and expression-aware
two-stage selection. The **selection-bias caveat** — published designs already passed
an in-silico filter — must be stated on real data.

## Domain model

Bounded context: **Selection** — a supporting subdomain downstream of
Developability, in a **Customer/Supplier** relationship with `dbtl-agent`
(the Autonomous Loop consumes its `diverse_greedy` selection, one-way and
versioned). Core aggregates: `Candidate`, `Selection`. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
