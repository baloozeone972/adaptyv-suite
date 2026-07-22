# expression-rescue

Between 7% and 19% of designs sent to the lab don't express — each failure is a
paid well that returns no data. Adaptyv's "Improve Protein Expression" guide
publishes the recommended workflow. **This tool implements it.**

> *You published this workflow. I built it.*

## Use

```bash
# Diagnose developability; optionally write an HTML report.
expression-rescue check designs.fasta --assay affinity --has-target --report report.html

# Estimate the spend at risk from high-risk designs.
expression-rescue estimate designs.fasta --price-per-protein 169

# Suggest conservative corrected variants (max 3 mutations each).
expression-rescue rescue designs.fasta --out corrected.fasta
```

```python
from adaptyv_core.schemas import ProteinDesign
from expression_rescue import analyze_sequence

r = analyze_sequence(ProteinDesign(name="d1", sequence="MC..."))
r.risk_tier            # low / medium / high
r.liabilities          # each with its positions
r.suggested_variants   # conservative corrections (analyze with suggest=True)
```

## What it checks

- **Validation** (shared with `preflight`): alphabet, length 50–700, multichain,
  target/aromatic requirements — blocking errors.
- **Developability liabilities**, each with positions: unpaired cysteine,
  hydrophobic patches, high GRAVY, N-glycosylation sequons, deamidation (NG/NS)
  and isomerization (DG/DP) motifs, minimal-solubility pI window, low-complexity
  homorepeats, high alanine fraction, long rigid (G/S-free) linkers.
- **Heuristic risk tier** (low/medium/high) from weighted liability severities.
- **Rescue**: up to 3 conservative mutations targeting localized liabilities.

## Honesty

The risk tier is a **heuristic, not a calibrated probability**, and rescue
variants are **suggested, not experimentally validated**. The calibrated
P(express) model (LightGBM on Proteinbase labels + ESM log-likelihood) and
ESM-guided rescue re-scoring are specified but need Adaptyv's labelled data —
see [docs/limitations.md](docs/limitations.md). The validation + liability
diagnosis is useful on its own and needs no external data.
