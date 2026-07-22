"""Tests for the lab backends."""

from __future__ import annotations

from pathlib import Path

from adaptyv_core.foundry import ExperimentStatus, FoundryClient
from adaptyv_core.schemas import AssayType
from adaptyv_kinetics.io.package import DataPackage
from adaptyv_pipeline.backend import FoundryBackend, SimulatedBackend
from adaptyv_pipeline.schemas import StepConfig

_CONFIG = StepConfig(
    experiment_type=AssayType.AFFINITY, sequences={"a": "A" * 60, "b": "A" * 55}, replicates=2
)


def test_simulated_estimate_price() -> None:
    est = SimulatedBackend().estimate(_CONFIG)
    assert est.n_sequences == 2
    assert est.total_usd == 169.0 * 2 * 2  # price x seqs x replicates


def test_simulated_submit_is_deterministic() -> None:
    assert SimulatedBackend().submit(_CONFIG) == SimulatedBackend().submit(_CONFIG)


def test_simulated_poll_done() -> None:
    assert SimulatedBackend().poll("sim-x") == ExperimentStatus.DONE


def test_simulated_fetch_is_parseable(tmp_path: Path) -> None:
    zp = SimulatedBackend().fetch_package("sim-x", _CONFIG, tmp_path / "p.zip")
    pkg = DataPackage.from_zip(zp)
    assert {"a", "b"} == {i.name for i in pkg.replicate_infos()}


class _FakeTransport:
    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path.endswith("cost-estimate"):
            return {"experiment_type": "affinity", "n_sequences": 2, "total_usd": 500.0}
        return {"experiment_id": "exp-9", "status": "InQueue"}

    def get(self, path: str, token: str) -> dict[str, object]:
        return {"experiment_id": "exp-9", "status": "Done"}

    def get_bytes(self, path: str, token: str) -> bytes:
        return b"ZIPBYTES"


def test_foundry_backend_delegates(tmp_path: Path) -> None:
    backend = FoundryBackend(FoundryClient(_FakeTransport(), "tok"))
    assert backend.estimate(_CONFIG).total_usd == 500.0
    assert backend.submit(_CONFIG) == "exp-9"
    assert backend.poll("exp-9") == ExperimentStatus.DONE
    dest = backend.fetch_package("exp-9", _CONFIG, tmp_path / "p.zip")
    assert dest.read_bytes() == b"ZIPBYTES"
