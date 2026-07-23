# campaign-planner — technical documentation

Enumerate and rank Adaptyv experiment strategies under a budget, including two-step
sequential strategies. Builds on `adaptyv-core.pricing`.

## Module map

```
schemas.py   Probs (p_express, p_bind), StrategyResult
simulate.py  Monte-Carlo yield + cost for direct and two-step
planner.py   evaluate / plan (rank) + two_step_crossover
cli.py       plan
```

## Pricing model (adaptyv-core.pricing)

Per-well unit prices and turnaround per assay, plus plate tiers
{24,48,96,192,384,768}. `price(assay, n, replicates)` bills the **whole tier** that
holds `n·replicates` wells — unused wells still cost. A 20% Proteinbase-publication
discount is available. Numbers are approximate defaults, calibratable against
`POST /experiments/cost-estimate`.

## Strategies

- **direct_affinity** — affinity on all n designs; non-expressers fail. Cost is
  deterministic; expected binders `= n·p_express·p_bind`.
- **two_step_expression_then_affinity** — expression on all n, then affinity only
  on survivors. Same expected binders, but **cost is stochastic** (survivors →
  affinity plate tier) and **duration is the sum** of both stages.

## Simulation

Vectorised binomial draws: `expressed ~ Binom(n, p_express)`,
`binders ~ Binom(expressed, p_bind)`. Cost per simulation looks up the affinity tier
for that draw's survivor count. Results carry a 95% percentile CI on both binders
and cost.

## Ranking and crossover

`plan` sorts: within-budget first, then most expected binders, then cheapest — the
last key is what makes the two-step win when it matches yield at lower cost.
`two_step_crossover(n)` scans P(express) and returns the highest rate at which the
two-step is still cheaper than direct affinity (None if never). With the default
prices and n=96 this is ≈ 0.5.

## Testing

100% coverage (the no-op Typer group callback is `# pragma: no cover`). Tests
cover the yield/cost simulation, the ranking flip across expression rates, the
budget flag, the crossover (including the None branch via a monkeypatched price),
and the CLI.

## Domain model

Bounded context: **Campaign Economics** — a supporting subdomain sharing
`adaptyv_core.pricing` (Shared Kernel) with Selection and Pipeline
Orchestration. Core aggregates: `Probs`, `StrategyResult`, `CostBreakdown`. It
simulates against Foundry's pricing model but never calls the Foundry ACL
itself — it plans before an `Experiment` is created. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
