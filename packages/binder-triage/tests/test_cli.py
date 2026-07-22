"""Test for the binder-triage CLI."""

from __future__ import annotations

from binder_triage.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_select_compares_strategies() -> None:
    result = runner.invoke(app, ["select", "--k", "24", "--diversity", "0.8"])
    assert result.exit_code == 0
    assert "top_n" in result.stdout
    assert "diverse_greedy" in result.stdout
    assert "families" in result.stdout
