"""Parser error paths and prefix-matching edge cases."""

from __future__ import annotations

from pathlib import Path

import pytest
from adaptyv_core.schemas import Method
from adaptyv_kinetics.io.parsers import (
    PackageSchemaError,
    read_replicate_info,
    read_traces,
)
from adaptyv_kinetics.schemas import ReplicateInfo


def _write_info(path: Path, rows: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("name,replicate,method,MAE,rel_MAE,rmax_estimate\n" + rows)
    return path


def test_missing_replicate_info_raises(tmp_path: Path) -> None:
    with pytest.raises(PackageSchemaError):
        read_replicate_info(tmp_path / "nope.csv")


def test_optional_metrics_blank_become_none(tmp_path: Path) -> None:
    info = _write_info(tmp_path / "aux" / "replicate_info.csv", "b,1,BLI,,,\n")
    (parsed,) = read_replicate_info(info)
    assert parsed.mae is None
    assert parsed.rel_mae is None
    assert parsed.method == Method.BLI


def test_wrong_columns_raise(tmp_path: Path) -> None:
    raw = tmp_path / "raw_data"
    raw.mkdir()
    (raw / "b_1_10.0.csv").write_text("time,response\n0,0\n1,1\n")
    infos = [ReplicateInfo(name="b", replicate=1, method=Method.BLI)]
    with pytest.raises(PackageSchemaError):
        read_traces(raw, infos)


def test_unmatched_prefix_is_skipped(tmp_path: Path) -> None:
    raw = tmp_path / "raw_data"
    raw.mkdir()
    (raw / "other_9_10.0.csv").write_text("t,y\n0,0\n")
    infos = [ReplicateInfo(name="b", replicate=1, method=Method.BLI)]
    assert read_traces(raw, infos) == []


def test_non_float_concentration_skipped(tmp_path: Path) -> None:
    raw = tmp_path / "raw_data"
    raw.mkdir()
    (raw / "b_1_notanumber.csv").write_text("t,y\n0,0\n")
    infos = [ReplicateInfo(name="b", replicate=1, method=Method.BLI)]
    assert read_traces(raw, infos) == []


def test_underscore_name_longest_prefix(tmp_path: Path) -> None:
    raw = tmp_path / "raw_data"
    raw.mkdir()
    (raw / "bind_er_2_12.5.csv").write_text("t,y\n0,0\n1,0.5\n")
    infos = [ReplicateInfo(name="bind_er", replicate=2, method=Method.BLI)]
    (trace,) = read_traces(raw, infos)
    assert trace.name == "bind_er"
    assert trace.replicate == 2
    assert trace.concentration_nM == 12.5
