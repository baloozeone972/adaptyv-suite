"""Self-contained HTML drift report."""

from __future__ import annotations

import html
from pathlib import Path

from adaptyv_core.report import ReportBuilder
from adaptyv_core.schemas import DataSource

from mosaic_loop.schemas import DriftReport


def _table(report: DriftReport) -> str:
    rows = [
        "<tr><th>term</th><th>n</th><th>Pearson</th><th>Spearman</th><th>drift</th><th>slope</th></tr>"
    ]
    for c in sorted(report.calibrations, key=lambda x: x.drift):
        flag = " ⚠️" if c.drift > 0.5 else ""
        rows.append(
            f"<tr><td>{html.escape(c.term.value)}{flag}</td><td>{c.n}</td>"
            f"<td>{c.pearson:.2f}</td><td>{c.spearman:.2f}</td>"
            f"<td>{c.drift:.2f}</td><td>{c.slope:.3g}</td></tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def build_report(report: DriftReport, out: Path, source: DataSource = DataSource.SYNTHETIC) -> Path:
    """Render the per-term drift and the objective realignment to HTML."""
    lift = report.objective_agreement_calibrated - report.objective_agreement_raw
    rb = ReportBuilder(title="mosaic-loop — prediction vs measurement drift", source=source)
    rb.add_html(
        f"<p>Objective agreement with reality: raw "
        f"<strong>{report.objective_agreement_raw:.2f}</strong> → calibrated "
        f"<strong>{report.objective_agreement_calibrated:.2f}</strong> ({lift:+.2f}).</p>"
    )
    rb.add_heading("Per-term drift (which predicted terms track reality)")
    rb.add_html(_table(report))
    rb.add_html(
        "<p class='muted'>Drift = 1 - Spearman(predicted, measured). A high-drift term "
        "means Mosaic is optimising a proxy that does not track the measurement — the "
        "single most useful thing to feed back. Synthetic data; declared.</p>"
    )
    out.write_text(rb.render(), encoding="utf-8")
    return out
