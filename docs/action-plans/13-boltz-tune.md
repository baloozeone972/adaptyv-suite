# Action plan 13 — boltz-tune (M) ⏳ planned · ⭐⭐ (research)

Spec M (source: `23-spec-M-boltz-tune.md`). Fine-tune only Boltz-2's affinity
module on Adaptyv/Proteinbase data, and measure honestly whether it helps.

## ⚠️ Highest risk in the suite
- Modest data volume (a few thousand points vs orders of magnitude more for the
  2026 protein-ligand results).
- Domain shift: Boltz-2 is mostly protein-ligand; protein-protein transfer is not
  guaranteed.
- Non-trivial compute cost.

**Treat as a tooled research project, not a product.** The defensible deliverable
is *a reproducible harness plus an honest result* — including "it does not help at
this data volume, and here is the factor by which the data would need to grow".
That quantified answer has value to them.

## Reuses from adaptyv-core / suite
- `proteinbase` ingestion, `stats` (grouped CV by cluster/campaign, calibration),
  `insilico-bench` (D) as the evaluation baseline.

## Work packages
| Lot | Content | Effort |
|---|---|---|
| L0 | data prep: pairs, labels, grouped splits (no leakage) | 2 |
| L1 | fine-tune harness for the affinity head only (config, checkpoints) | 3 |
| L2 | evaluation vs base model and vs current interface-metric filter | 2 |
| L3 | learning-curve extrapolation: data needed for a real gain | 1 |
| L4 | reproducible report + honest conclusion | 1 |

Effort: research-bounded, not a fixed j·p estimate. Gate on D being available.
