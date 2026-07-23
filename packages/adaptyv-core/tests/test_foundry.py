"""Tests for the Foundry client and webhook verification, via a fake transport.

The fake transport returns payloads shaped like the *real* API (verified against
`adaptyvbio/adaptyv-sdk`'s source): cost in `total_cents` under a `breakdown` or
`incomplete` envelope, `experiment_id` from create vs `id` from get, results as a
paginated `{"items": [...]}` envelope with `data_package_url`, and real
`ExperimentStatus` values (lowercase snake_case).
"""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

import pytest
from adaptyv_core.foundry import (
    AssayRequest,
    AttenuationScope,
    ExperimentStatus,
    FoundryClient,
    verify_webhook,
)
from adaptyv_core.schemas import AssayType, Method


class FakeTransport:
    """Records calls and returns canned, real-shaped responses."""

    def __init__(self, incomplete: bool = False) -> None:
        self.calls: list[tuple[str, str]] = []
        self.incomplete = incomplete
        self._status = "waiting_for_materials"

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        self.calls.append(("POST", path))
        if path.endswith("cost-estimate"):
            spec = payload["experiment_spec"]  # type: ignore[index]
            n = len(spec["sequences"])  # type: ignore[index, arg-type]
            if self.incomplete:
                return {
                    "incomplete": {"assay": {}, "pricing_version": "v1", "total_cents": 100 * n}
                }
            return {"breakdown": {"assay": {}, "pricing_version": "v1", "total_cents": 169_00 * n}}
        if path == "/experiments":
            self._status = "waiting_for_materials" if payload.get("auto_accept_quote") else "draft"
            return {"experiment_id": "exp-1"}
        if path.endswith("/submit"):
            self._status = "quote_sent"
            return {}
        if path.endswith("/quote/confirm"):
            self._status = "waiting_for_materials"
            return {}
        if path == "/tokens/attenuate":
            return {"id": "tok-rec-1", "token": "abs0_narrowed"}
        raise AssertionError(f"unexpected POST {path}")  # pragma: no cover

    def get(self, path: str, token: str) -> dict[str, object]:
        self.calls.append(("GET", path))
        if path.endswith("/results"):
            return {
                "items": [{"id": "res-1", "data_package_url": "https://signed.example/pkg.zip"}],
                "total": 1,
                "count": 1,
                "offset": 0,
            }
        return {"id": "exp-1", "status": self._status}

    def get_bytes(self, path: str, token: str) -> bytes:  # pragma: no cover - unused here
        return b""

    def fetch_url(self, url: str) -> bytes:
        self.calls.append(("FETCH_URL", url))
        return b"PKGDATA"


def _request() -> AssayRequest:
    return AssayRequest(experiment_type=AssayType.AFFINITY, sequences={"a": "AAAA", "b": "BBBB"})


def test_cost_estimate() -> None:
    est = FoundryClient(FakeTransport(), "tok").cost_estimate(_request())
    assert est.n_sequences == 2
    assert est.total_usd == 338.0
    assert not est.incomplete


def test_cost_estimate_incomplete() -> None:
    est = FoundryClient(FakeTransport(incomplete=True), "tok").cost_estimate(_request())
    assert est.incomplete
    assert est.total_usd == 2.0


def test_method_lowercased_for_the_wire(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}
    transport = FakeTransport()
    original_post = transport.post

    def spy_post(path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path.endswith("cost-estimate"):
            seen["method"] = payload["experiment_spec"]["method"]  # type: ignore[index]
        return original_post(path, payload, token)

    monkeypatch.setattr(transport, "post", spy_post)
    request = AssayRequest(
        experiment_type=AssayType.AFFINITY, sequences={"a": "AAAA"}, method=Method.BLI
    )
    FoundryClient(transport, "tok").cost_estimate(request)
    assert seen["method"] == "bli"  # CSV convention is "BLI"; the wire convention is lowercase


def test_create_experiment_auto_confirm_advances_status() -> None:
    client = FoundryClient(FakeTransport(), "tok")
    handle = client.create_experiment(_request(), "exp name", auto_confirm=True)
    assert handle.experiment_id == "exp-1"
    assert handle.status == ExperimentStatus.WAITING_FOR_MATERIALS


def test_create_experiment_without_auto_confirm_stays_draft() -> None:
    handle = FoundryClient(FakeTransport(), "tok").create_experiment(_request(), "exp name")
    assert handle.status == ExperimentStatus.DRAFT


def test_submit_then_confirm_quote_lifecycle() -> None:
    client = FoundryClient(FakeTransport(), "tok")
    handle = client.create_experiment(_request(), "exp name")
    assert handle.status == ExperimentStatus.DRAFT
    submitted = client.submit_experiment(handle.experiment_id)
    assert submitted.status == ExperimentStatus.QUOTE_SENT
    confirmed = client.confirm_quote(handle.experiment_id)
    assert confirmed.status == ExperimentStatus.WAITING_FOR_MATERIALS


def test_get_experiment() -> None:
    handle = FoundryClient(FakeTransport(), "tok").get_experiment("exp-1")
    assert handle.experiment_id == "exp-1"


def test_list_results() -> None:
    results = FoundryClient(FakeTransport(), "tok").list_results("exp-1")
    assert results[0]["data_package_url"] == "https://signed.example/pkg.zip"


def test_download_package_follows_data_package_url(tmp_path: Path) -> None:
    transport = FakeTransport()
    dest = FoundryClient(transport, "tok").download_package("exp-1", tmp_path / "p.zip")
    assert dest.read_bytes() == b"PKGDATA"
    assert ("FETCH_URL", "https://signed.example/pkg.zip") in transport.calls


def test_download_package_raises_without_a_result(tmp_path: Path) -> None:
    class _NoResultsTransport(FakeTransport):
        def get(self, path: str, token: str) -> dict[str, object]:
            if path.endswith("/results"):
                return {"items": [], "total": 0, "count": 0, "offset": 0}
            return super().get(path, token)

    with pytest.raises(LookupError, match="No data_package_url"):
        FoundryClient(_NoResultsTransport(), "tok").download_package("exp-1", tmp_path / "p.zip")


def test_attenuate_token_returns_narrowed_token() -> None:
    scope = AttenuationScope(allowed_actions=["read"], allowed_resources=["experiment"])
    token = FoundryClient(FakeTransport(), "root-tok").attenuate_token(name="agent-1", scope=scope)
    assert token == "abs0_narrowed"


def test_attenuate_chained_token_includes_parent_id() -> None:
    seen: dict[str, object] = {}
    transport = FakeTransport()
    original_post = transport.post

    def spy_post(path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path == "/tokens/attenuate":
            seen.update(payload)
        return original_post(path, payload, token)

    transport.post = spy_post  # type: ignore[method-assign]
    scope = AttenuationScope(allowed_actions=["read"])
    FoundryClient(transport, "root-tok").attenuate_token(
        name="chained", scope=scope, parent_token_id="parent-1"
    )
    assert seen["attenuated_parent_token_id"] == "parent-1"


def test_target_id_included_in_wire_spec_when_set() -> None:
    seen: dict[str, object] = {}
    transport = FakeTransport()
    original_post = transport.post

    def spy_post(path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path.endswith("cost-estimate"):
            seen.update(payload["experiment_spec"])  # type: ignore[arg-type]
        return original_post(path, payload, token)

    transport.post = spy_post  # type: ignore[method-assign]
    request = AssayRequest(
        experiment_type=AssayType.AFFINITY, sequences={"a": "AAAA"}, target_id="target-xyz"
    )
    FoundryClient(transport, "tok").cost_estimate(request)
    assert seen["target_id"] == "target-xyz"


def test_cost_estimate_and_create_hit_distinct_paths() -> None:
    t = FakeTransport()
    client = FoundryClient(t, "tok")
    client.cost_estimate(_request())
    client.create_experiment(_request(), "exp name")
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


@pytest.mark.parametrize(
    "status",
    [
        "draft",
        "waiting_for_confirmation",
        "canceled",
        "waiting_for_materials",
        "in_production",
        "quote_sent",
        "in_queue",
        "data_analysis",
        "in_review",
        "done",
    ],
)
def test_status_enum_values(status: str) -> None:
    assert ExperimentStatus(status)
