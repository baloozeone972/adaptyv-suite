"""Tests for the report and the CLI."""

from __future__ import annotations

from pathlib import Path

from insilico_bench.analysis import analyze
from insilico_bench.cli import app
from insilico_bench.data import synthetic_dataset
from insilico_bench.report import build_report
from typer.testing import CliRunner

runner = CliRunner()


def test_report_self_contained(tmp_path: Path) -> None:
    recs = synthetic_dataset(seed=0, campaigns=("a",), n_per_campaign=40)
    reports = analyze(recs, bootstrap=100)
    base = sum(r.is_binder for r in recs) / len(recs)
    out = build_report(reports, base, tmp_path / "r.html")
    html = out.read_text()
    assert "<!doctype html>" in html
    assert "data:image/png;base64," in html  # hit-rate figure
    assert "AUC-ROC" in html


def test_report_small_n_note(tmp_path: Path) -> None:
    recs = synthetic_dataset(seed=0, campaigns=("a",), n_per_campaign=10)  # < SMALL_N
    reports = analyze(recs, bootstrap=50)
    out = build_report(reports, 0.4, tmp_path / "r.html")
    assert "small n" in out.read_text()


def test_cli_synth_then_run(tmp_path: Path) -> None:
    csv = tmp_path / "d.csv"
    synthed = runner.invoke(app, ["synth", "--out", str(csv), "--seed", "0"])
    assert synthed.exit_code == 0
    assert csv.exists()
    out = tmp_path / "r.html"
    ran = runner.invoke(app, ["run", str(csv), "--out", str(out), "--bootstrap", "100"])
    assert ran.exit_code == 0
    assert "AUC-ROC" in ran.stdout
    assert out.exists()
