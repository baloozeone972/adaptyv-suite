"""Frozen contracts for expression-rescue. Written before any logic."""

from __future__ import annotations

from enum import StrEnum

from adaptyv_core.schemas import Issue, Severity
from pydantic import BaseModel, Field


class RiskTier(StrEnum):
    """Heuristic expression-risk tier (not a calibrated probability)."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Liability(BaseModel):
    """A developability liability at one or more positions in the sequence."""

    code: str
    severity: Severity
    message: str
    positions: list[int] = Field(default_factory=list)  # 0-based residue indices


class Variant(BaseModel):
    """A suggested corrected variant (not experimentally validated)."""

    sequence: str
    mutations: list[str]  # e.g. ["L45S", "C88A"]
    addressed: list[str]  # liability codes this variant targets
    risk_score_before: int
    risk_score_after: int  # re-diagnosed after applying the mutations

    @property
    def score_delta(self) -> int:
        """How much the heuristic risk score dropped (positive is better)."""
        return self.risk_score_before - self.risk_score_after


class SequenceReport(BaseModel):
    """Per-sequence diagnosis."""

    name: str
    sequence: str
    valid: bool
    blocking_errors: list[Issue]
    liabilities: list[Liability]
    risk_score: int
    risk_tier: RiskTier
    suggested_variants: list[Variant] = Field(default_factory=list)


class CampaignReport(BaseModel):
    """Whole-submission diagnosis with a wasted-spend estimate."""

    n_sequences: int
    n_blocked: int
    n_high_risk: int
    estimated_wasted_usd: float
    per_sequence: list[SequenceReport]
