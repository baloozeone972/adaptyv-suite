# Action plan 07 — foundry-guard (K) ⏳ planned

Spec K. An MCP proxy between an agent and Adaptyv's server that enforces spend
caps, scope allow-lists, human escalation, and a hash-chained audit journal —
without the agent's cooperation.

## Reuses from adaptyv-core
- `guard` (budget policy, reservation, hash-chained audit — shared with dbtl B),
  `foundry` (token attenuation via `POST /tokens/attenuate`), `config`.

## Work packages
| Lot | Content | Deps | Effort |
|---|---|---|---|
| L0 | schemas (Policy, Decision) | — | 0.5 |
| L1 | proxy/ — MCP façade (streamable HTTP) + upstream client | L0 | 2.5 |
| L2 | policy/ — budget, scope, rate, engine | L0 | 2 |
| L3 | tokens/ — attenuation via API | L0 | 1 |
| L4 | audit/ — hash-chained journal, replay, report | L0 | 1.5 |
| L5 | approval/ — CLI + webhook escalation | L2 | 1 |

**MVP** = L0+L1+L2+L4 ≈ 6.5 j·p. **L1 is the risky lot** (MCP spec: capability
negotiation, error propagation).

## The test that matters
Property-based proof that **no call sequence exceeds the budget** (reservation,
not post-hoc accounting; default-deny on any failure). Infra/security profile,
not ML — best as the differentiating layer of dbtl-agent (B).
