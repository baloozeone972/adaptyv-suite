"""Tests for environment-sourced settings, including token safety."""

from __future__ import annotations

import pytest
from adaptyv_core.config import Settings


def test_defaults_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADAPTYVBIO_API_TOKEN", raising=False)
    monkeypatch.delenv("ADAPTYVBIO_API_BASE", raising=False)
    s = Settings.from_env()
    assert s.api_base.startswith("https://")
    assert not s.has_token


def test_require_token_raises_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADAPTYVBIO_API_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        Settings.from_env().require_token()


def test_token_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADAPTYVBIO_API_TOKEN", "s3cr3t")
    s = Settings.from_env()
    assert s.has_token
    assert s.require_token() == "s3cr3t"


def test_custom_api_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADAPTYVBIO_API_BASE", "https://example.test")
    assert Settings.from_env().api_base == "https://example.test"


def test_error_message_never_leaks_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADAPTYVBIO_API_TOKEN", "TOP_SECRET_VALUE")
    s = Settings.from_env()
    # repr / str of settings must not expose the token value.
    assert "TOP_SECRET_VALUE" not in repr(s)
