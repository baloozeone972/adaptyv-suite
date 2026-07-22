"""Heuristic expression-risk scoring.

Deliberately rule-based and honest: this is a tier, not a calibrated probability.
A calibrated P(express) model (LightGBM on Proteinbase labels, ESM
log-likelihood) is specified but needs Adaptyv's labelled data — see the tool's
limitations. The rule tier is still useful and is what degrades gracefully.
"""

from __future__ import annotations

from adaptyv_core.schemas import Severity

from expression_rescue.schemas import Liability, RiskTier

_WEIGHT = {Severity.INFO: 1, Severity.WARNING: 2, Severity.CRITICAL: 3}
_HIGH_AT = 4
_MEDIUM_AT = 2


def risk_score(liabilities: list[Liability]) -> int:
    """Weighted sum of liability severities.

    >>> risk_score([])
    0
    """
    return sum(_WEIGHT[liability.severity] for liability in liabilities)


def risk_tier(score: int) -> RiskTier:
    """Map a risk score to a tier.

    >>> risk_tier(0), risk_tier(2), risk_tier(5)
    (<RiskTier.LOW: 'low'>, <RiskTier.MEDIUM: 'medium'>, <RiskTier.HIGH: 'high'>)
    """
    if score >= _HIGH_AT:
        return RiskTier.HIGH
    if score >= _MEDIUM_AT:
        return RiskTier.MEDIUM
    return RiskTier.LOW
