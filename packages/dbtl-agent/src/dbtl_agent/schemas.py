"""Frozen contracts for the DBTL loop."""

from __future__ import annotations

from pydantic import BaseModel


class RoundResult(BaseModel):
    """What happened in one design-build-test-learn round."""

    round: int
    n_submitted: int
    n_binders: int
    cost_usd: float
    hit_rate: float
    mean_pairwise_identity: float  # anti-monoculture indicator for this batch
    n_families: int


class CampaignOutcome(BaseModel):
    """The whole autonomous campaign."""

    rounds: list[RoundResult]
    total_submitted: int
    total_binders: int
    total_cost_usd: float
    budget_usd: float
    budget_respected: bool  # must be True — the guarantee
    audit_valid: bool  # the hash-chained journal verifies

    @property
    def cumulative_hit_rate(self) -> float:
        """Binders per design submitted across the whole campaign."""
        return self.total_binders / self.total_submitted if self.total_submitted else 0.0
