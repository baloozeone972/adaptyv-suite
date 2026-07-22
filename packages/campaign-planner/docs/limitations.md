# Known limitations — campaign-planner

## Pricing numbers are approximate

`adaptyv-core.pricing` ships reasonable default unit prices and turnaround times,
not Adaptyv's exact grid. The **structure** is what matters — billing by plate tier,
the publication discount — because that is what drives plate alignment and the
two-step trade-off. Calibrate the absolute numbers against
`POST /experiments/cost-estimate` (via `adaptyv-core.foundry`) when a token is
available; the ranking logic is unchanged.

## Success probabilities are inputs, not predictions

`p_express` and `p_bind` are supplied by the user (or by expression-rescue /
insilico-bench). The planner does not estimate them; it propagates their
consequences with confidence intervals. Garbage in, garbage out — but the crossover
result is robust to moderate error because it depends on the price ratio, not the
exact probability.

## Scope vs the full spec

- Strategies: direct affinity and one two-step (expression → affinity). Screening
  variants, replicate optimisation, and >2-step pipelines are natural extensions on
  the same simulation machinery.
- Objective: expected binders (and cost). "Maximize information" (e.g. spread across
  a diversity axis) is specced but not built.
- No live API calls; everything runs offline and deterministically (seeded).
