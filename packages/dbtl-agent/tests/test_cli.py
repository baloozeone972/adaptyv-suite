"""Test for the dbtl-agent CLI."""

from __future__ import annotations

from dbtl_agent.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_run_reports_guarantees() -> None:
    result = runner.invoke(app, ["run", "--budget", "13000", "--batch", "24", "--rounds", "4"])
    assert result.exit_code == 0
    assert "Budget respected: True" in result.stdout
    assert "audit valid: True" in result.stdout
    assert "random" in result.stdout  # the learning lift vs baseline
