"""Structured JSON logging. Libraries never `print`."""

from __future__ import annotations

import structlog


def configure(json_output: bool = True) -> None:
    """Configure structlog once, at application entry points (not in libraries).

    >>> configure(json_output=False)
    >>> get_logger("demo").info("ready")  # doctest: +SKIP
    """
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ]
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a bound logger for the given component name."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
