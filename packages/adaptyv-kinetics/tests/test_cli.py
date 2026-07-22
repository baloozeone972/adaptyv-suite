"""End-to-end CLI test: synth, then report / refit / qc against the package."""

from __future__ import annotations

from pathlib import Path

from adaptyv_kinetics.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def _make_package(tmp_path: Path) -> Path:
    pkg = tmp_path / "pkg.zip"
    result = runner.invoke(app, ["synth", "--out", str(pkg), "--seed", "1"])
    assert result.exit_code == 0
    assert pkg.exists()
    return pkg


def test_report(tmp_path: Path) -> None:
    pkg = _make_package(tmp_path)
    out = tmp_path / "r.html"
    result = runner.invoke(app, ["report", str(pkg), "--out", str(out), "--bootstrap", "0"])
    assert result.exit_code == 0
    assert "<!doctype html>" in out.read_text()


def test_refit_csv(tmp_path: Path) -> None:
    pkg = _make_package(tmp_path)
    out = tmp_path / "fits.csv"
    result = runner.invoke(app, ["refit", str(pkg), "--out", str(out), "--bootstrap", "0"])
    assert result.exit_code == 0
    assert out.read_text().startswith("name,replicate,model")


def test_qc_fail_on_critical(tmp_path: Path) -> None:
    pkg = _make_package(tmp_path)
    result = runner.invoke(app, ["qc", str(pkg), "--fail-on", "critical", "--bootstrap", "0"])
    assert result.exit_code == 1  # the demo package contains rejectable replicates
    assert "REJECT" in result.stdout


def test_compare(tmp_path: Path) -> None:
    pkg = _make_package(tmp_path)
    result = runner.invoke(app, ["compare", str(pkg)])
    assert result.exit_code == 0
    assert "binder_001" in result.stdout
    assert "rmax" in result.stdout
