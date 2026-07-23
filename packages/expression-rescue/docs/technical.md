# expression-rescue — technical documentation

Diagnose designs that won't express and suggest corrected variants — the workflow
Adaptyv's "Improve Protein Expression" guide published but nobody built.

## Module map

```
validate/        reused from adaptyv_core.seq.validate (the preflight layer)
diagnose/liabilities   10 positioned developability liabilities (uses core.biophysics)
score/risk       heuristic tier from weighted severities
rescue/mutations conservative mutations, re-diagnosed, interface-aware
analyze.py       orchestration: SequenceReport / CampaignReport
report.py        self-contained HTML
cli.py           check / estimate / rescue
```

## Liability catalog

| Code | Severity | Detection |
|---|---|---|
| `UNPAIRED_CYS` | warning | odd cysteine count |
| `HYDROPHOBIC_PATCH` | warning | Kyte-Doolittle window mean > 2.0 (core.biophysics) |
| `HIGH_GRAVY` | warning | overall GRAVY > 0.4 |
| `EXTREME_PI` | warning | pI in [6.5, 8.0] (minimal-solubility window) |
| `LOW_COMPLEXITY` | warning | homorepeat ≥ 5 |
| `N_GLYC` | info | sequon `N-X-S/T`, X≠P |
| `DEAMIDATION` | info | `NG`/`NS` |
| `ISOMERIZATION` | info | `DG`/`DP` |
| `HIGH_ALA` | info | alanine fraction > 0.30 |
| `LONG_RIGID_LINKER` | info | ≥ 11 residues with no Gly/Ser |

Each carries its residue **positions** so a correction can be targeted. Liabilities
run **per chain** with position offsets, so no motif is invented at a chain break.

## Risk score

Weighted sum of severities (info 1, warning 2, critical 3). Tier: **high** ≥ 4,
**medium** ≥ 2, else **low**. This is a **heuristic, not a calibrated probability**
— the calibrated P(express) model (LightGBM + ESM on Proteinbase labels) is
specified but needs Adaptyv's data (see `limitations.md`).

## Rescue

Up to 3 conservative mutations targeting localized liabilities, in severity order:
unpaired cys → S; hydrophobic patch residue → T (branched I/L/V/M) or S; deamidation
N → Q. Positions in `interface_positions` are never mutated. The variant is
**re-diagnosed**, so `Variant` reports `risk_score_before`/`after` — the tool never
assumes the fix helped, and never says "improved", only "suggested to consider".

## Data flow

```
FASTA ─▶ validate ─▶ diagnose (per chain) ─▶ risk tier ─▶ [rescue] ─▶ report / estimate
```

`estimate` translates high-risk count into dollars: `n_high × price_per_protein`.

## Testing

100% coverage; one test per liability, tier thresholds, per-chain offsets,
before/after rescue, interface avoidance, and the CLI.

## Domain model

Bounded context: **Developability** — a supporting subdomain downstream of
Submission Validation (**Shared Kernel**: `ProteinDesign`, `Verdict`). Core
aggregates: `Liability`, `Variant`, `SequenceReport`. No relationship to
Adaptyv's Foundry model — every liability is computed from the sequence alone,
before an `Experiment` exists. See
[the DDD doc](../../../docs/architecture/domain-driven-design.md).
