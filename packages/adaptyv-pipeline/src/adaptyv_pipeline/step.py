"""The pipeline step: estimate -> guard -> submit -> poll -> fetch, with resume.

State is persisted after every transition, so an interrupted run resumes exactly
where it stopped — essential when a real assay takes about three weeks. The
default is dry-run: nothing is submitted (nothing is spent) without an explicit
opt-in, and never above the budget.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from adaptyv_core.foundry import ExperimentStatus

from adaptyv_pipeline.backend import LabBackend
from adaptyv_pipeline.schemas import RunState, RunStatus, StepConfig

_TERMINAL = {RunStatus.DONE, RunStatus.BLOCKED, RunStatus.FAILED}


class PipelineStep:
    """Drives one wet-lab step against a `LabBackend`, persisting state."""

    def __init__(self, backend: LabBackend, state_dir: str | Path) -> None:
        self._backend = backend
        self._dir = Path(state_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def run(self, config: StepConfig, run_id: str | None = None) -> RunState:
        """Start a fresh run and advance it as far as the guardrails allow."""
        rid = run_id or uuid.uuid4().hex[:12]
        state = RunState(run_id=rid, status=RunStatus.PENDING)
        return self._advance(state, config)

    def resume(self, run_id: str) -> RunState:
        """Resume a persisted run from wherever it stopped."""
        state = self._load_state(run_id)
        config = self._load_config(run_id)
        return self._advance(state, config)

    def load(self, run_id: str) -> RunState:
        """Return the persisted state of a run without advancing it."""
        return self._load_state(run_id)

    def _advance(self, state: RunState, config: StepConfig) -> RunState:
        if state.status in _TERMINAL:
            return state
        if state.estimate_usd is None and not self._estimate(state, config):
            return self._save(state, config)
        if config.dry_run and state.experiment_id is None:
            state.status = RunStatus.ESTIMATED
            state.note("dry-run: cost estimated, nothing submitted")
            return self._save(state, config)
        if state.experiment_id is None:
            state.experiment_id = self._backend.submit(config)
            state.status = RunStatus.SUBMITTED
            state.note(f"submitted as {state.experiment_id}")
            self._save(state, config)
        return self._collect(state, config)

    def _estimate(self, state: RunState, config: StepConfig) -> bool:
        estimate = self._backend.estimate(config)
        state.estimate_usd = estimate.total_usd
        state.status = RunStatus.ESTIMATED
        state.note(f"estimated ${estimate.total_usd:,.0f}")
        if config.budget_usd and estimate.total_usd > config.budget_usd:
            state.status = RunStatus.BLOCKED
            state.note(f"blocked: ${estimate.total_usd:,.0f} over budget ${config.budget_usd:,.0f}")
            return False
        return True

    def _collect(self, state: RunState, config: StepConfig) -> RunState:
        status = self._backend.poll(state.experiment_id or "")
        if status == ExperimentStatus.CANCELED:
            state.status = RunStatus.FAILED
            state.note("experiment canceled")
            return self._save(state, config)
        if status != ExperimentStatus.DONE:
            state.note(f"still running ({status.value}); resume later")
            return self._save(state, config)
        dest = self._dir / f"{state.run_id}.zip"
        self._backend.fetch_package(state.experiment_id or "", config, dest)
        state.package_path = str(dest)
        state.status = RunStatus.DONE
        state.note("package fetched")
        return self._save(state, config)

    def _save(self, state: RunState, config: StepConfig) -> RunState:
        (self._dir / f"{state.run_id}.state.json").write_text(state.model_dump_json(indent=2))
        (self._dir / f"{state.run_id}.config.json").write_text(config.model_dump_json(indent=2))
        return state

    def _load_state(self, run_id: str) -> RunState:
        return RunState.model_validate_json((self._dir / f"{run_id}.state.json").read_text())

    def _load_config(self, run_id: str) -> StepConfig:
        return StepConfig.model_validate_json((self._dir / f"{run_id}.config.json").read_text())
