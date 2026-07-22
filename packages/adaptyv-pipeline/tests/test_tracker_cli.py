"""Tests for tracker logging and the CLI."""

from __future__ import annotations

import json
from pathlib import Path

from adaptyv_core.schemas import AssayType
from adaptyv_pipeline.cli import app
from adaptyv_pipeline.schemas import RunState, RunStatus, StepConfig
from adaptyv_pipeline.tracker import log_run, record
from typer.testing import CliRunner

runner = CliRunner()


def _state() -> tuple[RunState, StepConfig]:
    config = StepConfig(
        experiment_type=AssayType.AFFINITY, sequences={"a": "A" * 60}, model_version="m-1"
    )
    state = RunState(run_id="r1", status=RunStatus.DONE, estimate_usd=338.0, package_path="p.zip")
    return state, config


def test_record_links_model_to_result() -> None:
    state, config = _state()
    rec = record(state, config)
    assert rec["model_version"] == "m-1"
    assert rec["status"] == "done"
    assert rec["n_sequences"] == 1


def test_log_run_appends_jsonl(tmp_path: Path) -> None:
    state, config = _state()
    path = tmp_path / "tracker.jsonl"
    log_run(state, config, path)
    log_run(state, config, path)
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["run_id"] == "r1"


def _fasta(tmp_path: Path) -> Path:
    p = tmp_path / "designs.fasta"
    p.write_text(">a\n" + "A" * 60 + "\n>b\n" + "A" * 55 + "\n")
    return p


def test_cli_estimate(tmp_path: Path) -> None:
    result = runner.invoke(app, ["estimate", str(_fasta(tmp_path)), "--assay", "affinity"])
    assert result.exit_code == 0
    assert "estimated" in result.stdout


def test_cli_run_dry_then_execute_then_resume_status(tmp_path: Path) -> None:
    fasta = _fasta(tmp_path)
    sd = tmp_path / "runs"
    tracker = tmp_path / "t.jsonl"
    execd = runner.invoke(
        app,
        [
            "run",
            str(fasta),
            "--execute",
            "--budget",
            "15000",
            "--state-dir",
            str(sd),
            "--tracker",
            str(tracker),
            "--model-version",
            "m-2",
        ],
    )
    assert execd.exit_code == 0
    assert "done" in execd.stdout
    assert tracker.exists()
    run_id = execd.stdout.split("run ")[1].split(" ")[0]
    status = runner.invoke(app, ["status", run_id, "--state-dir", str(sd)])
    assert status.exit_code == 0
    assert "done" in status.stdout
    resumed = runner.invoke(app, ["resume", run_id, "--state-dir", str(sd)])
    assert resumed.exit_code == 0


def test_cli_run_over_budget_blocks(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "run",
            str(_fasta(tmp_path)),
            "--execute",
            "--budget",
            "10",
            "--state-dir",
            str(tmp_path / "runs"),
        ],
    )
    assert result.exit_code == 0
    assert "blocked" in result.stdout
