"""Tests for logging configuration."""

from __future__ import annotations

from adaptyv_core.logging import configure, get_logger


def test_configure_json_then_log() -> None:
    configure(json_output=True)
    log = get_logger("test.json")
    log.info("event", key="value", n=1)  # must not raise


def test_configure_console() -> None:
    configure(json_output=False)
    log = get_logger("test.console")
    log.warning("careful")  # must not raise


def test_get_logger_returns_bound_logger() -> None:
    assert get_logger("x") is not None
