"""Command-line interface for binder-triage.

    binder-triage select --k 96 --diversity 0.5

Generates a clustered candidate pool and compares naive top-N against a
diversity-aware selection: expected binders, TRUE binders (synthetic ground truth),
and the monoculture indicator.
"""

from __future__ import annotations

from typing import Annotated

import typer

from binder_triage.evaluate import compare
from binder_triage.pool import synthetic_pool

app = typer.Typer(add_completion=False, help="Constrained, diversity-aware binder selection.")


@app.callback()
def _main() -> None:  # pragma: no cover - no-op group callback (forces `select` subcommand)
    """Constrained, diversity-aware binder selection."""


@app.command()
def select(
    k: Annotated[int, typer.Option(help="Plate budget (designs to select).")] = 24,
    diversity: Annotated[float, typer.Option(help="Diversity weight (0 = pure top-N).")] = 0.8,
    n_clusters: int = 5,
    per_cluster: int = 40,
    seed: int = 0,
) -> None:
    """Compare top-N vs diversity-aware selection on a synthetic clustered pool."""
    pool = synthetic_pool(n_clusters=n_clusters, per_cluster=per_cluster, seed=seed)
    for sel in compare(pool, k, diversity_weight=diversity):
        true = "—" if sel.true_binders is None else f"{sel.true_binders:5.1f}"
        typer.echo(
            f"{sel.strategy:15} ${sel.cost_usd:>7,.0f}  "
            f"expected {sel.expected_binders:5.1f}  true {true}  "
            f"identity {sel.mean_pairwise_identity:.2f}  families {sel.n_clusters}"
        )
    typer.echo("\n(Synthetic pool; 'true binders' is generated ground truth for evaluation.)")


if __name__ == "__main__":
    app()
