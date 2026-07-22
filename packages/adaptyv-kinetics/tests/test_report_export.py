"""Report rendering and tabular export."""

from __future__ import annotations

from pathlib import Path

from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator
from adaptyv_kinetics.report.export import export_fits, fits_to_frame


def _pkg(tmp_path: Path) -> DataPackage:
    g = PackageGenerator(seed=5)
    g.add_protein("binder_001", kd_nM=13.2, replicates=1)
    g.add_protein("binder_003", non_binder=True, replicates=1)
    return DataPackage.from_dir(g.write_dir(tmp_path / "pkg"))


def test_report_is_self_contained(tmp_path: Path) -> None:
    out = _pkg(tmp_path).report(tmp_path / "r.html", bootstrap=0)
    html = out.read_text()
    assert "<!doctype html>" in html
    assert "Synthetic data" in html  # data-source banner
    assert "data:image/png;base64," in html  # embedded plot


def test_export_formats(tmp_path: Path) -> None:
    fits = _pkg(tmp_path).refit(bootstrap=0)
    for fmt, suffix in [("csv", ".csv"), ("parquet", ".parquet"), ("json", ".json")]:
        p = export_fits(fits, tmp_path / f"fits{suffix}", fmt=fmt)
        assert p.exists() and p.stat().st_size > 0


def test_fits_frame_columns(tmp_path: Path) -> None:
    frame = fits_to_frame(_pkg(tmp_path).refit(bootstrap=0))
    assert {"name", "kd_nM", "kd_ci95_low_nM", "converged"} <= set(frame.columns)
