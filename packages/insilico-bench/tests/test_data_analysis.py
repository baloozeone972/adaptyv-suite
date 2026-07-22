"""Tests for data ingestion and the analysis."""

from __future__ import annotations

from pathlib import Path

from insilico_bench.analysis import analyze, evaluate_score, score_names
from insilico_bench.data import load_csv, synthetic_dataset, write_csv
from insilico_bench.schemas import DesignRecord


def test_synthetic_shape() -> None:
    recs = synthetic_dataset(seed=0, campaigns=("a", "b"), n_per_campaign=10)
    assert len(recs) == 20
    assert {r.campaign for r in recs} == {"a", "b"}
    assert score_names(recs) == ["ipsae", "iptm", "plddt"]


def test_csv_roundtrip(tmp_path: Path) -> None:
    recs = synthetic_dataset(seed=1, campaigns=("a",), n_per_campaign=8)
    path = write_csv(recs, tmp_path / "d.csv")
    loaded = load_csv(path)
    assert len(loaded) == len(recs)
    assert loaded[0].scores.keys() == recs[0].scores.keys()
    assert loaded[0].is_binder == recs[0].is_binder


def test_ipsae_beats_plddt() -> None:
    recs = synthetic_dataset(seed=0)
    reports = {r.score_name: r for r in analyze(recs, bootstrap=150, per_campaign=False)}
    assert reports["ipsae"].auc_roc.value > reports["plddt"].auc_roc.value


def test_per_campaign_cohorts() -> None:
    recs = synthetic_dataset(seed=0, campaigns=("a", "b"), n_per_campaign=40)
    cohorts = {r.cohort for r in analyze(recs, bootstrap=100)}
    assert {"pooled", "a", "b"} <= cohorts


def test_spearman_empty_with_few_binders() -> None:
    recs = [
        DesignRecord(name="x", campaign="c", method="m", scores={"ipsae": 0.5}, is_binder=False)
        for _ in range(10)
    ]
    report = evaluate_score(recs, "ipsae", "pooled", bootstrap=50)
    assert report.spearman_pkd.n == 0  # no binders with pK_D


def test_small_n_warning() -> None:
    recs = synthetic_dataset(seed=0, campaigns=("a",), n_per_campaign=10)
    report = evaluate_score(recs, "ipsae", "pooled", bootstrap=50)
    assert report.small_n_warning
