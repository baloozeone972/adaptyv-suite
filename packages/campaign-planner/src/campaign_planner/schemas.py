"""Frozen contracts for the campaign planner."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True, slots=True)
class Probs:
    """Per-design success probabilities driving the yield simulation."""

    p_express: float  # P(expresses)
    p_bind: float  # P(binds | expressed)


class StrategyResult(BaseModel):
    """The evaluation of one strategy under a budget."""

    name: str
    n_input: int
    total_cost_usd: float  # expected cost
    cost_ci95: tuple[float, float]
    duration_days: int
    expected_binders: float
    binders_ci95: tuple[float, float]
    within_budget: bool
    cost_per_binder: float | None  # None if no binders expected

    def as_row(self) -> str:
        """One-line human summary."""
        budget = "ok" if self.within_budget else "OVER"
        cpb = "—" if self.cost_per_binder is None else f"${self.cost_per_binder:,.0f}/binder"
        return (
            f"{self.name:32} ${self.total_cost_usd:>8,.0f} [{budget}]  "
            f"{self.expected_binders:5.1f} binders "
            f"[{self.binders_ci95[0]:.0f},{self.binders_ci95[1]:.0f}]  {cpb}"
        )
