"""An in-process fake Foundry transport, so the guard can be demonstrated offline."""

from __future__ import annotations

import uuid


class DemoTransport:
    """Returns a cost estimate of $169 per sequence and a fresh experiment id."""

    def post(self, path: str, payload: dict[str, object], token: str) -> dict[str, object]:
        if path.endswith("cost-estimate"):
            sequences = payload["sequences"]
            assert isinstance(sequences, dict)
            return {
                "experiment_type": payload["experiment_type"],
                "n_sequences": len(sequences),
                "total_usd": 169.0 * len(sequences),
            }
        return {"experiment_id": f"demo-{uuid.uuid4().hex[:6]}", "status": "InQueue"}

    def get(self, path: str, token: str) -> dict[str, object]:  # pragma: no cover - unused in demo
        return {"experiment_id": "demo", "status": "Done"}

    def get_bytes(self, path: str, token: str) -> bytes:  # pragma: no cover - unused in demo
        return b""
