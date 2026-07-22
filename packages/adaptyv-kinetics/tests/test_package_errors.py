"""DataPackage error paths and archive-extraction safety (zip slip)."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.parsers import PackageSchemaError
from adaptyv_kinetics.io.synthetic import PackageGenerator


def test_from_dir_without_raw_data_raises(tmp_path: Path) -> None:
    (tmp_path / "aux").mkdir()
    with pytest.raises(PackageSchemaError):
        DataPackage.from_dir(tmp_path)


def test_from_zip_rejects_path_traversal(tmp_path: Path) -> None:
    evil = tmp_path / "evil.zip"
    with zipfile.ZipFile(evil, "w") as zf:
        zf.writestr("../escape.txt", "pwned")
    with pytest.raises(PackageSchemaError):
        DataPackage.from_zip(evil)


def test_from_zip_rejects_absolute_path(tmp_path: Path) -> None:
    evil = tmp_path / "abs.zip"
    with zipfile.ZipFile(evil, "w") as zf:
        zf.writestr("/tmp/escape.txt", "pwned")
    with pytest.raises(PackageSchemaError):
        DataPackage.from_zip(evil)


def test_from_zip_empty_has_no_root(tmp_path: Path) -> None:
    empty = tmp_path / "empty.zip"
    with zipfile.ZipFile(empty, "w"):
        pass
    with pytest.raises(PackageSchemaError):
        DataPackage.from_zip(empty)


def test_from_zip_nested_root(tmp_path: Path) -> None:
    # A package placed under a top-level folder inside the zip must still be found.
    gen = PackageGenerator(seed=2)
    gen.add_protein("binder_001", kd_nM=13.2, replicates=1)
    root = gen.write_dir(tmp_path / "inner")
    nested = tmp_path / "nested.zip"
    with zipfile.ZipFile(nested, "w") as zf:
        for f in sorted(root.rglob("*")):
            if f.is_file():
                zf.write(f, Path("package") / f.relative_to(root))
    pkg = DataPackage.from_zip(nested)
    assert len(pkg.traces()) == 5
