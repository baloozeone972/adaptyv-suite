"""Tests for the predictive metrics."""

from __future__ import annotations

import numpy as np
from insilico_bench.metrics import (
    _rankdata,
    auc_pr,
    auc_roc,
    bootstrap_metric,
    hit_rate_at_k,
    spearman,
)


def test_rankdata_averages_ties() -> None:
    assert list(_rankdata(np.array([1.0, 1.0, 2.0]))) == [1.5, 1.5, 3.0]


def test_auc_roc_perfect_and_reversed() -> None:
    s = np.array([1.0, 2.0, 3.0, 4.0])
    assert auc_roc(s, np.array([0.0, 0.0, 1.0, 1.0])) == 1.0
    assert auc_roc(s, np.array([1.0, 1.0, 0.0, 0.0])) == 0.0


def test_auc_roc_single_class_is_half() -> None:
    assert auc_roc(np.array([1.0, 2.0]), np.array([1.0, 1.0])) == 0.5


def test_auc_pr_bounds() -> None:
    s = np.array([1.0, 2.0, 3.0, 4.0])
    assert auc_pr(s, np.array([0.0, 0.0, 0.0, 0.0])) == 0.0
    assert auc_pr(s, np.array([0.0, 0.0, 1.0, 1.0])) > 0.9


def test_spearman_monotone() -> None:
    a = np.array([1.0, 2.0, 3.0, 4.0])
    assert spearman(a, a) == 1.0
    assert spearman(a, a[::-1]) == -1.0
    assert spearman(np.array([1.0]), np.array([1.0])) == 0.0


def test_hit_rate_at_k() -> None:
    scores = np.array([3.0, 1.0, 2.0])
    labels = np.array([1.0, 0.0, 1.0])
    assert hit_rate_at_k(scores, labels, 1) == 1.0
    assert hit_rate_at_k(scores, labels, 3) == 2 / 3
    assert hit_rate_at_k(scores, labels, 0) == 0.0


def test_bootstrap_metric_brackets_value() -> None:
    rng = np.random.default_rng(0)
    scores = np.concatenate([rng.normal(0, 1, 40), rng.normal(3, 1, 40)])
    labels = np.concatenate([np.zeros(40), np.ones(40)])
    m = bootstrap_metric(auc_roc, scores, labels, n=200)
    assert m.ci_low <= m.value <= m.ci_high
    assert m.n == 80
