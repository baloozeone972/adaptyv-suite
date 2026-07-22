# campaign-planner

Given a budget and an objective, enumerate **valid** experiment strategies — and
rank them. Its edge over the web configurator: it can express **two-step
sequential** strategies (a cheap expression filter, then affinity only on the
survivors) that the point-and-click form cannot.

## Use

```bash
campaign-planner plan --n 96 --p-express 0.4 --p-bind 0.15 --budget 20000
```

```python
from campaign_planner import plan, two_step_crossover, Probs

for r in plan(96, Probs(p_express=0.3, p_bind=0.15), budget=20_000):
    print(r.as_row())
two_step_crossover(96)   # e.g. 0.50: filter first while P(express) < 50%
```

## What it does

- **Prices** each booking by plate tier (`adaptyv-core.pricing`): you pay for the
  whole tier, so unused wells still cost — which is what makes plate alignment and
  the two-step trade-off matter.
- **Simulates** yield and cost by Monte-Carlo (`adaptyv-core` house rule: every
  number gets a CI). The two-step's cost is stochastic — the affinity plate tier
  depends on how many designs survive expression — so a point estimate would lie.
- **Ranks** strategies: within-budget first, then most expected binders, then
  cheapest (the tiebreaker that surfaces the two-step when it matches yield for less).

## The result worth showing

Direct affinity and the two-step deliver the **same expected binders**. The
two-step is **cheaper when expression is unreliable** and **more expensive when it
isn't** — and slower, because it is sequential. The planner reports the exact
crossover: *"filter first while P(express) < 50%."* That is a decision the web
configurator can't even pose. See `docs/limitations.md` for the pricing caveat.
