"""Reproducible HTML report: which in-silico score predicts wet-lab outcome."""

from __future__ import annotations

import html
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from adaptyv_core.report import ReportBuilder
from adaptyv_core.schemas import DataSource

from insilico_bench.schemas import MetricReport


def _hitrate_png(pooled: list[MetricReport], base_rate: float) -> bytes:
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for report in pooled:
        ks = sorted(report.hit_rate_at_k)
        values = [report.hit_rate_at_k[k].value for k in ks]
        lo = [report.hit_rate_at_k[k].value - report.hit_rate_at_k[k].ci_low for k in ks]
        hi = [report.hit_rate_at_k[k].ci_high - report.hit_rate_at_k[k].value for k in ks]
        ax.errorbar(ks, values, yerr=[lo, hi], marker="o", capsize=3, label=report.score_name)
    ax.axhline(base_rate, ls="--", color="#8886", label="random baseline")
    ax.set_xlabel("budget k (top-k by score)")
    ax.set_ylabel("hit rate (fraction binders)")
    ax.set_title("Hit rate @ k, by in-silico score")
    ax.legend(fontsize=8)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    return buf.getvalue()


def _auc_table(pooled: list[MetricReport]) -> str:
    rows = ["<tr><th>score</th><th>AUC-ROC</th><th>AUC-PR</th><th>Spearman rho (pK_D)</th></tr>"]
    for r in sorted(pooled, key=lambda x: x.auc_roc.value, reverse=True):
        rows.append(
            f"<tr><td>{html.escape(r.score_name)}</td><td>{r.auc_roc.as_row()}</td>"
            f"<td>{r.auc_pr.as_row()}</td><td>{r.spearman_pkd.as_row()}</td></tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def build_report(
    reports: list[MetricReport],
    base_rate: float,
    out: Path,
    source: DataSource = DataSource.SYNTHETIC,
) -> Path:
    """Render the benchmark to a self-contained, regenerable HTML file."""
    pooled = [r for r in reports if r.cohort == "pooled"]
    best = max(pooled, key=lambda r: r.auc_roc.value)
    rb = ReportBuilder(title="insilico-bench — score vs wet-lab", source=source)
    rb.add_html(
        f"<p>Base binder rate {base_rate:.0%}. Best discriminator: "
        f"<strong>{html.escape(best.score_name)}</strong> "
        f"(AUC-ROC {best.auc_roc.as_row()}).</p>"
    )
    rb.add_heading("Hit rate @ budget")
    rb.add_png(_hitrate_png(pooled, base_rate), caption="higher is better; random baseline dashed")
    rb.add_heading("Discrimination and affinity (pooled)")
    rb.add_html(_auc_table(pooled))
    if any(r.small_n_warning for r in reports):
        rb.add_html("<p class='muted'>⚠️ Some cohorts have small n; read those CIs with care.</p>")
    out.write_text(rb.render(), encoding="utf-8")
    return out
