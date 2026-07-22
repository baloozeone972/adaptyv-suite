# Action plan 02 — adaptyv-kinetics (G) ⏳ NEXT · awaiting validation

Spec G, the top recommendation. A library that reads Adaptyv's binding data
package, re-fits the kinetics independently, flags artifacts, and produces a
report — in one command.

## Why this one next

Bounded scope, no unverifiable scientific claim, and its synthetic package
generator doubles as the validation harness (true parameters are known, so we
measure fit-recovery error). A *finished* deliverable.

## Verify first (before any code)

1. Re-read the live "Binding Data Package" doc and confirm the on-disk schema:
   file naming `<name>_<replicate>_<concentration>.csv`, columns `t`/`y`,
   `aux/replicate_info.csv` columns (`MAE`, `rel_MAE`, `rmax_estimate`),
   `blanks/run_mapping.csv`. **A parser built on a wrong schema is the #1 risk.**
2. Confirm units (t in seconds, y in nm) and rounding (3 decimals).

## Reuses from adaptyv-core

- `schemas` (Method BLI/SPR), `config`, `logging`.
- New in core when built here: `stats` (bootstrap CI), `report` (HTML base).

## New Pydantic contracts (frozen first)

`Trace`, `ReplicateInfo`, `KineticFit`, `QCFlag`, `TraceVerdict` — per spec §5.1.

## Work packages

| Lot | Content | Deps | Effort |
|---|---|---|---|
| L0 | `schemas.py` — all kinetics contracts | — | 0.5 |
| L1 | `io/` — package parse + **synthetic generator** | L0 | 2 |
| L2 | `models/` — Langmuir 1:1, global fit, bootstrap CI | L0 | 3 |
| L3 | `models/` — mass transport + bivalent | L2 | 1.5 |
| L4 | `qc/` — shape features + artifact rule catalog (YAML thresholds) | L0, L2 | 2.5 |
| L5 | `report/` — plots, self-contained HTML, CSV/Parquet export | L0 | 2 |
| L6 | `cli.py` + Foundry package download | L1, L5 | 1 |
| L7 | validation, docs, CI | all | 1.5 |

**MVP** = L0+L1+L2+L4+L5 ≈ 7–8 j·p.

## Validation targets

- Parameter recovery: on 200 noiseless synthetic curves, KD relative error < 1%.
- Noise robustness: at SNR 10, median KD error < 15%, CI covers truth ≥ 90%.
- Artifact detection: sensitivity ≥ 90%, specificity ≥ 90% per injected type.
- Round-trip I/O: `write` then `read` restores identical objects.

## Definition of done

`make all` green for the package, coverage ≥ 80%, every public façade documented
in `docs/architecture.md`, limitations in `docs/limitations.md`, data source
(synthetic vs Proteinbase) stamped on every generated figure and report.

## Loom (3 min)

`unzip package.zip` (illegible) → `adaptyv-kinetics report package.zip -o out.html`
→ show verdicts + overlaid fits → zoom on an `INCOMPLETE_DISSOCIATION` curve →
`compare_fits()` vs Adaptyv's own fit → close on "validated on synthetic +
Proteinbase; thresholds to calibrate on your internal data".

## Decision needed from you

- Confirm start on G next (vs I).
- Confirm the "verify-first" schema check is OK to do against the live docs.
