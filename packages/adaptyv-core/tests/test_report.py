"""Tests for the self-contained HTML report builder."""

from __future__ import annotations

from adaptyv_core.report import ReportBuilder
from adaptyv_core.schemas import DataSource

_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_synthetic_banner_and_structure() -> None:
    html = (
        ReportBuilder(title="T", source=DataSource.SYNTHETIC)
        .add_heading("Section")
        .add_html("<p>body</p>")
        .render()
    )
    assert "<!doctype html>" in html
    assert "Synthetic data" in html
    assert "<h2>Section</h2>" in html


def test_real_source_banner() -> None:
    html = ReportBuilder(title="T", source=DataSource.REAL).render()
    assert "Real data" in html


def test_png_embedded_as_data_uri() -> None:
    html = ReportBuilder(title="T", source=DataSource.REAL).add_png(_PNG, "cap").render()
    assert "data:image/png;base64," in html
    assert "cap" in html


def test_title_escaped() -> None:
    html = ReportBuilder(title="<x>", source=DataSource.REAL).render()
    assert "&lt;x&gt;" in html
