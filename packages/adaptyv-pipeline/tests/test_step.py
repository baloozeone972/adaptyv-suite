"""Tests for the pipeline step: guardrails, persistence and resume."""

from __future__ import annotations

from pathlib import Path

from adaptyv_core.foundry import CostEstimate, ExperimentStatus
from adaptyv_core.schemas import AssayType
from adaptyv_pipeline.schemas import RunStatus, StepConfig
from adaptyv_pipeline.step import PipelineStep

_SEQS = {"a": "A" * 60, "b": "A" * 55}


def _config(**kw: object) -> StepConfig:
    return StepConfig(experiment_type=AssayType.AFFINITY, sequences=_SEQS, **kw)  # type: ignore[arg-type]


class _StubBackend:
    """A backend whose poll result is controllable, to exercise the async path."""

    def __init__(self, poll_status: ExperimentStatus = ExperimentStatus.DONE) -> None:
        self.poll_status = poll_status
        self.submitted = 0

    def estimate(self, config: StepConfig) -> CostEstimate:
        return CostEstimate(experiment_type=config.experiment_type, n_sequences=2, total_usd=676.0)

    def submit(self, config: StepConfig) -> str:
        self.submitted += 1
        return "exp-1"

    def poll(self, experiment_id: str) -> ExperimentStatus:
        return self.poll_status

    def fetch_package(self, experiment_id: str, config: StepConfig, dest: Path) -> Path:
        dest.write_bytes(b"PKG")
        return dest


def test_dry_run_estimates_but_does_not_submit(tmp_path: Path) -> None:
    backend = _StubBackend()
    state = PipelineStep(backend, tmp_path).run(_config(dry_run=True))
    assert state.status == RunStatus.ESTIMATED
    assert state.experiment_id is None
    assert backend.submitted == 0


def test_over_budget_is_blocked(tmp_path: Path) -> None:
    state = PipelineStep(_StubBackend(), tmp_path).run(_config(dry_run=False, budget_usd=100.0))
    assert state.status == RunStatus.BLOCKED
    assert state.experiment_id is None


def test_execute_runs_to_done(tmp_path: Path) -> None:
    state = PipelineStep(_StubBackend(), tmp_path).run(_config(dry_run=False, budget_usd=15000.0))
    assert state.status == RunStatus.DONE
    assert state.package_path is not None
    assert Path(state.package_path).exists()


def test_failed_experiment(tmp_path: Path) -> None:
    backend = _StubBackend(poll_status=ExperimentStatus.FAILED)
    state = PipelineStep(backend, tmp_path).run(_config(dry_run=False))
    assert state.status == RunStatus.FAILED


def test_async_submitted_then_resume_to_done(tmp_path: Path) -> None:
    backend = _StubBackend(poll_status=ExperimentStatus.IN_PRODUCTION)
    step = PipelineStep(backend, tmp_path)
    state = step.run(_config(dry_run=False), run_id="async1")
    assert state.status == RunStatus.SUBMITTED  # still running
    backend.poll_status = ExperimentStatus.DONE
    resumed = step.resume("async1")
    assert resumed.status == RunStatus.DONE
    assert backend.submitted == 1  # not resubmitted on resume


def test_resume_terminal_is_idempotent(tmp_path: Path) -> None:
    step = PipelineStep(_StubBackend(), tmp_path)
    step.run(_config(dry_run=False, budget_usd=15000.0), run_id="t1")
    assert step.resume("t1").status == RunStatus.DONE


def test_load_returns_state(tmp_path: Path) -> None:
    step = PipelineStep(_StubBackend(), tmp_path)
    step.run(_config(dry_run=True), run_id="l1")
    assert step.load("l1").status == RunStatus.ESTIMATED
