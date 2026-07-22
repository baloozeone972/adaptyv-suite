"""Tests for heuristic risk scoring and tiering."""

from __future__ import annotations

from adaptyv_core.schemas import Severity
from expression_rescue.schemas import Liability, RiskTier
from expression_rescue.score.risk import risk_score, risk_tier


def _liab(sev: Severity) -> Liability:
    return Liability(code="X", severity=sev, message="m")


def test_score_weights() -> None:
    assert risk_score([]) == 0
    assert risk_score([_liab(Severity.INFO)]) == 1
    assert risk_score([_liab(Severity.WARNING)]) == 2
    assert risk_score([_liab(Severity.CRITICAL)]) == 3


def test_tiers() -> None:
    assert risk_tier(0) == RiskTier.LOW
    assert risk_tier(1) == RiskTier.LOW
    assert risk_tier(2) == RiskTier.MEDIUM
    assert risk_tier(3) == RiskTier.MEDIUM
    assert risk_tier(4) == RiskTier.HIGH
    assert risk_tier(10) == RiskTier.HIGH
