"""Frozen contracts for the in-silico benchmark."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DesignRecord(BaseModel):
    """One design with its in-silico scores and its wet-lab outcome."""

    name: str
    campaign: str
    method: str  # design method, e.g. "RFdiffusion", "Mosaic"
    scores: dict[str, float] = Field(default_factory=dict)  # ipsae, iptm, plddt, ...
    is_binder: bool
    pkd: float | None = None  # -log10(K_D in M); only for binders


class MetricScore(BaseModel):
    """A metric value with a bootstrap confidence interval and sample size."""

    value: float
    ci_low: float
    ci_high: float
    n: int

    def as_row(self) -> str:
        """Render as 'value [lo, hi] (n=…)'."""
        return f"{self.value:.3f} [{self.ci_low:.3f}, {self.ci_high:.3f}] (n={self.n})"


class MetricReport(BaseModel):
    """All metrics for one in-silico score, over one cohort."""

    score_name: str
    cohort: str  # "pooled" or a campaign name
    n: int
    auc_roc: MetricScore
    auc_pr: MetricScore
    spearman_pkd: MetricScore
    hit_rate_at_k: dict[int, MetricScore]  # k -> hit rate among top-k
    small_n_warning: bool
