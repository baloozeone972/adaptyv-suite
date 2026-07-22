"""Command-line interface for campaign-planner.

    campaign-planner plan --n 96 --p-express 0.4 --p-bind 0.15 --budget 20000

Ranks strategies (direct vs two-step sequential) by expected binders within budget,
and reports the P(express) below which filtering first is worth its overhead.
"""

from __future__ import annotations

from typing import Annotated

import typer

from campaign_planner.planner import plan, two_step_crossover
from campaign_planner.schemas import Probs

app = typer.Typer(add_completion=False, help="Plan an Adaptyv campaign under a budget.")


@app.callback()
def _main() -> None:  # pragma: no cover - no-op group callback (forces `plan` subcommand)
    """Plan an Adaptyv campaign under a budget."""


@app.command(name="plan")
def plan_cmd(
    n: Annotated[int, typer.Option(help="Number of candidate designs.")] = 96,
    p_express: Annotated[float, typer.Option("--p-express", help="P(expresses).")] = 0.4,
    p_bind: Annotated[float, typer.Option("--p-bind", help="P(binds | expressed).")] = 0.15,
    budget: Annotated[float, typer.Option(help="Budget in USD (0 = no cap).")] = 0.0,
    sims: int = 2000,
) -> None:
    """Rank experiment strategies for a budget and objective."""
    results = plan(n, Probs(p_express=p_express, p_bind=p_bind), budget=budget, sims=sims)
    for r in results:
        typer.echo(r.as_row())
    crossover = two_step_crossover(n)
    if crossover is None:
        typer.echo("\nTwo-step is never cheaper than direct affinity at this size.")
    else:
        typer.echo(
            f"\nTwo-step (expression filter first) is cheaper while P(express) < {crossover:.0%}."
        )


if __name__ == "__main__":
    app()
