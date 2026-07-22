"""Predictive metrics with paired bootstrap confidence intervals.

Never a bare number: every metric returns a value with a 95% bootstrap CI and its
sample size, matching Adaptyv's own reporting style.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from insilico_bench.schemas import MetricScore

Array = NDArray[np.float64]


def _rankdata(a: Array) -> Array:
    """Average ranks (ties share the mean of their positions)."""
    sorter = np.argsort(a, kind="mergesort")
    inv = np.empty_like(sorter)
    inv[sorter] = np.arange(len(a))
    a_sorted = a[sorter]
    obs = np.r_[True, a_sorted[1:] != a_sorted[:-1]]
    dense = obs.cumsum()[inv]
    counts = np.r_[np.nonzero(obs)[0], len(a)]
    ranks: Array = 0.5 * (counts[dense] + counts[dense - 1] + 1)
    return ranks


def auc_roc(scores: Array, labels: Array) -> float:
    """Area under the ROC curve via the Mann-Whitney statistic."""
    mask = labels.astype(bool)
    n_pos = int(mask.sum())
    n_neg = int(len(labels) - n_pos)
    if n_pos == 0 or n_neg == 0:
        return 0.5
    ranks = _rankdata(scores)
    return float((ranks[mask].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def auc_pr(scores: Array, labels: Array) -> float:
    """Average precision (area under the precision-recall curve)."""
    if labels.sum() == 0:
        return 0.0
    order = np.argsort(-scores, kind="mergesort")
    y = labels[order].astype(np.float64)
    tp = np.cumsum(y)
    precision = tp / np.arange(1, len(y) + 1)
    recall = tp / y.sum()
    recall_prev = np.r_[0.0, recall[:-1]]
    return float(np.sum(precision * (recall - recall_prev)))


def spearman(a: Array, b: Array) -> float:
    """Spearman rank correlation."""
    if len(a) < 2:
        return 0.0
    ra = _rankdata(a) - _rankdata(a).mean()
    rb = _rankdata(b) - _rankdata(b).mean()
    denom = float(np.sqrt((ra**2).sum() * (rb**2).sum()))
    return float((ra * rb).sum() / denom) if denom > 0 else 0.0


def hit_rate_at_k(scores: Array, labels: Array, k: int) -> float:
    """Fraction of binders among the top-k designs by score."""
    k = min(k, len(scores))
    if k == 0:
        return 0.0
    top = np.argsort(-scores, kind="mergesort")[:k]
    return float(labels[top].mean())


def bootstrap_metric(
    fn: Callable[[Array, Array], float], scores: Array, target: Array, n: int = 1000, seed: int = 0
) -> MetricScore:
    """Paired bootstrap of `fn(scores, target)`; returns value + 95% CI."""
    rng = np.random.default_rng(seed)
    m = scores.size
    point = fn(scores, target)
    vals = np.array([fn(scores[i], target[i]) for i in (rng.integers(0, m, m) for _ in range(n))])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return MetricScore(value=float(point), ci_low=float(lo), ci_high=float(hi), n=int(m))
