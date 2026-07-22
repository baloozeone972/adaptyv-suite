# foundry-guard — user guide

A guardrail proxy between an autonomous agent and the Foundry API: hard budget, scope
allow-list, human escalation, tamper-evident audit — enforced whether or not the agent
cooperates.

## How do I see it in action?

```bash
$ uv run foundry-guard demo --budget 3000
```

```
ALLOW $    845  small affinity (5)               — submitted
DENY  $    845  out-of-scope expression (5)      — assay 'expression' not in scope
DENY  $  3,380  over per-call cap (20)           — exceeds per-call cap
DENY  $  1,690  needs approval (10)              — human approval declined
ALLOW $  1,014  another small affinity (6)       — submitted

Spent $1,859 of $3,000 (never exceeded).
Audit chain valid: True (8 entries)
```

Five scripted requests through one policy: an out-of-scope assay, a call over the
per-call cap, one needing human approval (denied by default), and two legitimate ones —
all logged, budget never exceeded.

## How do I wrap my own Foundry client?

```python
from adaptyv_core.foundry import FoundryClient
from adaptyv_core.guard import Budget, Guard, Policy
from adaptyv_core.schemas import AssayType
from foundry_guard import GuardedLab

policy = Policy(
    max_total_usd=20_000, max_per_call_usd=5_000,
    allowed_assays={AssayType.AFFINITY}, require_approval_over_usd=3_000,
)
guard = Guard(policy=policy, budget=Budget(20_000))
lab = GuardedLab(FoundryClient(transport, token), guard)

result = lab.submit(request)   # estimate -> authorize -> reserve -> submit -> audit
result.allowed, result.reason
```

## How do I approve a request that needs escalation?

Pass an `ApprovalGate` — any callable `(request, amount) -> bool` — to `GuardedLab`.
The default (`auto_deny`) always says no; wire your own (Slack prompt, CLI confirm,
whatever fits) to actually grant approval when it's warranted.

## Gotchas

- The guarantee is **reservation, not accounting**: cost is authorized and reserved
  *before* submission, so no call sequence can exceed the budget — proven by a
  property-based test, not just eyeballed.
- Every decision (allowed or denied) is appended to the hash-chained journal; verify it
  any time with `guard.journal.verify()`.

See also: [README](../../packages/foundry-guard/README.md) ·
[technical](../../packages/foundry-guard/docs/technical.md) ·
[limitations](../../packages/foundry-guard/docs/limitations.md).
