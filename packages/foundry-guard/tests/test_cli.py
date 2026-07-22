"""Test for the foundry-guard demo CLI."""

from __future__ import annotations

from foundry_guard.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_demo_runs_and_stays_within_budget() -> None:
    result = runner.invoke(app, ["demo", "--budget", "3000"])
    assert result.exit_code == 0
    assert "ALLOW" in result.stdout
    assert "DENY" in result.stdout
    assert "Audit chain valid: True" in result.stdout
    assert "never exceeded" in result.stdout
