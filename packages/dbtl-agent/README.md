# dbtl-agent

An autonomous **design-build-test-learn** loop over the Adaptyv lab: select a batch,
submit, observe which designs bound, relearn, repeat. This idea is written verbatim
in Adaptyv's most-read blog post, so **the differentiator is the governance layer,
not the loop** — this agent is governance-first.

## Use

```bash
dbtl-agent run --budget 20000 --batch 24 --rounds 6
```

```python
from dbtl_agent import run_campaign
from binder_triage import synthetic_pool
from adaptyv_core.guard import Policy
from adaptyv_core.schemas import AssayType

policy = Policy(max_total_usd=20000, max_per_call_usd=5000, allowed_assays={AssayType.AFFINITY})
outcome = run_campaign(synthetic_pool(), policy)
outcome.budget_respected   # True — the hard guarantee
outcome.audit_valid        # the round-by-round hash chain verifies
```

## The three guarantees (not the yield)

1. **Budget respected — always.** Every round's cost is authorized and reserved
   through the shared `adaptyv-core.guard` *before* anything is submitted, so the
   campaign **cannot** exceed its budget (the guard's reservation invariant is
   property-tested).
2. **Tamper-evident audit.** Every round is appended to a hash-chained journal;
   `audit_valid` fails if any record was altered.
3. **No monoculture.** Selection is diversity-aware, so the loop never collapses onto
   one design family (the TREM2 failure mode).

## And the loop does learn

Learning is Thompson sampling over per-family Beta beliefs: it explores wide early,
exploits confident families later. Against a random-selection control at the same
budget, the agent captures **~20–30% more binders** — while staying within budget,
audited, and diverse.

## Honesty

Runs against a **strict simulated oracle** (it only reveals outcomes for designs that
exist in the pool — no invented data), so the backtest is valid. On a real run the
oracle is the Foundry, gated by `foundry-guard`. The learning lift depends on the
data; the *guarantees* do not. See `docs/limitations.md`.
