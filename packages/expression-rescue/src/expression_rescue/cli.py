"""Command-line interface for expression-rescue.

expression-rescue check   designs.fasta --assay affinity --report report.html
expression-rescue rescue  designs.fasta --out corrected.fasta
expression-rescue estimate designs.fasta --price-per-protein 169
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from adaptyv_core.schemas import AssayType, ProteinDesign
from adaptyv_core.seq.io import read_fasta, write_fasta

from expression_rescue.analyze import analyze_campaign
from expression_rescue.report import build_report

app = typer.Typer(add_completion=False, help="Diagnose and rescue designs that won't express.")


@app.command()
def check(
    fasta: Annotated[Path, typer.Argument(help="FASTA of designs.")],
    assay: Annotated[AssayType | None, typer.Option(help="Target assay type.")] = None,
    has_target: Annotated[bool, typer.Option(help="A target is specified.")] = False,
    report: Annotated[Path | None, typer.Option(help="Write an HTML report here.")] = None,
) -> None:
    """Diagnose developability and print a per-sequence risk summary."""
    campaign = analyze_campaign(read_fasta(fasta), assay=assay, has_target=has_target)
    for r in campaign.per_sequence:
        if not r.valid:
            errs = ", ".join(i.code for i in r.blocking_errors)
            typer.echo(f"BLOCK  {r.name}: {errs}")
            continue
        codes = ", ".join(dict.fromkeys(li.code for li in r.liabilities)) or "clean"
        typer.echo(f"{r.risk_tier.value.upper():6} {r.name} (score {r.risk_score}): {codes}")
    typer.echo(
        f"\n{campaign.n_sequences} sequences — {campaign.n_blocked} blocked, "
        f"{campaign.n_high_risk} high-risk"
    )
    if report is not None:
        build_report(campaign, report)
        typer.echo(f"Wrote report to {report}")


def _parse_interface(spec: str) -> frozenset[int]:
    """Parse a comma-separated list of 1-based positions into 0-based indices."""
    if not spec.strip():
        return frozenset()
    return frozenset(int(p) - 1 for p in spec.split(",") if p.strip())


@app.command()
def rescue(
    fasta: Annotated[Path, typer.Argument(help="FASTA of designs.")],
    out: Annotated[Path, typer.Option(help="Where to write corrected variants.")] = Path(
        "corrected.fasta"
    ),
    interface: Annotated[
        str, typer.Option(help="1-based positions to never mutate, e.g. '10,11,45'.")
    ] = "",
) -> None:
    """Suggest conservative corrected variants for at-risk sequences."""
    campaign = analyze_campaign(
        read_fasta(fasta), suggest=True, interface_positions=_parse_interface(interface)
    )
    corrected: list[ProteinDesign] = []
    for r in campaign.per_sequence:
        for i, variant in enumerate(r.suggested_variants):
            name = (
                f"{r.name}_rescue{i + 1}" if len(r.suggested_variants) > 1 else f"{r.name}_rescue"
            )
            corrected.append(ProteinDesign(name=name, sequence=variant.sequence))
            muts = ", ".join(variant.mutations)
            typer.echo(
                f"{r.name}: {muts} -> risk score {variant.risk_score_before}"
                f" to {variant.risk_score_after} (addresses {', '.join(variant.addressed)})"
            )
    write_fasta(corrected, out)
    typer.echo(f"Wrote {len(corrected)} corrected variants to {out}")


@app.command()
def estimate(
    fasta: Annotated[Path, typer.Argument(help="FASTA of designs.")],
    price_per_protein: Annotated[float, typer.Option(help="Unit price in USD.")] = 169.0,
) -> None:
    """Estimate the spend at risk from high-risk designs."""
    campaign = analyze_campaign(read_fasta(fasta), price_per_protein=price_per_protein)
    typer.echo(
        f"{campaign.n_high_risk} of {campaign.n_sequences} designs are high-risk, "
        f"about ${campaign.estimated_wasted_usd:,.0f} of a run at ${price_per_protein:.0f}/protein."
    )


if __name__ == "__main__":
    app()
