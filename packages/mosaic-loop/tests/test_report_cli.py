"""Tests for the report and CLI."""

from __future__ import annotations

from pathlib import Path

from mosaic_loop.calibrate import analyze
from mosaic_loop.cli import app
from mosaic_loop.data import synthetic_measurements
from mosaic_loop.report import build_report
from typer.testing import CliRunner

runner = CliRunner()


def test_report_self_contained(tmp_path: Path) -> None:
    report = analyze(synthetic_measurements(n=80, seed=0))
    out = build_report(report, tmp_path / "r.html")
    html = out.read_text()
    assert "<!doctype html>" in html
    assert "drift" in html
    assert "Synthetic data" in html


def test_cli_analyze_flags_poor_proxy(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", "--n", "120", "--report", str(tmp_path / "r.html")])
    assert result.exit_code == 0
    assert "poor proxy" in result.stdout  # stability
    assert "Objective agreement" in result.stdout
    assert (tmp_path / "r.html").exists()
