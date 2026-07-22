"""Command-line interface for mosaic-loop.

    mosaic-loop analyze --report drift.html

Feeds synthetic Adaptyv measurements back against Mosaic's predicted objective terms,
and reports which terms track reality (low drift) and which do not (high drift).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from mosaic_loop.calibrate import analyze
from mosaic_loop.data import synthetic_measurements
from mosaic_loop.report import build_report

app = typer.Typer(add_completion=False, help="Close Mosaic's loop with Adaptyv measurements.")


@app.callback()
def _main() -> None:  # pragma: no cover - no-op group callback (forces `analyze` subcommand)
    """Close Mosaic's loop with Adaptyv measurements."""


@app.command()
def analyze_cmd(
    n: Annotated[int, typer.Option(help="Number of designs.")] = 120,
    report: Annotated[Path | None, typer.Option(help="Write an HTML report here.")] = None,
    seed: int = 0,
) -> None:
    """Report per-term drift and how much recalibration realigns the objective."""
    result = analyze(synthetic_measurements(n=n, seed=seed))
    for c in sorted(result.calibrations, key=lambda x: x.drift):
        flag = "  <-- poor proxy" if c.drift > 0.5 else ""
        typer.echo(f"{c.term.value:11} Spearman {c.spearman:+.2f}  drift {c.drift:.2f}{flag}")
    typer.echo(
        f"\nObjective agreement with reality: {result.objective_agreement_raw:.2f} raw "
        f"-> {result.objective_agreement_calibrated:.2f} calibrated."
    )
    if report is not None:
        build_report(result, report)
        typer.echo(f"Wrote report to {report}")


# Register the command under the name `analyze`.
app.command(name="analyze")(analyze_cmd)


if __name__ == "__main__":
    app()
