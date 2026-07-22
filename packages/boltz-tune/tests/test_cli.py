"""Test for the boltz-tune CLI."""

from __future__ import annotations

from boltz_tune.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_evaluate_reports_verdict_and_data_need() -> None:
    result = runner.invoke(app, ["evaluate", "--target-lift", "0.05"])
    assert result.exit_code == 0
    assert "base model score" in result.stdout
    assert "Verdict:" in result.stdout
    assert "more data" in result.stdout  # +0.05 needs ~6x more data


def test_evaluate_already_helps_branch() -> None:
    result = runner.invoke(app, ["evaluate", "--target-lift", "0.02"])
    assert result.exit_code == 0
    assert "Verdict:" in result.stdout
