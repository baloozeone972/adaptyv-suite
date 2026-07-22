"""Evaluate each in-silico score against wet-lab outcome, pooled and per campaign."""

from __future__ import annotations

from functools import partial

import numpy as np

from insilico_bench.metrics import auc_pr, auc_roc, bootstrap_metric, hit_rate_at_k, spearman
from insilico_bench.schemas import DesignRecord, MetricReport, MetricScore

DEFAULT_KS = (24, 48, 96)
SMALL_N = 30
_EMPTY = MetricScore(value=0.0, ci_low=0.0, ci_high=0.0, n=0)


def _arrays(records: list[DesignRecord], score: str) -> tuple[np.ndarray, np.ndarray]:
    rows = [r for r in records if score in r.scores]
    scores = np.array([r.scores[score] for r in rows], dtype=np.float64)
    labels = np.array([float(r.is_binder) for r in rows], dtype=np.float64)
    return scores, labels


def _spearman_pkd(records: list[DesignRecord], score: str, bootstrap: int) -> MetricScore:
    rows = [r for r in records if score in r.scores and r.is_binder and r.pkd is not None]
    if len(rows) < 5:
        return _EMPTY.model_copy(update={"n": len(rows)})
    s = np.array([r.scores[score] for r in rows], dtype=np.float64)
    p = np.array([r.pkd for r in rows], dtype=np.float64)
    return bootstrap_metric(spearman, s, p, n=bootstrap)


def evaluate_score(
    records: list[DesignRecord],
    score: str,
    cohort: str,
    ks: tuple[int, ...] = DEFAULT_KS,
    bootstrap: int = 500,
) -> MetricReport:
    """Compute discrimination, affinity correlation and hit-rate@k for one score."""
    scores, labels = _arrays(records, score)
    hit = {
        k: bootstrap_metric(partial(hit_rate_at_k, k=k), scores, labels, n=bootstrap) for k in ks
    }
    return MetricReport(
        score_name=score,
        cohort=cohort,
        n=int(scores.size),
        auc_roc=bootstrap_metric(auc_roc, scores, labels, n=bootstrap),
        auc_pr=bootstrap_metric(auc_pr, scores, labels, n=bootstrap),
        spearman_pkd=_spearman_pkd(records, score, bootstrap),
        hit_rate_at_k=hit,
        small_n_warning=scores.size < SMALL_N,
    )


def score_names(records: list[DesignRecord]) -> list[str]:
    """Every score present in the dataset, sorted."""
    return sorted({s for r in records for s in r.scores})


def analyze(
    records: list[DesignRecord],
    ks: tuple[int, ...] = DEFAULT_KS,
    bootstrap: int = 500,
    per_campaign: bool = True,
) -> list[MetricReport]:
    """Evaluate every score pooled, and (optionally) within each campaign."""
    names = score_names(records)
    reports = [evaluate_score(records, s, "pooled", ks, bootstrap) for s in names]
    if per_campaign:
        for campaign in sorted({r.campaign for r in records}):
            subset = [r for r in records if r.campaign == campaign]
            reports += [evaluate_score(subset, s, campaign, ks, bootstrap) for s in names]
    return reports
