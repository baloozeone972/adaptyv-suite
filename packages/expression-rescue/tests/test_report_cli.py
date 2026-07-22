"""Tests for the HTML report and the CLI."""

from __future__ import annotations

from pathlib import Path

from adaptyv_core.schemas import ProteinDesign
from expression_rescue.analyze import analyze_campaign
from expression_rescue.cli import app
from expression_rescue.report import build_report
from typer.testing import CliRunner

runner = CliRunner()
CLEAN = "GSDDEE" * 9
RISKY = "MC" + "I" * 12 + "NG" + "DG" + "A" * 25 + "KRDEKRDE"


def _fasta(tmp_path: Path) -> Path:
    p = tmp_path / "designs.fasta"
    p.write_text(f">clean\n{CLEAN}\n>risky\n{RISKY}\n>short\nMKTAYIAKQR\n")  # incl. a blocked seq
    return p


def test_report_self_contained(tmp_path: Path) -> None:
    campaign = analyze_campaign([ProteinDesign(name="r", sequence=RISKY)])
    out = build_report(campaign, tmp_path / "r.html")
    html = out.read_text()
    assert "<!doctype html>" in html
    assert "Synthetic data" in html
    assert "not a calibrated probability" in html


def test_cli_check(tmp_path: Path) -> None:
    result = runner.invoke(app, ["check", str(_fasta(tmp_path))])
    assert result.exit_code == 0
    assert "HIGH" in result.stdout
    assert "BLOCK" in result.stdout  # the too-short sequence
    assert "high-risk" in result.stdout


def test_cli_check_writes_report(tmp_path: Path) -> None:
    out = tmp_path / "r.html"
    result = runner.invoke(app, ["check", str(_fasta(tmp_path)), "--report", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_cli_estimate(tmp_path: Path) -> None:
    result = runner.invoke(app, ["estimate", str(_fasta(tmp_path)), "--price-per-protein", "169"])
    assert result.exit_code == 0
    assert "high-risk" in result.stdout


def test_cli_rescue(tmp_path: Path) -> None:
    out = tmp_path / "corrected.fasta"
    result = runner.invoke(app, ["rescue", str(_fasta(tmp_path)), "--out", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert out.read_text().startswith(">")
    assert "risk score" in result.stdout  # before/after reported


def test_cli_rescue_with_interface(tmp_path: Path) -> None:
    out = tmp_path / "corrected.fasta"
    result = runner.invoke(
        app, ["rescue", str(_fasta(tmp_path)), "--out", str(out), "--interface", "2,8"]
    )
    assert result.exit_code == 0
    assert out.exists()
