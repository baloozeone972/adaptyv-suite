"""Frozen contracts for the boltz-tune learning-curve harness."""

from __future__ import annotations

import math

from pydantic import BaseModel


class TrainingObservation(BaseModel):
    """Model quality (e.g. Spearman of predicted vs measured affinity) at a training size."""

    n_train: int
    score: float


class LearningCurve(BaseModel):
    """Power-law fit: score(n) = plateau - coef · n^(-alpha)."""

    plateau: float
    coef: float
    alpha: float

    def predict(self, n: float) -> float:
        """Predicted score at training size n."""
        return float(self.plateau - self.coef * n ** (-self.alpha))

    def n_for(self, target: float) -> float | None:
        """Training size needed to reach `target`, or None if unreachable (target ≥ plateau)."""
        gap = self.plateau - target
        if gap <= 0 or self.coef <= 0:
            return None
        return float((self.coef / gap) ** (1.0 / self.alpha))


class TuneResult(BaseModel):
    """The honest verdict: does fine-tuning help now, and what would a real gain cost?"""

    base_score: float  # the generic model, no fine-tuning
    current_n: int
    current_score: float
    target_lift: float
    n_for_target: float | None
    data_multiple: float | None  # n_for_target / current_n
    verdict: str

    @property
    def current_lift(self) -> float:
        """How much fine-tuning beats the base model at the current data volume."""
        return self.current_score - self.base_score

    def is_finite_multiple(self) -> bool:
        """Whether a finite amount of extra data reaches the target."""
        return self.data_multiple is not None and math.isfinite(self.data_multiple)
