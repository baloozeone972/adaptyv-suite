"""Command-line interface for boltz-tune.

    boltz-tune evaluate --target-lift 0.05

Fits a learning curve to a (synthetic, declared) training-size sweep and reports,
honestly, whether fine-tuning helps at the current data volume and how much more data
a target improvement would need.
"""

from __future__ import annotations

from typing import Annotated

import typer

from boltz_tune.curve import evaluate
from boltz_tune.data import BASE_SCORE, synthetic_sweep

app = typer.Typer(add_completion=False, help="Learning-curve harness for affinity fine-tuning.")


@app.callback()
def _main() -> None:  # pragma: no cover - no-op group callback (forces `evaluate` subcommand)
    """Learning-curve harness for affinity fine-tuning."""


@app.command(name="evaluate")
def evaluate_cmd(
    target_lift: Annotated[
        float, typer.Option("--target-lift", help="Desired gain over base.")
    ] = 0.05,
    seed: int = 0,
) -> None:
    """Report the honest verdict on fine-tuning value and the data it would need."""
    result = evaluate(synthetic_sweep(seed=seed), base_score=BASE_SCORE, target_lift=target_lift)
    typer.echo(f"base model score:        {result.base_score:.3f}")
    typer.echo(
        f"at current n={result.current_n}:      {result.current_score:.3f} "
        f"({result.current_lift:+.3f} vs base)"
    )
    if result.is_finite_multiple():
        typer.echo(f"for +{target_lift:.3f} over base: ~{result.data_multiple:.1f}x more data")
    typer.echo(f"\nVerdict: {result.verdict}")
    typer.echo("(Synthetic learning curve; declared. Real numbers need Adaptyv's data + compute.)")


if __name__ == "__main__":
    app()
