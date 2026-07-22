# foundry-guard

A guardrail proxy between an autonomous agent and Adaptyv's Foundry API. It
enforces spend caps, scope allow-lists, human escalation, and a tamper-evident
audit journal — **without the agent's cooperation**. The agent can only spend what
the policy allows.

## Use

```bash
foundry-guard demo --budget 3000
```

```python
from adaptyv_core.foundry import AssayRequest, FoundryClient
from adaptyv_core.guard import Budget, Guard, Policy
from adaptyv_core.schemas import AssayType
from foundry_guard import GuardedLab

policy = Policy(max_total_usd=3000, max_per_call_usd=2000,
                allowed_assays={AssayType.AFFINITY}, require_approval_over_usd=1500)
guard = Guard(policy=policy, budget=Budget(3000))
lab = GuardedLab(client, guard)          # wrap a FoundryClient
lab.submit(AssayRequest(...))            # policed: estimate → authorize → reserve → submit → audit
```

## The guarantee

Spending is controlled by **reservation, not post-hoc accounting**: a call is
authorized and its cost reserved *before* submission, and committed only on success.
So **no sequence of calls can exceed the budget** — proved by a property-based test
that fuzzes call sequences and checks `spent + reserved ≤ cap` always holds. Every
failure is **default-deny**, and the budget is never touched on a denied or failed
call.

## What it enforces

- **Scope** — only assays on the allow-list; anything else is denied.
- **Per-call cap** and **total budget** — both checked before reserving.
- **Human escalation** — requests over a threshold need explicit approval; the
  default gate denies until a human says yes.
- **Audit** — every decision is appended to a **hash-chained** journal; any edit or
  reordering breaks `verify()`.

## Positioning

An infra/security layer, not ML. It is the differentiating layer of **dbtl-agent
(B)**: give an autonomous DBTL loop this guard and it cannot overspend, go
out-of-scope, or act unlogged. The core (`adaptyv-core.guard`) is shared with B.
The full MCP HTTP transport is the thin outer shell (see `docs/limitations.md`);
the tested core is the policy engine.
