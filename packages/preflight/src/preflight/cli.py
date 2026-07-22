"""Command-line interface for preflight.

    preflight check designs.fasta --assay affinity --has-target
    preflight fix   designs.fasta --out clean.fasta

`check` returns a non-zero exit code when the submission has blocking errors,
so it can gate a design pipeline in CI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from adaptyv_core.schemas import AssayType, ProteinDesign, Severity
from adaptyv_core.seq.io import read_fasta, write_fasta

from preflight.report import PreflightReport, run_preflight

app = typer.Typer(add_completion=False, help="Pre-submission linter for Adaptyv experiments.")

_SEV_MARK = {Severity.CRITICAL: "✗", Severity.WARNING: "!", Severity.INFO: "·"}


def _print_human(report: PreflightReport) -> None:
    for issue in report.campaign_issues:
        typer.echo(f"  {_SEV_MARK[issue.severity]} [campaign] {issue.code}: {issue.message}")
    for design in report.designs:
        header = f"{design.verdict.value.upper():7} {design.name}"
        typer.echo(header)
        for issue in design.issues:
            loc = f" @chain{issue.chain}:{issue.position}" if issue.position is not None else ""
            typer.echo(f"  {_SEV_MARK[issue.severity]} {issue.code}{loc}: {issue.message}")
    typer.echo(
        f"\n{report.n_designs} designs — "
        f"{report.n_pass} pass, {report.n_review} review, {report.n_reject} reject"
    )


@app.command()
def check(
    fasta: Annotated[Path, typer.Argument(help="FASTA file of designs to validate.")],
    assay: Annotated[AssayType | None, typer.Option(help="Target assay type.")] = None,
    has_target: Annotated[bool, typer.Option(help="A target is specified for the run.")] = False,
    output_json: Annotated[bool, typer.Option("--json", help="Emit JSON instead of text.")] = False,
) -> None:
    """Validate a submission; exit non-zero if it contains blocking errors."""
    designs = read_fasta(fasta)
    report = run_preflight(designs, assay=assay, has_target=has_target)
    if output_json:
        typer.echo(json.dumps(report.model_dump(mode="json"), indent=2))
    else:
        _print_human(report)
    raise typer.Exit(code=1 if report.blocking else 0)


def _sanitize_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)


@app.command()
def fix(
    fasta: Annotated[Path, typer.Argument(help="FASTA file to clean.")],
    out: Annotated[Path, typer.Option(help="Where to write the cleaned FASTA.")] = Path(
        "clean.fasta"
    ),
) -> None:
    """Apply safe automatic corrections: drop exact duplicates, sanitize names."""
    designs = read_fasta(fasta)
    seen: set[str] = set()
    cleaned: list[ProteinDesign] = []
    for design in designs:
        if design.residues in seen:
            continue
        seen.add(design.residues)
        cleaned.append(ProteinDesign(name=_sanitize_name(design.name), sequence=design.sequence))
    write_fasta(cleaned, out)
    typer.echo(
        f"Wrote {len(cleaned)} designs to {out} (removed {len(designs) - len(cleaned)} duplicates)"
    )


if __name__ == "__main__":
    app()
