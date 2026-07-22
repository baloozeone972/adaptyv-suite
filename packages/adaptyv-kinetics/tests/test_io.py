"""I/O round-trip: synthetic generation then parsing, from dir and from zip."""

from __future__ import annotations

from pathlib import Path

from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator


def _gen() -> PackageGenerator:
    g = PackageGenerator(seed=7)
    g.add_protein("binder_001", kd_nM=13.2, replicates=2)  # name contains underscore
    g.add_protein("binder_002", non_binder=True, replicates=1)
    return g


def test_from_dir_roundtrip(tmp_path: Path) -> None:
    root = _gen().write_dir(tmp_path / "pkg")
    pkg = DataPackage.from_dir(root)
    infos = pkg.replicate_infos()
    assert {i.name for i in infos} == {"binder_001", "binder_002"}
    assert len(infos) == 3  # 2 + 1 replicates
    # 3 replicates x 5 concentrations
    assert len(pkg.traces()) == 15


def test_underscore_names_parsed(tmp_path: Path) -> None:
    root = _gen().write_dir(tmp_path / "pkg")
    pkg = DataPackage.from_dir(root)
    b1 = [t for t in pkg.traces() if t.name == "binder_001"]
    assert {t.concentration_nM for t in b1} == {3.125, 6.25, 12.5, 25.0, 50.0}


def test_from_zip(tmp_path: Path) -> None:
    zp = _gen().write_zip(tmp_path / "pkg.zip")
    pkg = DataPackage.from_zip(zp)
    assert len(pkg.traces()) == 15
    assert pkg.summary().height == 3
