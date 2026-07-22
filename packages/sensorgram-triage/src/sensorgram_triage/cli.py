"""Command-line interface for sensorgram-triage.

    sensorgram-triage calibrate --report report.html
    sensorgram-triage triage package.zip

`calibrate` trains on a synthetic labelled set and prints the delegation curve's
operating point — the metric that matters: how much human review can be removed.
`triage` sorts a real package's curves into green / orange / red.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from adaptyv_kinetics.io.package import DataPackage

from sensorgram_triage.delegation import calibrate
from sensorgram_triage.report import build_report
from sensorgram_triage.triage import triage_traces

app = typer.Typer(add_completion=False, help="Auto-sort binding curves; quantify review saved.")


def _open(path: Path) -> DataPackage:
    return DataPackage.from_zip(path) if path.suffix == ".zip" else DataPackage.from_dir(path)


@app.command(name="calibrate")
def calibrate_cmd(
    max_fnr: Annotated[float, typer.Option("--max-fnr", help="Target false-negative rate.")] = 0.02,
    report: Annotated[Path | None, typer.Option(help="Write an HTML report here.")] = None,
) -> None:
    """Train on synthetic labels and print the delegation operating point."""
    _model, curve = calibrate()
    op = curve.operating_point(max_fnr)
    typer.echo(
        f"Held-out n={curve.n}, Brier={curve.brier_score:.3f}. "
        f"At FNR <= {max_fnr:.0%}: {op.auto_approved_fraction:.0%} auto-approved "
        f"(threshold {op.threshold:.2f})."
    )
    if report is not None:
        build_report(curve, [], report, max_fnr=max_fnr)
        typer.echo(f"Wrote report to {report}")


@app.command()
def triage(
    package: Annotated[Path, typer.Argument(help="Package .zip or directory.")],
    max_fnr: Annotated[float, typer.Option("--max-fnr")] = 0.02,
    report: Annotated[Path | None, typer.Option(help="Write an HTML report here.")] = None,
) -> None:
    """Sort a package's curves into green / orange / red."""
    model, curve = calibrate()
    results = triage_traces(_open(package).traces(), model)
    for r in results:
        reasons = ", ".join(r.reasons) or "clean"
        head = f"{r.pile.value.upper():6} {r.name} rep{r.replicate}"
        typer.echo(f"{head} (p={r.needs_review_prob:.2f}): {reasons}")
    if report is not None:
        build_report(curve, results, report, max_fnr=max_fnr)
        typer.echo(f"Wrote report to {report}")


if __name__ == "__main__":
    app()
