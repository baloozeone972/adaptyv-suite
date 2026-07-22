# Action plan 05 — insilico-bench (D) ⏳ planned

Spec D. A reproducible harness measuring which in-silico scores (ipSAE, ipTM,
pLDDT, pAE, Boltz-2) actually predict wet-lab outcome, campaign by campaign.

## Verify first
- Proteinbase export format & the available campaigns (EGFR R1/R2, Nipah, TREM2,
  BenchBB). **L1 is the risky lot — structure unknown until downloaded.**

## Reuses from adaptyv-core
- `stats` (bootstrap, DeLong, calibration/ECE/Brier, Benjamini-Hochberg),
  `proteinbase` (download/cache/harmonize), `report`.

## Work packages
| Lot | Content | Deps | Effort |
|---|---|---|---|
| L0 | schemas + campaign registry | — | 0.5 |
| L1 | ingest/ — download, cache, harmonize | L0 | 2.5 |
| L2 | metrics/discrimination + bootstrap | L0 | 1.5 |
| L3 | metrics/calibration | L0 | 1 |
| L4 | metrics/selection — hit-rate@k {24,48,96,192} | L0 | 1 |
| L5 | analysis/ — the 7 questions (Q1–Q7) | L1–L4 | 2.5 |
| L6 | report/ — reproducible HTML (+ `--format markdown` blog draft) | L5 | 2 |

**MVP** = L0+L1+L2+L4+L6 ≈ 7.5 j·p.

## The trap to avoid
Shipping an analysis, not a tool. The single command
`insilico-bench run --campaigns all -o report.html` is the deliverable; it
regenerates on every new Proteinbase collection. Always show n and CI; auto-warn
under a small-n threshold.
