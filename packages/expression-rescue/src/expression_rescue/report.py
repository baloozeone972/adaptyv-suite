"""Self-contained HTML report for an expression-risk campaign."""

from __future__ import annotations

import html
from pathlib import Path

from adaptyv_core.report import ReportBuilder
from adaptyv_core.schemas import DataSource

from expression_rescue.schemas import CampaignReport, SequenceReport


def _seq_row(r: SequenceReport) -> str:
    codes = ", ".join(dict.fromkeys(liability.code for liability in r.liabilities)) or "—"
    blocking = ", ".join(i.code for i in r.blocking_errors) or "—"
    return (
        f"<tr><td>{html.escape(r.name)}</td>"
        f"<td class='{r.risk_tier.value}'>{r.risk_tier.value}</td>"
        f"<td>{r.risk_score}</td><td>{html.escape(blocking)}</td>"
        f"<td>{html.escape(codes)}</td></tr>"
    )


def build_report(
    campaign: CampaignReport, out: Path, source: DataSource = DataSource.SYNTHETIC
) -> Path:
    """Render the campaign diagnosis to a self-contained HTML file."""
    rb = ReportBuilder(title="expression-rescue — developability report", source=source)
    rb.add_html(
        f"<p>{campaign.n_sequences} sequences — {campaign.n_blocked} blocked, "
        f"{campaign.n_high_risk} high-risk. Estimated spend at risk: "
        f"<strong>${campaign.estimated_wasted_usd:,.0f}</strong> "
        "(high-risk count times price per protein).</p>"
    )
    rb.add_heading("Per-sequence diagnosis")
    header = (
        "<tr><th>name</th><th>risk tier</th><th>score</th>"
        "<th>blocking</th><th>liabilities</th></tr>"
    )
    rows = "".join(_seq_row(r) for r in campaign.per_sequence)
    rb.add_html(f"<table>{header}{rows}</table>")
    rb.add_html(
        "<p class='muted'>Risk tier is a heuristic from developability rules, not a "
        "calibrated probability. A calibrated P(express) model needs Adaptyv's labelled "
        "expression data. Suggested variants are to consider, not experimentally validated.</p>"
    )
    out.write_text(rb.render(), encoding="utf-8")
    return out
