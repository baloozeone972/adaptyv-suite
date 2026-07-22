# Action plan 10 — adaptyv-pipeline (L) ⏳ planned · ⭐⭐⭐

Spec L (source: `22-spec-L-adaptyv-pipeline.md`). Make the wet lab a declarative,
reproducible pipeline step — the chain of reproducibility currently breaks exactly
where the data becomes real.

## Why it's top-tier
No other CRO can offer this: Adaptyv has the only API. Their docs state the goal
("wetlab data requests as simple as a slow Modal call"). Nextflow/Snakemake
communities rank reproducibility above all — it's their adoption criterion.

## Verify first
- Foundry endpoints for submit / cost-estimate / status / package download, the
  status lifecycle, and webhook signature (HMAC-SHA256 on the raw body).

## Reuses from adaptyv-core
- `foundry` (submit, cost-estimate gate, webhook HMAC, pagination),
  `config` (BYOK), and `adaptyv-kinetics` to parse the returned package.

## Work packages
| Lot | Content | Effort |
|---|---|---|
| L0 | schemas: run manifest, step config, result handle | 0.5 |
| L1 | `foundry` client in core (cost-estimate, submit, poll, download) | 2 |
| L2 | Nextflow process module + Snakemake rule wrappers | 2 |
| L3 | dry-run cost estimation + resume-after-interruption (state on disk) | 1.5 |
| L4 | ML-tracker logging (W&B / MLflow): model version ↔ physical result | 1 |
| L5 | example pipeline (design → fold → score → **assay** → analyse) + docs | 1 |

**MVP** ≈ 8 j·p. Depends on the shared `foundry` client (also needed by A, B, J, K).

## Non-negotiables
- No submission without a dry-run cost estimate first.
- Deterministic resume: a interrupted run continues from persisted state (a real
  assay takes ~3 weeks).
