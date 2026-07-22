"""Command-line interface for insilico-bench.

    insilico-bench synth --out designs.csv
    insilico-bench run   designs.csv --out report.html

The report is fully regenerable: point `run` at a new Proteinbase export and get an
updated analysis in one command. `synth` writes a synthetic dataset (declared).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from insilico_bench.analysis import analyze
from insilico_bench.data import load_csv, synthetic_dataset, write_csv
from insilico_bench.report import build_report

app = typer.Typer(
    add_completion=False, help="Measure which in-silico scores predict wet-lab outcome."
)


@app.command()
def synth(
    out: Annotated[Path, typer.Option("--out", "-o")] = Path("designs.csv"),
    seed: int = 0,
) -> None:
    """Write a synthetic Proteinbase-shaped dataset (declared synthetic)."""
    write_csv(synthetic_dataset(seed=seed), out)
    typer.echo(f"Wrote synthetic dataset to {out}")


@app.command()
def run(
    csv: Annotated[Path, typer.Argument(help="Designs CSV (or use `synth` to make one).")],
    out: Annotated[Path, typer.Option("--out", "-o")] = Path("report.html"),
    bootstrap: int = 500,
) -> None:
    """Compute the benchmark and render a reproducible report."""
    records = load_csv(csv)
    base_rate = sum(r.is_binder for r in records) / max(len(records), 1)
    reports = analyze(records, bootstrap=bootstrap)
    pooled = [r for r in reports if r.cohort == "pooled"]
    for r in sorted(pooled, key=lambda x: x.auc_roc.value, reverse=True):
        typer.echo(f"{r.score_name:8} AUC-ROC {r.auc_roc.as_row()}")
    build_report(reports, base_rate, out)
    typer.echo(f"Wrote report to {out}")


if __name__ == "__main__":
    app()
