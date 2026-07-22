"""Frozen contracts for sensorgram triage. Written before any logic."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

FEATURE_NAMES: tuple[str, ...] = (
    "snr",
    "rel_mae",
    "decay_fraction",
    "spike_sigma",
    "converged",
    "kd_log_spread",
)


class Pile(StrEnum):
    """Three-way triage outcome."""

    GREEN = "green"  # publishable without intervention
    ORANGE = "orange"  # anomaly detected; needs a human look
    RED = "red"  # unusable; re-run


class TriageResult(BaseModel):
    """Per-replicate triage decision."""

    name: str
    replicate: int
    pile: Pile
    needs_review_prob: float  # calibrated P(needs review)
    reasons: list[str] = Field(default_factory=list)


class DelegationPoint(BaseModel):
    """One operating point on the delegation curve."""

    threshold: float
    auto_approved_fraction: float
    false_negative_rate: float


class DelegationCurve(BaseModel):
    """The central deliverable: how much human review can be safely removed."""

    points: list[DelegationPoint]
    brier_score: float  # calibration quality (lower is better)
    n: int

    def operating_point(self, max_fnr: float) -> DelegationPoint:
        """Best (most auto-approving) point whose false-negative rate ≤ max_fnr."""
        eligible = [p for p in self.points if p.false_negative_rate <= max_fnr]
        if not eligible:
            return min(self.points, key=lambda p: p.false_negative_rate)
        return max(eligible, key=lambda p: p.auto_approved_fraction)
