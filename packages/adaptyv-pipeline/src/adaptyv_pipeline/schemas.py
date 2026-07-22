"""Frozen contracts for the pipeline. Written before any logic."""

from __future__ import annotations

from enum import StrEnum

from adaptyv_core.schemas import AssayType
from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    """Where a pipeline run currently stands."""

    PENDING = "pending"
    ESTIMATED = "estimated"  # cost known; dry-run stops here
    BLOCKED = "blocked"  # over budget; nothing submitted
    SUBMITTED = "submitted"
    DONE = "done"
    FAILED = "failed"


class StepConfig(BaseModel):
    """Declarative description of one wet-lab pipeline step."""

    experiment_type: AssayType
    sequences: dict[str, str]  # name -> sequence
    target_id: str | None = None
    replicates: int = 2
    budget_usd: float = 0.0  # 0 means no cap
    dry_run: bool = True  # SAFE DEFAULT: never spends without an explicit opt-in
    model_version: str | None = None  # links a model version to its physical result


class RunState(BaseModel):
    """Persisted state of a run. Written to disk after every transition."""

    run_id: str
    status: RunStatus
    estimate_usd: float | None = None
    experiment_id: str | None = None
    package_path: str | None = None
    message: str | None = None
    log: list[str] = Field(default_factory=list)

    def note(self, message: str) -> None:
        """Append a human-readable transition note."""
        self.log.append(message)
        self.message = message
