"""Command-line interface for adaptyv-pipeline (offline simulator backend).

    adaptyv-pipeline estimate designs.fasta --assay affinity
    adaptyv-pipeline run      designs.fasta --assay affinity --execute --budget 15000
    adaptyv-pipeline resume   <run-id>
    adaptyv-pipeline status   <run-id>

A live Foundry backend exists (adaptyv_pipeline.backend.FoundryBackend) but needs
a token; the CLI uses the offline simulator so the whole flow is reproducible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from adaptyv_core.schemas import AssayType
from adaptyv_core.seq.io import read_fasta

from adaptyv_pipeline.backend import SimulatedBackend
from adaptyv_pipeline.schemas import StepConfig
from adaptyv_pipeline.step import PipelineStep
from adaptyv_pipeline.tracker import log_run

app = typer.Typer(add_completion=False, help="Run the Adaptyv wet lab as a pipeline step.")

_DEFAULT_STATE = Path(".adaptyv-runs")


def _config(fasta: Path, assay: AssayType, replicates: int, **kw: object) -> StepConfig:
    sequences = {d.name: d.sequence for d in read_fasta(fasta)}
    return StepConfig(experiment_type=assay, sequences=sequences, replicates=replicates, **kw)  # type: ignore[arg-type]


def _step(state_dir: Path) -> PipelineStep:
    return PipelineStep(SimulatedBackend(), state_dir)


@app.command()
def estimate(
    fasta: Annotated[Path, typer.Argument(help="FASTA of designs.")],
    assay: Annotated[AssayType, typer.Option(help="Assay type.")] = AssayType.AFFINITY,
    replicates: int = 2,
) -> None:
    """Dry-run cost estimate — never submits."""
    state = _step(_DEFAULT_STATE).run(_config(fasta, assay, replicates, dry_run=True))
    typer.echo(f"{state.status.value}: {state.message}")


@app.command()
def run(
    fasta: Annotated[Path, typer.Argument(help="FASTA of designs.")],
    assay: Annotated[AssayType, typer.Option(help="Assay type.")] = AssayType.AFFINITY,
    replicates: int = 2,
    execute: Annotated[
        bool, typer.Option("--execute", help="Actually submit (off by default).")
    ] = False,
    budget: Annotated[float, typer.Option(help="Spend cap in USD (0 = none).")] = 0.0,
    model_version: Annotated[str | None, typer.Option(help="Model version to link.")] = None,
    tracker: Annotated[Path | None, typer.Option(help="Append a JSONL tracker record.")] = None,
    state_dir: Path = _DEFAULT_STATE,
) -> None:
    """Estimate, then (if --execute and within budget) submit, poll and fetch."""
    config = _config(
        fasta,
        assay,
        replicates,
        dry_run=not execute,
        budget_usd=budget,
        model_version=model_version,
    )
    step = _step(state_dir)
    state = step.run(config)
    typer.echo(f"run {state.run_id} -> {state.status.value}: {state.message}")
    if tracker is not None:
        log_run(state, config, tracker)


@app.command()
def resume(
    run_id: Annotated[str, typer.Argument(help="Run id to resume.")],
    state_dir: Path = _DEFAULT_STATE,
) -> None:
    """Resume an interrupted run from its persisted state."""
    state = _step(state_dir).resume(run_id)
    typer.echo(f"run {state.run_id} -> {state.status.value}: {state.message}")


@app.command()
def status(
    run_id: Annotated[str, typer.Argument(help="Run id to inspect.")],
    state_dir: Path = _DEFAULT_STATE,
) -> None:
    """Print the persisted status of a run."""
    state = _step(state_dir).load(run_id)
    typer.echo(f"run {state.run_id} -> {state.status.value}")
    for line in state.log:
        typer.echo(f"  - {line}")


if __name__ == "__main__":
    app()
