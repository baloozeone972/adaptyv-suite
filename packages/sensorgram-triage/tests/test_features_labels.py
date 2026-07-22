"""Tests for feature extraction and the labelled dataset."""

from __future__ import annotations

import numpy as np
from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator
from sensorgram_triage.features import extract
from sensorgram_triage.labels import Dataset
from sensorgram_triage.schemas import FEATURE_NAMES


def test_extract_shapes(tmp_path) -> None:  # type: ignore[no-untyped-def]
    gen = PackageGenerator(seed=1)
    gen.add_protein("p", kd_nM=12.0, replicates=2)
    rows = extract(DataPackage.from_dir(gen.write_dir(tmp_path / "pkg")).traces())
    assert len(rows) == 2  # two replicates
    assert all(r.vector.size == len(FEATURE_NAMES) for r in rows)


def test_kd_spread_zero_for_single_replicate(tmp_path) -> None:  # type: ignore[no-untyped-def]
    gen = PackageGenerator(seed=1)
    gen.add_protein("p", kd_nM=12.0, replicates=1)
    (row,) = extract(DataPackage.from_dir(gen.write_dir(tmp_path / "pkg")).traces())
    assert row.vector[-1] == 0.0  # kd_log_spread column


def test_dataset_labels_and_groups(dataset: Dataset) -> None:
    assert dataset.x.shape[0] == dataset.y.size == len(dataset.groups)
    assert set(np.unique(dataset.y)) == {0.0, 1.0}
    assert any(g.startswith("good") for g in dataset.groups)
    assert any(g.startswith("bad") for g in dataset.groups)
