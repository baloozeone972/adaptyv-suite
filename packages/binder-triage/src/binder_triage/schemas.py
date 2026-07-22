"""Frozen contracts for binder-triage."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    """One design in the pool: a predicted bind probability and its sequence.

    `p_bind_true` exists only for evaluation on synthetic pools (it is the ground
    truth we generated). On real data it is unknown until the wet lab runs.
    """

    name: str
    sequence: str
    p_bind_pred: float  # model's predicted P(binds)
    cluster: int  # design family (proxy for shared structure)
    p_bind_true: float | None = None


class Selection(BaseModel):
    """The result of selecting a subset under a plate budget."""

    strategy: str
    names: list[str]
    plate_tier: int
    cost_usd: float
    expected_binders: float  # sum of predicted P(binds) over the selection
    true_binders: float | None  # sum of true P(binds), when known (synthetic eval)
    mean_pairwise_identity: float  # monoculture indicator (lower is more diverse)
    n_clusters: int = Field(description="distinct design families represented")
