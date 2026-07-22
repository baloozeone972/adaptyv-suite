# Roadmap — build order and status

Simplest first, then by the ranking from the specs. Each project has its own
action plan in this folder; validate a plan before I start building it.

| # | Project | Spec | Priority | Effort (MVP) | Status | Plan |
|---|---|---|---|---|---|---|
| 0 | `adaptyv-core` | socle | — | — | ✅ seq I/O + validation + stats + report | this doc |
| 1 | `preflight` | C | ⭐ (entry point) | 1.5 j·p | ✅ **built & green** | [01](01-preflight.md) |
| 2 | `adaptyv-kinetics` | G | ⭐⭐⭐ | 7–8 j·p | ✅ **built & green** | [02](02-adaptyv-kinetics.md) |
| 3 | `expression-rescue` | I | ⭐⭐ | 6 j·p | ✅ **built & green** | [03](03-expression-rescue.md) |
| 4 | `sensorgram-triage` | H | ⭐⭐ | 9 j·p (+G) | ✅ **built & green** | [04](04-sensorgram-triage.md) |
| 5 | `insilico-bench` | D | ⭐⭐ | 7.5 j·p | ✅ **built & green** | [05](05-insilico-bench.md) |
| 6 | `campaign-planner` | J | ⭐ | 5 j·p | ✅ **built & green** | [06](06-campaign-planner.md) |
| 7 | `foundry-guard` | K | ⭐ | 6.5 j·p | ✅ **built & green** | [07](07-foundry-guard.md) |
| 8 | `binder-triage` | A | ⭐⭐ | 11 j·p | ✅ **built & green** (MVP) | [08](08-binder-triage.md) |
| 9 | `dbtl-agent` | B | ⭐⭐ | 11 j·p | ✅ **built & green** (governance-first) | [09](09-dbtl-agent.md) |
| 10 | `adaptyv-pipeline` | L | ⭐⭐⭐ | 8 j·p | ✅ **built & green** | [10](10-adaptyv-pipeline.md) |
| 11 | `protviz` | O | ⭐⭐ | 6 j·p | ✅ **built & green** | [11](11-protviz.md) |
| 12 | `mosaic-loop` | N | ⭐⭐ | 8 j·p | ✅ **built & green** | [12](12-mosaic-loop.md) |
| 13 | `boltz-tune` | M | ⭐⭐ | research | ✅ **built & green** (harness) | [13](13-boltz-tune.md) |

### New specs (L, M, N, O) — added 2026-07-21

Four specs arrived after the first build (source docs `22`–`25` at project root, plus
ecosystem `20`, visualisation `21`, GitHub analysis `26`). Where they land:

- **L — adaptyv-pipeline** ⭐⭐⭐ ties with G as the strongest idea: make Adaptyv a
  declarative Nextflow/Snakemake step (cost dry-run, resume, ML-tracker logging).
  No other CRO can offer this — they have the only API. Reuses `core.foundry`.
- **O — protviz** is the **visualisation layer of G/A/H/I/D**. The kinetics report
  plots are its embryo; extracting them into a shared `protviz` is the natural
  refactor once a second tool needs the same figures.
- **N — mosaic-loop** feeds lab measurements back into Mosaic's objective (binding,
  expression, thermostability map one-to-one to Adaptyv's three assays).
- **M — boltz-tune** is research-flavoured and high-risk; ship it as a reproducible
  harness plus an honest result, not as a product.

## Why this order

1. **preflight** first — pure rules, no model, no external data, exhaustively
   testable. It seeds `adaptyv-core.seq` which everything else reuses. Done.
2. **adaptyv-kinetics (G)** — top-ranked: bounded scope, no unverifiable claim,
   its synthetic generator doubles as its validation harness. A *finished*
   deliverable.
3. **expression-rescue (I)** — reuses preflight's validation as its `validate/`
   layer; strong opening ("you published this workflow, I built it").
4. **sensorgram-triage (H)** — builds on G's parser + artifact catalog.
5. **insilico-bench (D)**, **campaign-planner (J)**, **foundry-guard (K)** —
   independent, medium scope.
6. **binder-triage (A)**, **dbtl-agent (B)** — heaviest; A degrades into I, B is
   the saturated idea so it ships only as a governance-first extension.

## Before verification against the live site

Every spec rests on facts gathered earlier (data-package schema, API endpoints,
TREM2 numbers, pricing grid). Before building G, re-verify the data-package
schema on the live docs — a parser built on a mis-remembered schema is the #1
risk. Flagged in each plan under "Verify first".

## Recommended take-home submission

Ship **preflight + adaptyv-kinetics** as the finished core, keep
**expression-rescue** as the strong fallback, mention H/D/K as extensions in the
Loom's "what I'd do with your internal data" close.
