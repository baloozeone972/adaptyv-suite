"""Pricing model: plate tiers, per-assay unit prices, discounts.

Shared by campaign-planner (J) and binder-triage (A). The absolute numbers are
approximate defaults (calibrate against POST /experiments/cost-estimate when a
token is available); the *structure* — you book a whole plate tier, so unused wells
still cost — is what drives plate-alignment optimisation.
"""

from __future__ import annotations

from dataclasses import dataclass

from adaptyv_core.schemas import AssayType, PlateTier

# Approximate per-well USD price and turnaround per assay. Calibratable.
# FLUORESCENCE, EPITOPE_BINNING and ENZYME_ACTIVITY exist in the real API
# (adaptyv-sdk's ExperimentType) but have no published pricing data here yet —
# deliberately absent rather than guessed; price() raises ValueError for them.
UNIT_PRICE_USD: dict[AssayType, float] = {
    AssayType.EXPRESSION: 79.0,
    AssayType.SCREENING: 129.0,
    AssayType.AFFINITY: 169.0,
    AssayType.THERMOSTABILITY: 149.0,
}
DURATION_DAYS: dict[AssayType, int] = {
    AssayType.EXPRESSION: 14,
    AssayType.SCREENING: 18,
    AssayType.AFFINITY: 21,
    AssayType.THERMOSTABILITY: 18,
}
PROTEINBASE_DISCOUNT = 0.20  # for publishing the campaign to Proteinbase
_TIERS: tuple[int, ...] = tuple(sorted(t.value for t in PlateTier))


def plate_tier_for(n_wells: int) -> int:
    """Smallest plate tier that holds `n_wells` (the largest tier if it overflows).

    >>> plate_tier_for(70)
    96
    >>> plate_tier_for(1)
    24
    """
    return next((t for t in _TIERS if t >= n_wells), _TIERS[-1])


@dataclass(frozen=True, slots=True)
class CostBreakdown:
    """The cost of one assay booking: you pay for the whole tier."""

    assay: AssayType
    n_wells: int
    plate_tier: int
    unit_price_usd: float
    total_usd: float
    duration_days: int


def price(
    assay: AssayType, n_designs: int, replicates: int = 1, publish: bool = False
) -> CostBreakdown:
    """Cost of running `assay` on `n_designs * replicates` wells, billed by plate tier.

    >>> price(AssayType.AFFINITY, 70).total_usd
    16224.0

    Raises ValueError for an assay with no published pricing data here
    (currently FLUORESCENCE, EPITOPE_BINNING, ENZYME_ACTIVITY) rather than guessing.
    """
    if assay not in UNIT_PRICE_USD:
        raise ValueError(f"No pricing data for {assay.value!r} yet; see pricing.py")
    wells = n_designs * replicates
    tier = plate_tier_for(wells)
    unit = UNIT_PRICE_USD[assay]
    total = tier * unit * (1.0 - (PROTEINBASE_DISCOUNT if publish else 0.0))
    return CostBreakdown(
        assay=assay,
        n_wells=wells,
        plate_tier=tier,
        unit_price_usd=unit,
        total_usd=round(total, 2),
        duration_days=DURATION_DAYS[assay],
    )
