"""Tests for environment-sourced settings, including token safety."""

from __future__ import annotations

import pytest
from adaptyv_core.config import Settings


def test_defaults_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADAPTYV_API_KEY", raising=False)
    monkeypatch.delenv("ADAPTYV_API_URL", raising=False)
    s = Settings.from_env()
    assert s.api_base.startswith("https://")
    assert not s.has_token


def test_require_token_raises_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADAPTYV_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        Settings.from_env().require_token()


def test_token_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADAPTYV_API_KEY", "s3cr3t")
    s = Settings.from_env()
    assert s.has_token
    assert s.require_token() == "s3cr3t"


def test_custom_api_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADAPTYV_API_URL", "https://example.test")
    assert Settings.from_env().api_base == "https://example.test"


def test_error_message_never_leaks_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADAPTYV_API_KEY", "TOP_SECRET_VALUE")
    s = Settings.from_env()
    # repr / str of settings must not expose the token value.
    assert "TOP_SECRET_VALUE" not in repr(s)
