"""Tests for the campaign-planner CLI."""

from __future__ import annotations

import pytest
from adaptyv_core import pricing
from adaptyv_core.schemas import AssayType
from campaign_planner.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_plan_low_expression() -> None:
    result = runner.invoke(
        app, ["plan", "--n", "96", "--p-express", "0.3", "--p-bind", "0.15", "--budget", "20000"]
    )
    assert result.exit_code == 0
    assert "two_step_expression_then_affinity" in result.stdout
    assert "cheaper while P(express)" in result.stdout


def test_plan_reports_binders() -> None:
    result = runner.invoke(app, ["plan", "--n", "48", "--sims", "500"])
    assert result.exit_code == 0
    assert "binders" in result.stdout


def test_plan_reports_when_two_step_never_cheaper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(pricing.UNIT_PRICE_USD, AssayType.EXPRESSION, 169.0)
    result = runner.invoke(app, ["plan", "--n", "96", "--sims", "300"])
    assert result.exit_code == 0
    assert "never cheaper" in result.stdout
