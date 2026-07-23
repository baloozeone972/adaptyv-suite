"""Foundry API client — wire-compatible with `adaptyvbio/adaptyv-sdk`'s real contract.

Verified against the SDK's actual source (`client/foundry.py` + its generated
types, 2026-07) rather than assumed: endpoint paths, payload/response shapes,
and enum values below match the real API. Deliberately out of scope — because
none of this suite's tools need them — are targets, sequences-as-a-resource,
quotes-as-a-list-resource, feedback, and info/health; see
`adaptyv-core/docs/limitations.md` for the full comparison.

The client depends on a `Transport` protocol, not a concrete HTTP library, so
every code path is testable offline against a fake transport. BYOK: the token
comes from the caller and is never logged.

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

from pydantic import BaseModel, Field

from adaptyv_core.schemas import AssayType, Method


class ExperimentStatus(StrEnum):
    """The real experiment lifecycle (`adaptyv-sdk`'s `ExperimentStatus`, verified)."""

    DRAFT = "draft"
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"
    CANCELED = "canceled"
    WAITING_FOR_MATERIALS = "waiting_for_materials"
    IN_PRODUCTION = "in_production"
    QUOTE_SENT = "quote_sent"
    IN_QUEUE = "in_queue"
    DATA_ANALYSIS = "data_analysis"
    IN_REVIEW = "in_review"
    DONE = "done"


class AssayRequest(BaseModel):
    """A request to run an assay on a set of sequences.

    This suite's convenience shape; `_experiment_spec()` maps it onto the real
    wire format (`ExperimentSpec`) at the client boundary.
    """

    experiment_type: AssayType
    sequences: dict[str, str]  # name -> sequence
    target_id: str | None = None
    replicates: int = 2
    method: Method | None = None


class CostEstimate(BaseModel):
    """A cost estimate, converted from the real API's integer cents to USD."""

    experiment_type: AssayType
    n_sequences: int
    total_usd: float
    incomplete: bool = False  # True if pricing was partial (see `warnings`)
    warnings: list[str] = Field(default_factory=list)


class ExperimentHandle(BaseModel):
    """A live experiment reference."""

    experiment_id: str
    status: ExperimentStatus


class AttenuationScope(BaseModel):
    """A narrowed permission set for a derived token (real API: `AttenuationSpec`).

    Attenuation is append-only and cryptographically enforced by the real API:
    it can only narrow what a token may do, never expand it.
    """

    allowed_actions: list[str] | None = None
    allowed_resources: list[str] | None = None
    allowed_org_ids: list[str] | None = None


class Transport(Protocol):
    """Minimal HTTP surface the client needs. Implementations may be fake."""

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]: ...
    def get(self, path: str, token: str) -> dict[str, object]: ...
    def get_bytes(self, path: str, token: str) -> bytes: ...
    def fetch_url(self, url: str) -> bytes: ...  # no auth header: pre-signed download links


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


def _experiment_spec(request: AssayRequest) -> dict[str, object]:
    """Build the real `ExperimentSpec` wire payload from this suite's `AssayRequest`.

    `method` is lowercased here only: the shared `Method` enum's values
    (`"BLI"`/`"SPR"`) match the downloaded data package's CSV convention
    (`aux/replicate_info.csv`, verified against the live docs separately); the
    live REST API's JSON schema uses lowercase (`"bli"`/`"spr"`) instead. Both
    conventions are real; this is the one place they're reconciled.
    """
    spec: dict[str, object] = {
        "experiment_type": request.experiment_type.value,
        "sequences": dict(request.sequences),
        "n_replicates": request.replicates,
    }
    if request.target_id is not None:
        spec["target_id"] = request.target_id
    if request.method is not None:
        spec["method"] = request.method.value.lower()
    return spec


def _cost_from_response(request: AssayRequest, data: dict[str, object]) -> CostEstimate:
    """Parse `CostEstimateResponse`: either a `breakdown` or an `incomplete` estimate."""
    breakdown = data.get("breakdown")
    incomplete = data.get("incomplete")
    raw_warnings = data.get("warnings")
    warnings = [str(w) for w in raw_warnings] if isinstance(raw_warnings, list) else []
    if breakdown is not None:
        total_cents = int(breakdown["total_cents"])  # type: ignore[index]
        is_incomplete = False
    elif incomplete is not None:
        total_cents = int(incomplete["total_cents"])  # type: ignore[index]
        is_incomplete = True
    else:  # pragma: no cover - the real API always sends one or the other
        raise ValueError("cost-estimate response has neither 'breakdown' nor 'incomplete'")
    return CostEstimate(
        experiment_type=request.experiment_type,
        n_sequences=len(request.sequences),
        total_usd=round(total_cents / 100.0, 2),
        incomplete=is_incomplete,
        warnings=warnings,
    )


class FoundryClient:
    """Typed client matching the real Foundry wire contract. Never logs the token.

    Scope: cost estimation, the experiment lifecycle (create / submit / confirm
    quote / get / list results) and token attenuation — everything this suite's
    tools need. See the module docstring for what is deliberately not covered.
    """

    def __init__(self, transport: Transport, token: str) -> None:
        self._t = transport
        self._token = token

    def cost_estimate(self, request: AssayRequest) -> CostEstimate:
        """POST /experiments/cost-estimate. Call this before any spend."""
        data = self._t.post(
            "/experiments/cost-estimate",
            {"experiment_spec": _experiment_spec(request)},
            self._token,
        )
        return _cost_from_response(request, data)

    def create_experiment(
        self, request: AssayRequest, name: str, *, auto_confirm: bool = False
    ) -> ExperimentHandle:
        """POST /experiments.

        `auto_confirm=True` sets the real API's `auto_accept_quote` + `skip_draft`
        flags, which accept the quote and create the invoice in this same call —
        the one-shot path the real API documents for "fully automated experiment
        submission pipelines". This suite's guard and pipeline use exactly this
        path, so spending happens at one call the guard can gate atomically.
        """
        payload: dict[str, object] = {"name": name, "experiment_spec": _experiment_spec(request)}
        if auto_confirm:
            payload["auto_accept_quote"] = True
            payload["skip_draft"] = True
        data = self._t.post("/experiments", payload, self._token)
        return self.get_experiment(str(data["experiment_id"]))

    def submit_experiment(self, experiment_id: str) -> ExperimentHandle:
        """POST /experiments/{id}/submit — advance a draft to a sent quote."""
        self._t.post(f"/experiments/{experiment_id}/submit", {}, self._token)
        return self.get_experiment(experiment_id)

    def confirm_quote(self, experiment_id: str) -> ExperimentHandle:
        """POST /experiments/{id}/quote/confirm — accept the quote and pay."""
        self._t.post(f"/experiments/{experiment_id}/quote/confirm", {}, self._token)
        return self.get_experiment(experiment_id)

    def get_experiment(self, experiment_id: str) -> ExperimentHandle:
        """GET /experiments/{id}."""
        data = self._t.get(f"/experiments/{experiment_id}", self._token)
        status = str(data["status"])
        return ExperimentHandle(experiment_id=str(data["id"]), status=ExperimentStatus(status))

    def list_results(self, experiment_id: str) -> list[dict[str, object]]:
        """GET /experiments/{id}/results — paginated; returns this page's items."""
        data = self._t.get(f"/experiments/{experiment_id}/results", self._token)
        items = data.get("items", [])
        if not isinstance(items, list):  # pragma: no cover - defensive, real API always a list
            raise TypeError("expected 'items' to be a list")
        return [dict(item) for item in items]

    def download_package(self, experiment_id: str, dest: str | Path) -> Path:
        """Find the result carrying `data_package_url` and download it there.

        Not a direct Foundry endpoint: the real API surfaces the package as a
        URL field on a result (`ResultInfo.data_package_url`, "same as in the
        Foundry portal"), reached via `list_results`. That URL is pre-signed
        (same as the portal's own download link), so it is fetched with no
        Foundry auth header — see `Transport.fetch_url`.
        """
        for result in self.list_results(experiment_id):
            url = result.get("data_package_url")
            if url:
                dest = Path(dest)
                dest.write_bytes(self._t.fetch_url(str(url)))
                return dest
        raise LookupError(f"No data_package_url in results for experiment {experiment_id!r}")

    def attenuate_token(
        self, *, name: str, scope: AttenuationScope, parent_token_id: str | None = None
    ) -> str:
        """POST /tokens/attenuate — mint a narrowed, append-only derived token.

        Hand the agent this token instead of the root one: attenuation can only
        narrow access, never expand it (enforced by the token's own format, not
        just server-side policy) — the natural pairing with this suite's `Guard`
        (belt and suspenders: the token can't do it even if the proxy is bypassed).
        """
        payload: dict[str, object] = {
            "token": self._token,
            "name": name,
            "attenuation": scope.model_dump(exclude_none=True),
        }
        if parent_token_id is not None:
            payload["attenuated_parent_token_id"] = parent_token_id
        data = self._t.post("/tokens/attenuate", payload, self._token)
        return str(data["token"])


class HttpTransport:  # pragma: no cover - reaches the network; tested via a fake
    """Thin urllib transport against the real Foundry API."""

    def __init__(self, base_url: str) -> None:
        self._base = base_url.rstrip("/")

    def _request(self, url: str, token: str | None, data: bytes | None) -> bytes:
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(
            url, data=data, headers=headers, method="POST" if data is not None else "GET"
        )
        with urllib.request.urlopen(req) as resp:
            return bytes(resp.read())

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        raw = self._request(self._base + path, token, json.dumps(payload).encode())
        return dict(json.loads(raw))

    def get(self, path: str, token: str) -> dict[str, object]:
        return dict(json.loads(self._request(self._base + path, token, None)))

    def get_bytes(self, path: str, token: str) -> bytes:
        return self._request(self._base + path, token, None)

    def fetch_url(self, url: str) -> bytes:
        return self._request(url, None, None)
