"""Assemble the self-contained HTML QC report."""

from __future__ import annotations

import html
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from adaptyv_core.report import ReportBuilder
from adaptyv_core.schemas import DataSource

from adaptyv_kinetics.report.plots import plot_replicate
from adaptyv_kinetics.schemas import Trace, TraceVerdict

if TYPE_CHECKING:
    from adaptyv_kinetics.io.package import DataPackage

_MAX_PLOTS = 8


def _verdict_table(verdicts: list[TraceVerdict]) -> str:
    rows = ["<tr><th>name</th><th>rep</th><th>verdict</th><th>KD (nM)</th><th>flags</th></tr>"]
    for v in verdicts:
        kd = f"{v.fit.kd_M * 1e9:.3g}" if v.fit else "—"
        flags = ", ".join(f.code for f in v.flags) or "—"
        rows.append(
            f"<tr><td>{html.escape(v.name)}</td><td>{v.replicate}</td>"
            f"<td class='{v.verdict.value}'>{v.verdict.value}</td>"
            f"<td>{kd}</td><td>{html.escape(flags)}</td></tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _fmt(value: object) -> str:
    return f"{value:.3g}" if isinstance(value, float) else ("—" if value is None else str(value))


def _compare_table(frame: pl.DataFrame) -> str:
    cols = ["name", "replicate", "kd_nM_refit", "rmax_refit", "rmax_reported", "rmax_pct_diff"]
    header = "".join(f"<th>{c}</th>" for c in cols)
    rows = [f"<tr>{header}</tr>"]
    for row in frame.iter_rows(named=True):
        cells = "".join(f"<td>{_fmt(row[c])}</td>" for c in cols)
        rows.append(f"<tr>{cells}</tr>")
    return f"<table>{''.join(rows)}</table>"


def _group(traces: list[Trace]) -> dict[tuple[str, int], list[Trace]]:
    groups: dict[tuple[str, int], list[Trace]] = defaultdict(list)
    for tr in traces:
        if not tr.is_control:
            groups[(tr.name, tr.replicate)].append(tr)
    return groups


def build_report(
    package: DataPackage, out: Path, bootstrap: int = 200, source: DataSource = DataSource.SYNTHETIC
) -> Path:
    """Render the QC report for a package and write it to `out`."""
    verdicts = package.qc(bootstrap=bootstrap)
    groups = _group(package.traces())
    n = len(verdicts)
    n_reject = sum(v.verdict.value == "reject" for v in verdicts)
    n_review = sum(v.verdict.value == "review" for v in verdicts)

    rb = ReportBuilder(title="adaptyv-kinetics — binding QC report", source=source)
    rb.add_html(
        f"<p>{n} replicates — {n - n_reject - n_review} pass, "
        f"{n_review} review, {n_reject} reject.</p>"
    )
    rb.add_heading("QC verdicts")
    rb.add_html(_verdict_table(verdicts))
    rb.add_heading("Independent verification (re-fit vs package values)")
    rb.add_html(
        "<p class='muted'>Independent re-fit against the values shipped in the package. "
        "Large R<sub>max</sub> differences are expected when the concentration series "
        "does not approach saturation — R<sub>max</sub> is only well determined near "
        "saturation, and the tool surfaces this rather than hiding it.</p>"
    )
    rb.add_html(_compare_table(package.compare_fits()))
    rb.add_heading("Sensorgrams (raw + independent re-fit)")
    for v in verdicts[:_MAX_PLOTS]:
        traces = groups.get((v.name, v.replicate), [])
        if traces and v.fit is not None:
            rb.add_png(plot_replicate(traces, v.fit), caption=f"{v.name} rep {v.replicate}")

    out.write_text(rb.render(), encoding="utf-8")
    return out
