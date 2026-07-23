"""Command-line interface for foundry-guard.

    foundry-guard demo --budget 3000

Runs a scripted sequence of agent requests against a policy and shows the guard
allowing, denying (scope / per-call / budget / approval), and keeping a valid
hash-chained audit — all offline against a fake Foundry.
"""

from __future__ import annotations

from typing import Annotated

import typer
from adaptyv_core.foundry import AssayRequest, FoundryClient
from adaptyv_core.guard import Budget, Guard, Policy
from adaptyv_core.schemas import AssayType

from foundry_guard._demo import DemoTransport
from foundry_guard.proxy import GuardedLab

app = typer.Typer(add_completion=False, help="Guardrail proxy over the Foundry API.")


@app.callback()
def _main() -> None:  # pragma: no cover - no-op group callback (forces `demo` subcommand)
    """Guardrail proxy over the Foundry API."""


def _request(assay: AssayType, n: int) -> AssayRequest:
    return AssayRequest(experiment_type=assay, sequences={f"d{i}": "A" * 60 for i in range(n)})


@app.command()
def demo(
    budget: Annotated[float, typer.Option(help="Total budget in USD.")] = 3000.0,
) -> None:
    """Run a scripted agent session through the guard."""
    policy = Policy(
        max_total_usd=budget,
        max_per_call_usd=2000.0,
        allowed_assays={AssayType.AFFINITY},
        require_approval_over_usd=1500.0,
    )
    guard = Guard(policy=policy, budget=Budget(budget))
    lab = GuardedLab(FoundryClient(DemoTransport(), "demo-token"), guard)

    scenario = [
        ("small affinity (5)", _request(AssayType.AFFINITY, 5)),
        ("out-of-scope expression (5)", _request(AssayType.EXPRESSION, 5)),
        ("over per-call cap (20)", _request(AssayType.AFFINITY, 20)),
        ("needs approval (10)", _request(AssayType.AFFINITY, 10)),
        ("another small affinity (6)", _request(AssayType.AFFINITY, 6)),
    ]
    for label, request in scenario:
        result = lab.submit(request, name=label)
        mark = "ALLOW" if result.allowed else "DENY "
        typer.echo(f"{mark} ${result.amount_usd:>7,.0f}  {label:32} — {result.reason}")

    typer.echo(f"\nSpent ${guard.budget.spent:,.0f} of ${budget:,.0f} (never exceeded).")
    typer.echo(
        f"Audit chain valid: {guard.journal.verify()} ({len(guard.journal.entries())} entries)"
    )


if __name__ == "__main__":
    app()
