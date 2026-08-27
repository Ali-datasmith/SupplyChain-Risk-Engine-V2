"""
Board-grade executive PDF report.

Fixes:
- Narrative severity bar no longer overlaps text.
- Narrative blocks are rendered as proper cards with left padding.
- Severity colors are preserved through clean badges and edge bars.
- Footer avoids fixed-width spacing artifacts.
- Unicode is safely transliterated for core PDF fonts.
"""
from __future__ import annotations

import math
import textwrap
import unicodedata
from datetime import datetime, timezone
from typing import Any

import polars as pl
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from schemas.narrative_schema import RiskNarrative
from theme import RISK_RGB, risk_band

_DARK = (11, 18, 32)
_ACCENT = (34, 211, 238)
_ACCENT_2 = (129, 140, 248)
_INK = (15, 23, 42)
_MUTED = (100, 116, 139)
_LINE = (226, 232, 240)
_ZEBRA = (248, 250, 252)
_CARD_BG = (248, 250, 252)

_SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}

_TRANS = str.maketrans(
    {
        "—": "-",
        "–": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "≥": ">=",
        "≤": "<=",
        "·": "-",
        "…": "...",
        "→": "->",
        "€": "EUR ",
        "£": "GBP ",
        "₹": "Rs ",
    }
)


def _safe(value: object) -> str:
    """FPDF core fonts are latin-1; transliterate instead of silently mangling."""
    text = unicodedata.normalize("NFKD", str(value).translate(_TRANS))
    return text.encode("latin-1", "ignore").decode("latin-1")


def _wrap(value: object, width: int = 90) -> str:
    return textwrap.fill(
        _safe(value),
        width=width,
        break_long_words=True,
        break_on_hyphens=True,
    )


def _estimated_lines(value: object, width: int = 92) -> int:
    text = _safe(value)
    if not text:
        return 1
    return max(1, math.ceil(len(text) / width))


def _severity_sorted(narratives: dict[str, RiskNarrative], limit: int = 5) -> list[tuple[str, RiskNarrative]]:
    return sorted(
        narratives.items(),
        key=lambda item: (
            _SEVERITY_ORDER.get(item[1].overall_risk.value, 9),
            -float(item[1].confidence),
        ),
    )[:limit]


def _badge_text_rgb(band: str) -> tuple[int, int, int]:
    """Readable text color for colored badges."""
    if band in {"LOW", "MEDIUM"}:
        return (15, 23, 42)
    return (255, 255, 255)


class _PDFReport(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            self.set_fill_color(*_DARK)
            self.rect(0, 0, self.w, 34, "F")

            self.set_fill_color(*_ACCENT)
            self.rect(0, 34, self.w, 1.4, "F")

            self.set_xy(12, 9)
            self.set_text_color(230, 237, 246)
            self.set_font("Helvetica", "B", 15)
            self.cell(0, 7, "SUPPLY CHAIN RISK ENGINE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_text_color(148, 163, 184)
            self.set_font("Helvetica", "", 9.5)
            self.cell(0, 6, "Executive Risk Briefing  //  V2.1", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_y(42)
        else:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*_MUTED)
            self.cell(0, 6, "SUPPLY CHAIN RISK ENGINE  //  EXECUTIVE BRIEFING", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(*_LINE)
            self.line(12, self.get_y(), self.w - 12, self.get_y())
            self.ln(5)

    def footer(self) -> None:
        self.set_y(-16)
        self.set_draw_color(*_LINE)
        self.line(12, self.get_y(), self.w - 12, self.get_y())

        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*_MUTED)
        self.cell(110, 6, "CONFIDENTIAL - INTERNAL DISTRIBUTION ONLY")
        self.cell(0, 6, f"Page {self.page_no()}/{{nb}}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _section(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(*_INK)
    pdf.cell(0, 7, _safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_fill_color(*_ACCENT)
    pdf.rect(12, pdf.get_y(), 26, 1.1, "F")
    pdf.ln(5)


def _kpi_row(pdf: FPDF, items: list[tuple[str, str, tuple[int, int, int]]]) -> None:
    gap = 4
    n = len(items)
    width = (pdf.w - 24 - gap * (n - 1)) / n
    y = pdf.get_y()

    if y > pdf.h - 48:
        pdf.add_page()
        y = pdf.get_y()

    for i, (label, value, rgb) in enumerate(items):
        x = 12 + i * (width + gap)

        pdf.set_fill_color(*_ZEBRA)
        pdf.set_draw_color(*_LINE)
        pdf.rect(x, y, width, 25, "DF")

        pdf.set_fill_color(*rgb)
        pdf.rect(x, y, width, 1.4, "F")

        pdf.set_xy(x + 4, y + 5)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(width - 8, 4, _safe(label.upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(x + 4, y + 11)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(*_INK)
        pdf.cell(width - 8, 8, _safe(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(y + 32)


def _draw_risk_badge(pdf: FPDF, band: str, x: float, y: float) -> None:
    rgb = RISK_RGB.get(band, _MUTED)
    text_rgb = _badge_text_rgb(band)

    pdf.set_fill_color(*rgb)
    pdf.set_text_color(*text_rgb)
    pdf.set_font("Helvetica", "B", 7.5)

    badge_w = 24 if band != "CRITICAL" else 30
    pdf.set_xy(x, y)
    pdf.cell(badge_w, 5.5, _safe(band), align="C", fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)


def _draw_narrative_card(pdf: FPDF, supplier_id: str, narrative: RiskNarrative) -> None:
    """
    Draw a narrative card with a colored severity edge bar.

    Important layout fix:
    - Bar lives at card_x.
    - All text starts at content_x = card_x + 7.
    - Therefore the bar cannot strike/overlap text.
    """
    band = narrative.overall_risk.value
    band_rgb = RISK_RGB.get(band, _MUTED)

    card_x = 12
    card_w = pdf.w - 24
    bar_w = 2.0
    content_x = card_x + 7.0
    content_w = card_w - 12.0

    risks = f"Key Risks: {', '.join(narrative.key_risks)}"
    recommendation = f"Recommendation: {narrative.recommendation}"
    confidence = f"Confidence: {narrative.confidence:.2f}"

    risk_lines = _estimated_lines(risks, 92)
    rec_lines = _estimated_lines(recommendation, 92)

    card_h = 10 + 6 + (risk_lines * 5) + (rec_lines * 5) + 7 + 8

    if pdf.get_y() + card_h > pdf.h - 22:
        pdf.add_page()

    y = pdf.get_y()

    # Card background and border.
    pdf.set_fill_color(*_CARD_BG)
    pdf.set_draw_color(*_LINE)
    pdf.rect(card_x, y, card_w, card_h, "DF")

    # Severity bar at the absolute card edge, away from text.
    pdf.set_fill_color(*band_rgb)
    pdf.rect(card_x, y, bar_w, card_h, "F")

    # Title.
    pdf.set_xy(content_x, y + 4)
    pdf.set_font("Helvetica", "B", 10.3)
    pdf.set_text_color(*_INK)
    title = f"{narrative.supplier_name}  //  {supplier_id}"
    pdf.cell(content_w - 35, 5.5, _safe(title)[:115], new_x=XPos.RIGHT, new_y=YPos.TOP)

    # Badge aligned on the right side of the title row.
    _draw_risk_badge(pdf, band, card_x + card_w - 36, y + 4)

    # Risk paragraph.
    pdf.set_xy(content_x, y + 13)
    pdf.set_font("Helvetica", "", 8.8)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(content_w, 4.8, _wrap(risks, 92), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Recommendation paragraph.
    pdf.set_x(content_x)
    pdf.multi_cell(content_w, 4.8, _wrap(recommendation, 92), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Confidence.
    pdf.set_x(content_x)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*_MUTED)
    pdf.cell(content_w, 5.5, _safe(confidence), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(y + card_h + 4)


def render_pdf_report(
    scored_df: pl.DataFrame,
    narratives: dict[str, RiskNarrative],
    scenario_name: str = "Default",
    scenario_config: Any | None = None,
) -> bytes:
    pdf = _PDFReport()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    effective_width = pdf.w - pdf.l_margin - pdf.r_margin

    # Scenario metadata.
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*_INK)
    pdf.cell(0, 8, _safe(f"Scenario: {scenario_name}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_MUTED)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(0, 6, _safe(f"Generated {generated}  -  Board-ready analysis"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if scenario_config is not None:
        weighting = getattr(getattr(scenario_config, "weighting", ""), "value", getattr(scenario_config, "weighting", "balanced"))
        regions = ", ".join(getattr(scenario_config, "regions", []) or [])
        min_risk = getattr(scenario_config, "min_risk_threshold", 0.0)
        max_risk = getattr(scenario_config, "max_risk_threshold", 1.0)
        meta = f"Weighting: {weighting}  -  Risk window: {min_risk:.2f}-{max_risk:.2f}  -  Regions: {regions}"
        pdf.cell(0, 6, _safe(meta), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    total_suppliers = scored_df.height
    avg_risk = 0.0
    high_risk_count = 0
    critical_count = 0

    if "composite_risk" in scored_df.columns and scored_df.height > 0:
        mean_value = scored_df["composite_risk"].mean()
        avg_risk = float(mean_value) if mean_value is not None else 0.0
        high_risk_count = scored_df.filter(pl.col("composite_risk") >= 0.70).height
        critical_count = scored_df.filter(pl.col("composite_risk") >= 0.85).height

    _section(pdf, "Portfolio Risk Metrics")
    _kpi_row(
        pdf,
        [
            ("Total Entities", f"{total_suppliers:,}", _ACCENT),
            ("Portfolio Risk Index", f"{avg_risk:.3f}", _ACCENT_2),
            ("High Exposure", f"{high_risk_count:,}", RISK_RGB["HIGH"]),
            ("Critical Exposure", f"{critical_count:,}", RISK_RGB["CRITICAL"]),
        ],
    )

    _section(pdf, "Top-10 Highest Risk Entities")

    headers = ["Entity ID", "Name", "Risk", "Band", "Region"]
    widths = [
        effective_width * 0.20,
        effective_width * 0.34,
        effective_width * 0.13,
        effective_width * 0.15,
    ]
    widths.append(effective_width - sum(widths))

    if pdf.get_y() > pdf.h - 45:
        pdf.add_page()

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(*_DARK)
    pdf.set_text_color(230, 237, 246)

    for idx, (header, width) in enumerate(zip(headers, widths)):
        new_x = XPos.LMARGIN if idx == len(widths) - 1 else XPos.RIGHT
        new_y = YPos.NEXT if idx == len(widths) - 1 else YPos.TOP
        pdf.cell(width, 8, _safe(header.upper()), border=0, fill=True, new_x=new_x, new_y=new_y)

    pdf.set_font("Helvetica", "", 8)

    top_10 = (
        scored_df.sort("composite_risk", descending=True).head(10)
        if "composite_risk" in scored_df.columns
        else scored_df.head(10)
    )

    for row_idx, row in enumerate(top_10.iter_rows(named=True)):
        if pdf.get_y() > pdf.h - 30:
            pdf.add_page()

            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_fill_color(*_DARK)
            pdf.set_text_color(230, 237, 246)

            for idx, (header, width) in enumerate(zip(headers, widths)):
                new_x = XPos.LMARGIN if idx == len(widths) - 1 else XPos.RIGHT
                new_y = YPos.NEXT if idx == len(widths) - 1 else YPos.TOP
                pdf.cell(width, 8, _safe(header.upper()), border=0, fill=True, new_x=new_x, new_y=new_y)

            pdf.set_font("Helvetica", "", 8)

        pdf.set_x(pdf.l_margin)
        pdf.set_fill_color(*_ZEBRA if row_idx % 2 == 0 else (255, 255, 255))

        risk_val = float(row.get("composite_risk", 0.0))
        band = risk_band(risk_val)
        band_rgb = RISK_RGB.get(band, _MUTED)

        values = [
            str(row.get("supplier_id", ""))[:22],
            str(row.get("supplier_name", ""))[:40],
            f"{risk_val:.3f}",
            band,
            str(row.get("region", ""))[:16],
        ]

        for idx, value in enumerate(values):
            new_x = XPos.LMARGIN if idx == len(values) - 1 else XPos.RIGHT
            new_y = YPos.NEXT if idx == len(values) - 1 else YPos.TOP

            if idx in (2, 3):
                pdf.set_text_color(*band_rgb)
                pdf.set_font("Helvetica", "B", 8)
            else:
                pdf.set_text_color(51, 65, 85)
                pdf.set_font("Helvetica", "", 8)

            pdf.cell(widths[idx], 7, _safe(value), border=0, fill=True, new_x=new_x, new_y=new_y)

    pdf.ln(8)

    _section(pdf, "AI Risk Narratives - Top 5")

    if not narratives:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*_MUTED)
        pdf.cell(0, 7, "No narratives available for this scenario.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        for supplier_id, narrative in _severity_sorted(narratives, 5):
            _draw_narrative_card(pdf, supplier_id, narrative)

    return bytes(pdf.output())
