"""Tests for the pricing model."""

from __future__ import annotations

import pytest
from adaptyv_core.pricing import PROTEINBASE_DISCOUNT, plate_tier_for, price
from adaptyv_core.schemas import AssayType


def test_plate_tiers() -> None:
    assert plate_tier_for(1) == 24
    assert plate_tier_for(24) == 24
    assert plate_tier_for(25) == 48
    assert plate_tier_for(70) == 96
    assert plate_tier_for(10_000) == 768  # overflow clamps to the largest tier


def test_price_bills_by_tier() -> None:
    cost = price(AssayType.AFFINITY, 70)
    assert cost.plate_tier == 96
    assert cost.total_usd == 96 * 169.0
    assert cost.duration_days == 21


def test_replicates_count_as_wells() -> None:
    assert price(AssayType.EXPRESSION, 40, replicates=2).plate_tier == 96  # 80 wells


def test_publish_discount() -> None:
    full = price(AssayType.AFFINITY, 96).total_usd
    discounted = price(AssayType.AFFINITY, 96, publish=True).total_usd
    assert abs(discounted - full * (1 - PROTEINBASE_DISCOUNT)) < 1e-6


def test_unpriced_assay_raises_rather_than_guessing() -> None:
    # Real assay types (matching adaptyv-sdk's ExperimentType) with no pricing data yet.
    for unpriced in (AssayType.FLUORESCENCE, AssayType.EPITOPE_BINNING, AssayType.ENZYME_ACTIVITY):
        with pytest.raises(ValueError, match="No pricing data"):
            price(unpriced, 24)
