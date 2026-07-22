"""Self-contained HTML reporting.

Reports embed everything inline (CSS, and images as data URIs) so a single
.html file can be opened or emailed with no external assets. The data source is
always stamped on the report, per the ground rules.
"""

from __future__ import annotations

import base64
import html
from dataclasses import dataclass, field

from adaptyv_core.schemas import DataSource

_CSS = """
:root { color-scheme: light dark; }
body { font: 15px/1.5 -apple-system, system-ui, sans-serif; margin: 2rem auto;
       max-width: 60rem; padding: 0 1rem; }
h1 { font-size: 1.6rem; } h2 { font-size: 1.2rem; margin-top: 2rem; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #8884; padding: .4rem .6rem; text-align: left; }
th { background: #8882; }
.banner { padding: .6rem 1rem; border-radius: .4rem; margin: 1rem 0; font-weight: 600; }
.banner.synthetic { background: #fce4a6; color: #5a3c00; }
.banner.real { background: #cdeccd; color: #14401a; }
.pass { color: #1a7f37; } .review { color: #b26a00; } .reject { color: #cf222e; }
figure { margin: 1rem 0; } img { max-width: 100%; height: auto; }
.muted { color: #8886; font-size: .85rem; }
"""

_SOURCE_TEXT = {
    DataSource.SYNTHETIC: "⚠️ Synthetic data — generated in-repo, not a real measurement.",
    DataSource.REAL: "Real data (Proteinbase / genuine data package).",
    DataSource.FOUNDRY: "Live data from the Foundry API.",
}


@dataclass
class ReportBuilder:
    """Accumulate HTML sections into one self-contained document."""

    title: str
    source: DataSource
    _sections: list[str] = field(default_factory=list)

    def add_html(self, raw_html: str) -> ReportBuilder:
        """Append a raw HTML fragment (caller is responsible for escaping)."""
        self._sections.append(raw_html)
        return self

    def add_heading(self, text: str) -> ReportBuilder:
        """Append an escaped section heading."""
        self._sections.append(f"<h2>{html.escape(text)}</h2>")
        return self

    def add_png(self, png_bytes: bytes, caption: str = "") -> ReportBuilder:
        """Embed a PNG image as a base64 data URI."""
        b64 = base64.b64encode(png_bytes).decode("ascii")
        cap = f"<figcaption class='muted'>{html.escape(caption)}</figcaption>" if caption else ""
        self._sections.append(
            f"<figure><img alt='{html.escape(caption)}' "
            f"src='data:image/png;base64,{b64}'/>{cap}</figure>"
        )
        return self

    def render(self) -> str:
        """Return the complete HTML document as a string."""
        banner_cls = "synthetic" if self.source == DataSource.SYNTHETIC else "real"
        banner = f"<div class='banner {banner_cls}'>{_SOURCE_TEXT[self.source]}</div>"
        body = "\n".join(self._sections)
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{html.escape(self.title)}</title><style>{_CSS}</style></head>"
            f"<body><h1>{html.escape(self.title)}</h1>{banner}{body}</body></html>"
        )
