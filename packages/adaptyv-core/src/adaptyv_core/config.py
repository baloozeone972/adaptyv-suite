"""Runtime configuration, sourced exclusively from the environment.

No secret ever lives in code or on disk. The Foundry token is read on demand
and never logged. BYOK ("bring your own key") is the mandated posture.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

_TOKEN_ENV = "ADAPTYVBIO_API_TOKEN"
_API_BASE_ENV = "ADAPTYVBIO_API_BASE"
_DEFAULT_API_BASE = "https://api.adaptyvbio.com"


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable view of the process environment relevant to the suite."""

    api_base: str = _DEFAULT_API_BASE
    # repr=False so the token can never leak into logs or tracebacks.
    _token: str | None = field(default=None, repr=False)

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from environment variables.

        >>> isinstance(Settings.from_env().api_base, str)
        True
        """
        return cls(
            api_base=os.environ.get(_API_BASE_ENV, _DEFAULT_API_BASE),
            _token=os.environ.get(_TOKEN_ENV),
        )

    @property
    def has_token(self) -> bool:
        """Whether a Foundry token is available, without exposing it."""
        return bool(self._token)

    def require_token(self) -> str:
        """Return the token or fail loudly. Never call this in a code path that logs."""
        if not self._token:
            raise RuntimeError(f"No Foundry token found. Set {_TOKEN_ENV} in your environment.")
        return self._token
