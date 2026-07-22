# dbtl-agent — user guide

A governance-first autonomous design-build-test-learn loop: select a batch, submit,
observe outcomes, relearn, repeat — with a budget it mathematically cannot exceed.

## How do I run a campaign?

```bash
$ uv run dbtl-agent run --budget 24000 --batch 24 --rounds 6 --diversity 0.3 --seed 3
```

```
round 0:  9/24 binders (hit 38%)  identity 0.12  families 6
round 1:  7/24 binders (hit 29%)  identity 0.25  families 6
round 2:  9/24 binders (hit 38%)  identity 0.15  families 6
round 3:  9/24 binders (hit 38%)  identity 0.21  families 6
round 4: 13/24 binders (hit 54%)  identity 0.14  families 6

Total 47/120 binders for $20,280 of $24,000 (47 vs 36 random, +31%).
Budget respected: True · audit valid: True (synthetic strict oracle).
```

Read the **last two lines** first: the budget guarantee and audit validity always print
`True`, and the comparison against a random-selection control is how you judge whether
the learning is doing anything (+31% here, at equal spend).

## How do I make it more/less conservative about diversity?

`--diversity` trades exploitation for anti-monoculture insurance, same knob as
`binder-triage` (0 = pure exploitation, higher = more spread across design families).
Watch the `families` column — it should never collapse to 1.

## Using it as a library

```python
from dbtl_agent import run_campaign
from binder_triage import synthetic_pool
from adaptyv_core.guard import Policy
from adaptyv_core.schemas import AssayType

policy = Policy(max_total_usd=20_000, max_per_call_usd=5_000, allowed_assays={AssayType.AFFINITY})
outcome = run_campaign(synthetic_pool(), policy)
outcome.budget_respected   # must always be True
outcome.audit_valid        # the round-by-round hash chain verifies
```

## Gotchas

- The lab is a **strict simulated oracle**: it only ever reveals outcomes for designs
  that exist in the pool you gave it — nothing is invented, so the backtest is honest.
- The learning lift (~20–30% here) is a property of the synthetic pool; the **budget and
  audit guarantees** do not depend on the data at all.

See also: [README](../../packages/dbtl-agent/README.md) ·
[technical](../../packages/dbtl-agent/docs/technical.md) ·
[limitations](../../packages/dbtl-agent/docs/limitations.md).
