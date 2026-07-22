"""Frozen contracts for the Mosaic loop.

Mosaic optimises three predicted terms — affinity, solubility, stability — and Adaptyv
measures exactly three assays — binding, expression, thermostability. That one-to-one
correspondence is the whole reason this connector exists.
"""

from __future__ import annotations

from enum import StrEnum

from adaptyv_core.schemas import AssayType
from pydantic import BaseModel, Field


class ObjectiveTerm(StrEnum):
    """A term in Mosaic's multi-objective function."""

    AFFINITY = "affinity"
    SOLUBILITY = "solubility"
    STABILITY = "stability"


# The one-to-one map that makes the loop possible.
ASSAY_TO_TERM: dict[AssayType, ObjectiveTerm] = {
    AssayType.AFFINITY: ObjectiveTerm.AFFINITY,
    AssayType.EXPRESSION: ObjectiveTerm.SOLUBILITY,
    AssayType.THERMOSTABILITY: ObjectiveTerm.STABILITY,
}


class DesignMeasurement(BaseModel):
    """One design's predicted objective terms and its measured outcomes."""

    name: str
    predicted: dict[ObjectiveTerm, float]  # what Mosaic optimised
    measured: dict[ObjectiveTerm, float]  # what Adaptyv measured


class Calibration(BaseModel):
    """How one predicted term relates to its measurement."""

    term: ObjectiveTerm
    n: int
    slope: float
    intercept: float
    pearson: float
    spearman: float
    mae_after: float  # residual error after linear calibration

    @property
    def drift(self) -> float:
        """How poorly the predicted term tracks reality (1 - Spearman)."""
        return 1.0 - self.spearman


class DriftReport(BaseModel):
    """Per-term calibrations plus how much recalibration helps the composite objective."""

    calibrations: list[Calibration]
    objective_agreement_raw: float  # Spearman(raw predicted composite, measured composite)
    objective_agreement_calibrated: float
    weights: dict[ObjectiveTerm, float] = Field(default_factory=dict)
