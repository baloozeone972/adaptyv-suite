"""Self-contained HTML report: the delegation curve and the three piles."""

from __future__ import annotations

import html
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from adaptyv_core.report import ReportBuilder
from adaptyv_core.schemas import DataSource

from sensorgram_triage.schemas import DelegationCurve, TriageResult


def _delegation_png(curve: DelegationCurve, max_fnr: float) -> bytes:
    thresholds = [p.threshold for p in curve.points]
    approved = [p.auto_approved_fraction for p in curve.points]
    fnr = [p.false_negative_rate for p in curve.points]
    op = curve.operating_point(max_fnr)

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(thresholds, approved, label="auto-approved fraction", color="#1a7f37")
    ax.plot(thresholds, fnr, label="false-negative rate", color="#cf222e")
    ax.axvline(op.threshold, ls="--", color="#8886")
    ax.set_xlabel("auto-approval threshold")
    ax.set_ylabel("fraction")
    ax.set_title(f"At FNR ≤ {max_fnr:.0%}: {op.auto_approved_fraction:.0%} auto-approved")
    ax.legend(fontsize=8)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    return buf.getvalue()


def _piles_table(results: list[TriageResult]) -> str:
    rows = ["<tr><th>name</th><th>rep</th><th>pile</th><th>P(review)</th><th>reasons</th></tr>"]
    for r in results:
        reasons = ", ".join(r.reasons) or "—"
        rows.append(
            f"<tr><td>{html.escape(r.name)}</td><td>{r.replicate}</td>"
            f"<td>{r.pile.value}</td><td>{r.needs_review_prob:.2f}</td>"
            f"<td>{html.escape(reasons)}</td></tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def build_report(
    curve: DelegationCurve,
    results: list[TriageResult],
    out: Path,
    max_fnr: float = 0.02,
    source: DataSource = DataSource.SYNTHETIC,
) -> Path:
    """Render the delegation curve and the triage piles to a self-contained HTML file."""
    op = curve.operating_point(max_fnr)
    rb = ReportBuilder(title="sensorgram-triage — delegation report", source=source)
    rb.add_html(
        f"<p>Held-out n={curve.n}, calibration Brier={curve.brier_score:.3f}. "
        f"At a false-negative rate ≤ {max_fnr:.0%}, "
        f"<strong>{op.auto_approved_fraction:.0%}</strong> of curves need no human eye.</p>"
    )
    rb.add_heading("Delegation curve")
    rb.add_png(
        _delegation_png(curve, max_fnr), caption="auto-approved fraction vs false-negative rate"
    )
    rb.add_heading("Triage piles")
    rb.add_html(_piles_table(results))
    out.write_text(rb.render(), encoding="utf-8")
    return out
