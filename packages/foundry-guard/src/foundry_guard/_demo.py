"""An in-process fake Foundry transport, so the guard can be demonstrated offline.

Shaped like the real API's responses (verified against `adaptyv-sdk`'s source):
cost in cents under a `breakdown` envelope, `create` returning only
`experiment_id` (status is fetched separately via `get`), and the real
`ExperimentStatus` values.
"""

from __future__ import annotations

import uuid


class DemoTransport:
    """Returns a cost estimate of $169/sequence and a fresh experiment id."""

    def __init__(self) -> None:
        self._status: dict[str, str] = {}

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path.endswith("cost-estimate"):
            spec = payload["experiment_spec"]
            sequences = spec["sequences"]  # type: ignore[index]
            assert isinstance(sequences, dict)
            return {"breakdown": {"total_cents": 169_00 * len(sequences)}}
        if path == "/experiments":
            exp_id = f"demo-{uuid.uuid4().hex[:6]}"
            self._status[exp_id] = (
                "waiting_for_materials" if payload.get("auto_accept_quote") else "draft"
            )
            return {"experiment_id": exp_id}
        return {}  # pragma: no cover - submit/confirm-quote not exercised by the demo

    def get(self, path: str, token: str) -> dict[str, object]:
        exp_id = path.rsplit("/", 1)[-1]
        return {"id": exp_id, "status": self._status.get(exp_id, "done")}

    def get_bytes(self, path: str, token: str) -> bytes:  # pragma: no cover - unused in demo
        return b""

    def fetch_url(self, url: str) -> bytes:  # pragma: no cover - unused in demo
        return b""
