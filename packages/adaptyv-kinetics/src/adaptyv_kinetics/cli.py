"""Command-line interface for adaptyv-kinetics.

adaptyv-kinetics synth  --out fake_package.zip
adaptyv-kinetics report fake_package.zip -o report.html
adaptyv-kinetics refit  fake_package.zip --out fits.csv
adaptyv-kinetics qc     fake_package.zip --fail-on critical
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from adaptyv_kinetics.io.package import DataPackage
from adaptyv_kinetics.io.synthetic import PackageGenerator
from adaptyv_kinetics.report.export import export_fits

app = typer.Typer(add_completion=False, help="Toolkit for the Adaptyv binding data package.")


def _open(path: Path) -> DataPackage:
    return DataPackage.from_zip(path) if path.suffix == ".zip" else DataPackage.from_dir(path)


@app.command()
def synth(
    out: Annotated[Path, typer.Option("--out", "-o", help="Output .zip path.")] = Path(
        "fake_package.zip"
    ),
    seed: int = 42,
) -> None:
    """Generate a schema-conformant synthetic package for testing/demo."""
    gen = PackageGenerator(seed=seed)
    gen.add_protein("binder_001", kd_nM=13.2, kon=1e5, rmax=0.8, replicates=2)
    gen.add_protein("binder_002", kd_nM=5.0, kon=1.5e5, rmax=0.6, replicates=2)
    gen.add_protein("binder_003", non_binder=True)
    gen.add_protein("binder_004", kd_nM=50.0, kon=1e5, artifacts=["incomplete_dissociation"])
    gen.add_protein("binder_005", kd_nM=20.0, kon=1e5, artifacts=["spike"])
    gen.write_zip(out)
    typer.echo(f"Wrote synthetic package to {out}")


@app.command()
def report(
    package: Annotated[Path, typer.Argument(help="Package .zip or directory.")],
    out: Annotated[Path, typer.Option("--out", "-o")] = Path("report.html"),
    bootstrap: int = 200,
) -> None:
    """Render a self-contained HTML QC report."""
    _open(package).report(out, bootstrap=bootstrap)
    typer.echo(f"Wrote report to {out}")


@app.command()
def refit(
    package: Annotated[Path, typer.Argument(help="Package .zip or directory.")],
    out: Annotated[Path, typer.Option("--out", "-o")] = Path("fits.csv"),
    model: str = "langmuir_1to1",
    bootstrap: int = 200,
) -> None:
    """Independently re-fit every replicate and export the kinetic parameters."""
    fits = _open(package).refit(model=model, bootstrap=bootstrap)
    fmt = out.suffix.lstrip(".") or "csv"
    export_fits(fits, out, fmt=fmt)
    typer.echo(f"Wrote {len(fits)} fits to {out}")


@app.command()
def qc(
    package: Annotated[Path, typer.Argument(help="Package .zip or directory.")],
    fail_on: Annotated[
        str, typer.Option(help="Exit non-zero if any verdict reaches this level.")
    ] = "none",
    bootstrap: int = 200,
) -> None:
    """Print QC verdicts; optionally fail the process on rejects (for CI)."""
    verdicts = _open(package).qc(bootstrap=bootstrap)
    for v in verdicts:
        flags = ", ".join(f.code for f in v.flags) or "clean"
        typer.echo(f"{v.verdict.value.upper():7} {v.name} rep{v.replicate}: {flags}")
    if fail_on == "critical" and any(v.verdict.value == "reject" for v in verdicts):
        raise typer.Exit(code=1)


@app.command()
def compare(
    package: Annotated[Path, typer.Argument(help="Package .zip or directory.")],
    bootstrap: int = 0,
) -> None:
    """Compare the independent re-fit against the package's own reported values."""
    frame = _open(package).compare_fits(bootstrap=bootstrap)
    with pl.Config(tbl_rows=-1, tbl_hide_dataframe_shape=True, tbl_width_chars=200):
        typer.echo(str(frame))


if __name__ == "__main__":
    app()
