"""ML-tracker logging: link a model version to the physical result it produced.

Append-only JSONL by default; the same record maps cleanly onto a W&B / MLflow
run. This closes the second reproducibility gap — training metrics and wet-lab
results living in different systems with nothing tying them together.
"""

from __future__ import annotations

import json
from pathlib import Path

from adaptyv_pipeline.schemas import RunState, StepConfig


def record(state: RunState, config: StepConfig) -> dict[str, object]:
    """Build the tracker record linking model version to physical outcome."""
    return {
        "run_id": state.run_id,
        "model_version": config.model_version,
        "experiment_type": config.experiment_type.value,
        "n_sequences": len(config.sequences),
        "estimate_usd": state.estimate_usd,
        "status": state.status.value,
        "package_path": state.package_path,
    }


def log_run(state: RunState, config: StepConfig, path: str | Path) -> Path:
    """Append one run record to a JSONL tracker file."""
    path = Path(path)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record(state, config)) + "\n")
    return path
