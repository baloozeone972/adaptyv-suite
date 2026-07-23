"""Lab backends: a real Foundry backend and an offline simulator.

The simulator fabricates a schema-conformant package from the requested
sequences (via adaptyv-kinetics), so the whole pipeline runs end-to-end offline
and deterministically — declared as simulated, never presented as real.

`FoundryBackend` uses the real API's one-shot `auto_confirm=True` submission
path (see `adaptyv_core.foundry.FoundryClient.create_experiment`) and follows
`ResultInfo.data_package_url` to fetch the package — both verified against
`adaptyv-sdk`'s source, not assumed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Protocol

from adaptyv_core.foundry import AssayRequest, CostEstimate, ExperimentStatus, FoundryClient
from adaptyv_kinetics.io.synthetic import PackageGenerator

from adaptyv_pipeline.schemas import StepConfig

_UNIT_PRICE_USD = 169.0


class LabBackend(Protocol):
    """What the pipeline needs from a lab, real or simulated."""

    def estimate(self, config: StepConfig) -> CostEstimate: ...
    def submit(self, config: StepConfig) -> str: ...
    def poll(self, experiment_id: str) -> ExperimentStatus: ...
    def fetch_package(self, experiment_id: str, config: StepConfig, dest: Path) -> Path: ...


def _experiment_id(config: StepConfig, prefix: str) -> str:
    digest = hashlib.sha256("".join(sorted(config.sequences)).encode()).hexdigest()[:8]
    return f"{prefix}-{digest}"


class SimulatedBackend:
    """Offline lab. Instant, deterministic, and clearly synthetic."""

    def estimate(self, config: StepConfig) -> CostEstimate:
        n = len(config.sequences)
        return CostEstimate(
            experiment_type=config.experiment_type,
            n_sequences=n,
            total_usd=_UNIT_PRICE_USD * n * config.replicates,
        )

    def submit(self, config: StepConfig) -> str:
        return _experiment_id(config, "sim")

    def poll(self, experiment_id: str) -> ExperimentStatus:
        return ExperimentStatus.DONE  # the simulator completes instantly

    def fetch_package(self, experiment_id: str, config: StepConfig, dest: Path) -> Path:
        gen = PackageGenerator(seed=_seed(experiment_id))
        for name in config.sequences:
            kd = 1.0 + _seed(name) % 100  # deterministic pseudo-affinity in nM
            gen.add_protein(name, kd_nM=float(kd), replicates=config.replicates)
        return gen.write_zip(dest)


class FoundryBackend:
    """Real lab via the Foundry API.

    `submit` uses `create_experiment(..., auto_confirm=True)` — the real API's
    one-shot path — so the whole spend happens at one call, matching how the
    guard/pipeline gate a single atomic submission.
    """

    def __init__(self, client: FoundryClient) -> None:
        self._client = client

    def estimate(self, config: StepConfig) -> CostEstimate:
        return self._client.cost_estimate(_to_request(config))

    def submit(self, config: StepConfig) -> str:
        name = f"{config.experiment_type.value} — {len(config.sequences)} designs"
        handle = self._client.create_experiment(_to_request(config), name, auto_confirm=True)
        return handle.experiment_id

    def poll(self, experiment_id: str) -> ExperimentStatus:
        return self._client.get_experiment(experiment_id).status

    def fetch_package(self, experiment_id: str, config: StepConfig, dest: Path) -> Path:
        return self._client.download_package(experiment_id, dest)


def _to_request(config: StepConfig) -> AssayRequest:
    return AssayRequest(
        experiment_type=config.experiment_type,
        sequences=config.sequences,
        target_id=config.target_id,
        replicates=config.replicates,
    )


def _seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
