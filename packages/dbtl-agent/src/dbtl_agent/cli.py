"""Command-line interface for dbtl-agent.

    dbtl-agent run --budget 20000 --batch 24 --rounds 6

Runs a governance-first autonomous DBTL campaign against a strict simulated lab:
every round is budget-guarded and audited, selection is anti-monoculture, and the
agent learns which design families bind, round over round.
"""

from __future__ import annotations

from typing import Annotated

import typer
from adaptyv_core.guard import Policy
from adaptyv_core.pricing import price
from adaptyv_core.schemas import AssayType
from binder_triage.pool import synthetic_pool

from dbtl_agent.loop import random_baseline, run_campaign

app = typer.Typer(add_completion=False, help="Governance-first autonomous DBTL loop.")


@app.callback()
def _main() -> None:  # pragma: no cover - no-op group callback (forces `run` subcommand)
    """Governance-first autonomous DBTL loop."""


@app.command()
def run(
    budget: Annotated[float, typer.Option(help="Hard total budget in USD.")] = 20000.0,
    batch: Annotated[int, typer.Option(help="Designs per round.")] = 24,
    rounds: Annotated[int, typer.Option(help="Maximum rounds.")] = 6,
    diversity: Annotated[float, typer.Option(help="Diversity weight (anti-monoculture).")] = 0.4,
    seed: int = 0,
) -> None:
    """Run the closed loop and print per-round learning under a hard budget."""
    pool = synthetic_pool(n_clusters=6, per_cluster=40, seed=seed)
    policy = Policy(
        max_total_usd=budget,
        max_per_call_usd=price(AssayType.AFFINITY, batch).total_usd,
        allowed_assays={AssayType.AFFINITY},
    )
    outcome = run_campaign(
        pool, policy, batch_size=batch, max_rounds=rounds, diversity_weight=diversity, seed=seed
    )
    for r in outcome.rounds:
        typer.echo(
            f"round {r.round}: {r.n_binders:2}/{r.n_submitted} binders "
            f"(hit {r.hit_rate:.0%})  identity {r.mean_pairwise_identity:.2f}  "
            f"families {r.n_families}"
        )
    baseline = random_baseline(pool, batch_size=batch, max_rounds=len(outcome.rounds), seed=seed)
    lift = (outcome.total_binders / baseline - 1.0) if baseline else 0.0
    typer.echo(
        f"\nTotal {outcome.total_binders}/{outcome.total_submitted} binders "
        f"for ${outcome.total_cost_usd:,.0f} of ${outcome.budget_usd:,.0f} "
        f"({outcome.total_binders} vs {baseline} random, {lift:+.0%})."
    )
    typer.echo(
        f"Budget respected: {outcome.budget_respected} · audit valid: {outcome.audit_valid} "
        "(synthetic strict oracle)."
    )


if __name__ == "__main__":
    app()
