"""Build per-sequence and campaign diagnoses."""

from __future__ import annotations

from adaptyv_core.schemas import AssayType, ProteinDesign, Severity
from adaptyv_core.seq.validate import validate_design

from expression_rescue.diagnose.liabilities import diagnose
from expression_rescue.rescue.mutations import suggest_variants
from expression_rescue.schemas import CampaignReport, Liability, RiskTier, SequenceReport
from expression_rescue.score.risk import risk_score, risk_tier


def _diagnose_construct(design: ProteinDesign) -> list[Liability]:
    """Run liabilities per chain, offsetting positions so no motif spans a chain break."""
    out: list[Liability] = []
    offset = 0
    for chain in design.chains:
        for liability in diagnose(chain):
            shifted = [p + offset for p in liability.positions]
            out.append(liability.model_copy(update={"positions": shifted}))
        offset += len(chain)
    return out


def analyze_sequence(
    design: ProteinDesign,
    assay: AssayType | None = None,
    has_target: bool = False,
    suggest: bool = False,
    interface_positions: frozenset[int] = frozenset(),
) -> SequenceReport:
    """Validate, diagnose, score and (optionally) suggest variants for one design.

    Positions in `interface_positions` (0-based, over concatenated residues) are
    never mutated by the rescue step.
    """
    issues = validate_design(design, assay, has_target)
    blocking = [i for i in issues if i.severity == Severity.CRITICAL]
    liabilities = _diagnose_construct(design) if not blocking else []
    score = risk_score(liabilities)
    tier = risk_tier(score)

    variants = []
    if suggest and tier != RiskTier.LOW:
        variants = suggest_variants(design.residues, liabilities, interface_positions)

    return SequenceReport(
        name=design.name,
        sequence=design.sequence,
        valid=not blocking,
        blocking_errors=blocking,
        liabilities=liabilities,
        risk_score=score,
        risk_tier=tier,
        suggested_variants=variants,
    )


def analyze_campaign(
    designs: list[ProteinDesign],
    assay: AssayType | None = None,
    has_target: bool = False,
    price_per_protein: float = 169.0,
    suggest: bool = False,
    interface_positions: frozenset[int] = frozenset(),
) -> CampaignReport:
    """Diagnose a whole submission and estimate the spend at risk."""
    reports = [
        analyze_sequence(d, assay, has_target, suggest, interface_positions) for d in designs
    ]
    n_blocked = sum(not r.valid for r in reports)
    n_high = sum(r.risk_tier == RiskTier.HIGH for r in reports)
    return CampaignReport(
        n_sequences=len(designs),
        n_blocked=n_blocked,
        n_high_risk=n_high,
        estimated_wasted_usd=n_high * price_per_protein,
        per_sequence=reports,
    )
