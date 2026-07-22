"""Tests for the analysis orchestration."""

from __future__ import annotations

from adaptyv_core.schemas import ProteinDesign
from expression_rescue.analyze import analyze_campaign, analyze_sequence
from expression_rescue.schemas import RiskTier

CLEAN = "GSDDEE" * 9  # 54 aa, no liabilities
RISKY = "MC" + "I" * 12 + "NG" + "DG" + "A" * 25 + "KRDEKRDE"  # 51 aa, high risk


def test_clean_is_low_risk_and_valid() -> None:
    r = analyze_sequence(ProteinDesign(name="c", sequence=CLEAN))
    assert r.valid
    assert r.risk_tier == RiskTier.LOW
    assert r.liabilities == []


def test_risky_is_high_risk() -> None:
    r = analyze_sequence(ProteinDesign(name="r", sequence=RISKY))
    assert r.valid
    assert r.risk_tier == RiskTier.HIGH
    assert r.risk_score >= 4


def test_blocking_skips_liabilities() -> None:
    # 40 aa is below the 50 minimum: blocked at validation, no diagnosis run.
    r = analyze_sequence(ProteinDesign(name="short", sequence="C" + "I" * 39))
    assert not r.valid
    assert r.blocking_errors
    assert r.liabilities == []


def test_multichain_positions_offset() -> None:
    design = ProteinDesign(name="mc", sequence=CLEAN + ":" + "NG" + CLEAN)
    r = analyze_sequence(design)
    deam = [x for x in r.liabilities if x.code == "DEAMIDATION"]
    assert deam and deam[0].positions[0] >= len(CLEAN)  # motif lives in the second chain


def test_campaign_counts_and_estimate() -> None:
    designs = [
        ProteinDesign(name="c", sequence=CLEAN),
        ProteinDesign(name="r", sequence=RISKY),
        ProteinDesign(name="short", sequence="A" * 40),
    ]
    campaign = analyze_campaign(designs, price_per_protein=169.0)
    assert campaign.n_sequences == 3
    assert campaign.n_blocked == 1
    assert campaign.n_high_risk == 1
    assert campaign.estimated_wasted_usd == 169.0
