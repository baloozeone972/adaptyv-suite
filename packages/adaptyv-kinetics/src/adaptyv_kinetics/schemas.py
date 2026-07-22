"""Frozen contracts for the kinetics toolkit. Written before any logic.

Mirrors the on-disk binding data package schema verified against the live docs:
raw sensorgrams have columns `t` (seconds) and `y` (nanometers); replicate
metadata lives in `aux/replicate_info.csv`.
"""

from __future__ import annotations

from adaptyv_core.schemas import Method, Severity, Verdict
from pydantic import BaseModel, Field


class Trace(BaseModel):
    """One raw sensorgram: a (protein, replicate, concentration) curve."""

    name: str
    replicate: int
    concentration_nM: float
    t: list[float]  # seconds
    y: list[float]  # response, nanometers
    is_control: bool = False


class ReplicateInfo(BaseModel):
    """Metadata from aux/replicate_info.csv."""

    name: str
    replicate: int
    method: Method
    mae: float | None = None
    rel_mae: float | None = None
    rmax_estimate: float | None = None


class KineticFit(BaseModel):
    """Result of an independent re-fit of one replicate (all its concentrations)."""

    name: str
    replicate: int
    model: str  # "langmuir_1to1", "langmuir_mtl"
    kon: float  # M^-1 s^-1
    koff: float  # s^-1
    kd_M: float
    kd_ci95: tuple[float, float]
    rmax: float
    chi2_red: float
    rel_mae: float
    n_points: int
    converged: bool


class QCFlag(BaseModel):
    """A single detected artifact, with the measured evidence that triggered it."""

    code: str
    severity: Severity
    message: str
    evidence: dict[str, float] = Field(default_factory=dict)


class TraceVerdict(BaseModel):
    """Disposition for one replicate: its flags and (if any) its re-fit."""

    name: str
    replicate: int
    verdict: Verdict
    flags: list[QCFlag]
    fit: KineticFit | None = None
