"""Tests for triage classification, the report and the CLI."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator
from sensorgram_triage.cli import app
from sensorgram_triage.model import LogisticModel
from sensorgram_triage.report import build_report
from sensorgram_triage.schemas import DelegationCurve, Pile
from sensorgram_triage.triage import _pile, _reasons, triage_traces
from typer.testing import CliRunner

runner = CliRunner()


def _package(tmp_path: Path) -> Path:
    gen = PackageGenerator(seed=99)
    gen.add_protein("clean_a", kd_nM=12.0, rmax=0.8, replicates=2)
    gen.add_protein("nonbinder", non_binder=True, replicates=2)
    gen.add_protein("spiky", kd_nM=20.0, artifacts=["spike"], replicates=2)
    return gen.write_zip(tmp_path / "p.zip")


def test_triage_sorts_clean_green_and_bad_red(
    tmp_path: Path, calibrated: tuple[LogisticModel, DelegationCurve]
) -> None:
    model, _ = calibrated
    results = triage_traces(DataPackage.from_zip(_package(tmp_path)).traces(), model)
    by_name = {(r.name, r.replicate): r for r in results}
    assert by_name[("clean_a", 1)].pile == Pile.GREEN
    assert by_name[("nonbinder", 1)].pile == Pile.RED
    # sorted by descending review probability
    probs = [r.needs_review_prob for r in results]
    assert probs == sorted(probs, reverse=True)


def test_triage_empty_traces(calibrated: tuple[LogisticModel, DelegationCurve]) -> None:
    model, _ = calibrated
    assert triage_traces([], model) == []


def test_all_reason_branches() -> None:
    # snr, rel_mae, decay, spike_sigma, converged, kd_spread
    bad = np.array([5.0, 0.3, 0.05, 9.0, 1.0, 1.5])
    codes = _reasons(bad)
    assert {"low_snr", "incomplete_dissociation", "spike", "poor_fit", "replicate_disagree"} <= set(
        codes
    )
    clean = np.array([40.0, 0.05, 0.5, 1.0, 1.0, 0.1])
    assert _reasons(clean) == []


def test_pile_thresholds() -> None:
    assert _pile(0.9) == Pile.RED
    assert _pile(0.5) == Pile.ORANGE
    assert _pile(0.1) == Pile.GREEN


def test_report_self_contained(
    tmp_path: Path, calibrated: tuple[LogisticModel, DelegationCurve]
) -> None:
    model, curve = calibrated
    results = triage_traces(DataPackage.from_zip(_package(tmp_path)).traces(), model)
    out = build_report(curve, results, tmp_path / "r.html")
    html = out.read_text()
    assert "<!doctype html>" in html
    assert "data:image/png;base64," in html  # the delegation curve
    assert "auto-approved" in html


def test_cli_calibrate(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["calibrate", "--max-fnr", "0.05", "--report", str(tmp_path / "r.html")]
    )
    assert result.exit_code == 0
    assert "auto-approved" in result.stdout
    assert (tmp_path / "r.html").exists()


def test_cli_triage(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["triage", str(_package(tmp_path)), "--report", str(tmp_path / "t.html")]
    )
    assert result.exit_code == 0
    assert "GREEN" in result.stdout or "RED" in result.stdout
    assert (tmp_path / "t.html").exists()
