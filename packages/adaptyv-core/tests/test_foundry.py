"""Tests for the Foundry client and webhook verification, via a fake transport."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

import pytest
from adaptyv_core.foundry import (
    AssayRequest,
    ExperimentStatus,
    FoundryClient,
    verify_webhook,
)
from adaptyv_core.schemas import AssayType


class FakeTransport:
    """Records calls and returns canned responses."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        self.calls.append(("POST", path))
        if path.endswith("cost-estimate"):
            return {
                "experiment_type": payload["experiment_type"],
                "n_sequences": len(payload["sequences"]),  # type: ignore[arg-type]
                "total_usd": 169.0 * len(payload["sequences"]),  # type: ignore[arg-type]
            }
        return {"experiment_id": "exp-1", "status": "InQueue"}

    def get(self, path: str, token: str) -> dict[str, object]:
        self.calls.append(("GET", path))
        return {"experiment_id": "exp-1", "status": "Done"}

    def get_bytes(self, path: str, token: str) -> bytes:
        self.calls.append(("GET_BYTES", path))
        return b"PKGDATA"


def _request() -> AssayRequest:
    return AssayRequest(experiment_type=AssayType.AFFINITY, sequences={"a": "AAAA", "b": "BBBB"})


def test_cost_estimate() -> None:
    est = FoundryClient(FakeTransport(), "tok").cost_estimate(_request())
    assert est.n_sequences == 2
    assert est.total_usd == 338.0


def test_submit_returns_handle() -> None:
    handle = FoundryClient(FakeTransport(), "tok").submit(_request())
    assert handle.experiment_id == "exp-1"
    assert handle.status == ExperimentStatus.IN_QUEUE


def test_status() -> None:
    handle = FoundryClient(FakeTransport(), "tok").status("exp-1")
    assert handle.status == ExperimentStatus.DONE


def test_download_package(tmp_path: Path) -> None:
    dest = FoundryClient(FakeTransport(), "tok").download_package("exp-1", tmp_path / "p.zip")
    assert dest.read_bytes() == b"PKGDATA"


def test_cost_estimate_called_before_submit_paths_differ() -> None:
    t = FakeTransport()
    client = FoundryClient(t, "tok")
    client.cost_estimate(_request())
    client.submit(_request())
    assert ("POST", "/experiments/cost-estimate") in t.calls
    assert ("POST", "/experiments") in t.calls


def test_webhook_roundtrip() -> None:
    body = b'{"event":"done"}'
    sig = hmac.new(b"whsec", body, hashlib.sha256).hexdigest()
    assert verify_webhook(body, sig, "whsec")
    assert verify_webhook(body, "sha256=" + sig, "whsec")  # prefixed form
    assert not verify_webhook(b"tampered", sig, "whsec")


def test_webhook_wrong_secret() -> None:
    body = b"x"
    sig = hmac.new(b"right", body, hashlib.sha256).hexdigest()
    assert not verify_webhook(body, sig, "wrong")


@pytest.mark.parametrize("status", ["Done", "InReview", "Failed"])
def test_status_enum_values(status: str) -> None:
    assert ExperimentStatus(status)
