# Shared components — why there is one `adaptyv-core`

Analysis of the 11 project specs, looking for components that recur. Anything
used by two or more projects lives in `adaptyv-core`; anything project-specific
stays in its own package. This is the "base commune" the suite is built on.

## Cross-project component matrix

| Component | Consumers | Home |
|---|---|---|
| Sequence I/O (FASTA parse/write) | preflight, expression-rescue (I), triage (A), dbtl (B) | `adaptyv_core.seq.io` ✅ |
| Submission validation (alphabet, length, multichain, target, aromatics, duplicates, plate) | preflight (C), expression-rescue (I), triage (A) | `adaptyv_core.seq.validate` ✅ |
| Shared enums & contracts (AssayType, PlateTier, Method, Issue, Severity, Verdict) | all | `adaptyv_core.schemas` ✅ |
| Config / BYOK token / logging | all | `adaptyv_core.config`, `.logging` ✅ |
| Biophysical descriptors (pI, GRAVY, patches, cys, N-glyc, Ala fraction) | expression-rescue (I), triage (A), QC (H) | `adaptyv_core.biophysics` ✅ |
| Statistics (bootstrap CI, Fisher, Mann-Whitney, grouped CV, calibration) | triage (A), benchmark (D), QC (H), kinetics (G) | `adaptyv_core.stats` ✅ (bootstrap) |
| Kinetics (Langmuir models, global fit, bootstrap, artifact rules) | kinetics (G), QC (H) | `adaptyv-kinetics` (reused by H) ⏳ |
| Foundry client (cost-estimate, submit, status, download, webhook HMAC) | pipeline (L), triage (A), dbtl (B), planner (J), guard (K) | `adaptyv_core.foundry` ✅ |
| Pricing / plate tiers | planner (J), triage (A) | `adaptyv_core.pricing` ✅ |
| Budget guardrails + hash-chained audit journal | dbtl (B), guard (K) | `adaptyv_core.guard` ✅ |
| Self-contained HTML reporting | kinetics (G), expression-rescue (I), QC (H), benchmark (D) | `adaptyv_core.report` ✅ |
| ESM embeddings / log-likelihood (disk-cached) | triage (A), expression-rescue (I), dbtl (B) | `adaptyv_core.plm` ⏳ |
| Proteinbase ingestion (download, cache, harmonize) | triage (A), benchmark (D), expression-rescue (I), QC (H) | `adaptyv_core.proteinbase` ⏳ |

✅ built · ⏳ planned, pulled in when the first consumer is built.

## Principle

`adaptyv-core` holds **stable primitives**, not orchestration. Each project keeps
its own domain logic and composes core pieces. The rule from the specs holds:
Pydantic contracts are frozen first (`schemas.py`), and every module exposes a
narrow façade so packages can be built and tested in isolation against synthetic
fixtures.

## What this buys us

- `preflight` and the `validate/` layer of `expression-rescue` are the **same
  code** — build once.
- The artifact catalog in `adaptyv-kinetics` (G) is consumed directly by the QC
  triage tool (H); H never re-implements fitting.
- The budget/audit layer is written once and shared by the DBTL agent (B) and the
  MCP guard proxy (K) — exactly the "governance layer nobody else builds".
