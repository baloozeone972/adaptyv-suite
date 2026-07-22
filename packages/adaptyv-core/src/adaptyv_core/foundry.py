"""Foundry API client — shared by the pipeline (L), triage (A), DBTL (B), guard (K).

The client depends on a `Transport` protocol, not on a concrete HTTP library, so
every code path is testable offline against a fake transport. The real HTTP
transport is a thin urllib wrapper, excluded from coverage (it only reaches the
network). BYOK: the token comes from the caller and is never logged.

Non-negotiable: nothing that spends money runs without a cost estimate first.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import urllib.request
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from adaptyv_core.schemas import AssayType


class ExperimentStatus(StrEnum):
    """The experiment lifecycle exposed by the Foundry API."""

    WAITING_FOR_CONFIRMATION = "WaitingForConfirmation"
    QUOTE_SENT = "QuoteSent"
    IN_QUEUE = "InQueue"
    IN_PRODUCTION = "InProduction"
    DATA_ANALYSIS = "DataAnalysis"
    IN_REVIEW = "InReview"
    DONE = "Done"
    FAILED = "Failed"


class AssayRequest(BaseModel):
    """A request to run an assay on a set of sequences."""

    experiment_type: AssayType
    sequences: dict[str, str]  # name -> sequence
    target_id: str | None = None
    replicates: int = 2


class CostEstimate(BaseModel):
    """The estimate returned by POST /experiments/cost-estimate."""

    experiment_type: AssayType
    n_sequences: int
    total_usd: float
    currency: str = "USD"


class ExperimentHandle(BaseModel):
    """A live experiment reference."""

    experiment_id: str
    status: ExperimentStatus


class Transport(Protocol):
    """Minimal HTTP surface the client needs. Implementations may be fake."""

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]: ...
    def get(self, path: str, token: str) -> dict[str, object]: ...
    def get_bytes(self, path: str, token: str) -> bytes: ...


def verify_webhook(body: bytes, signature: str, secret: str) -> bool:
    """Verify an X-Adaptyv-Signature HMAC-SHA256 over the raw request body.

    >>> import hmac, hashlib
    >>> sig = hmac.new(b"k", b"body", hashlib.sha256).hexdigest()
    >>> verify_webhook(b"body", sig, "k")
    True
    >>> verify_webhook(b"tampered", sig, "k")
    False
    """
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    provided = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


class FoundryClient:
    """Typed client over a `Transport`. Never logs the token."""

    def __init__(self, transport: Transport, token: str) -> None:
        self._t = transport
        self._token = token

    def cost_estimate(self, request: AssayRequest) -> CostEstimate:
        """Estimate the cost of a request. Call this before any submission."""
        data = self._t.post("/experiments/cost-estimate", _payload(request), self._token)
        return CostEstimate.model_validate(data)

    def submit(self, request: AssayRequest) -> ExperimentHandle:
        """Create an experiment (spends money — gate this behind a cost estimate)."""
        data = self._t.post("/experiments", _payload(request), self._token)
        return ExperimentHandle.model_validate(data)

    def status(self, experiment_id: str) -> ExperimentHandle:
        """Fetch the current status of an experiment."""
        data = self._t.get(f"/experiments/{experiment_id}", self._token)
        return ExperimentHandle.model_validate(data)

    def download_package(self, experiment_id: str, dest: str | Path) -> Path:
        """Download the result package to `dest`."""
        dest = Path(dest)
        dest.write_bytes(self._t.get_bytes(f"/experiments/{experiment_id}/package", self._token))
        return dest


def _payload(request: AssayRequest) -> dict[str, object]:
    return {
        "experiment_type": request.experiment_type.value,
        "sequences": request.sequences,
        "target_id": request.target_id,
        "replicates": request.replicates,
    }


class HttpTransport:  # pragma: no cover - reaches the network; tested via a fake
    """Thin urllib transport against the real Foundry API."""

    def __init__(self, base_url: str) -> None:
        self._base = base_url.rstrip("/")

    def _request(self, path: str, token: str, data: bytes | None) -> bytes:
        req = urllib.request.Request(
            self._base + path,
            data=data,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        with urllib.request.urlopen(req) as resp:
            return bytes(resp.read())

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        raw = self._request(path, token, json.dumps(payload).encode())
        return dict(json.loads(raw))

    def get(self, path: str, token: str) -> dict[str, object]:
        return dict(json.loads(self._request(path, token, None)))

    def get_bytes(self, path: str, token: str) -> bytes:
        return self._request(path, token, None)
