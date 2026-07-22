"""foundry-guard — a guardrail proxy over Adaptyv's Foundry API."""

from foundry_guard.proxy import ApprovalGate, GuardedLab, GuardedResult, auto_deny

__all__ = [
    "ApprovalGate",
    "GuardedLab",
    "GuardedResult",
    "auto_deny",
]
__version__ = "0.0.1"
