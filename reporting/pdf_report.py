"""
Board-grade executive PDF (FPDF2 2.8+).

Correctives: transliterated unicode safety, full-width right-aligned footer
(no fixed-cell spacing artifacts), page-break guards inside the zebra table,
severity-first narrative ordering, and optional scenario parameter metadata.
"""
from __future__ import annotations

import textwrap
import unicodedata
from datetime import datetime, timezone

import polars as pl
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from schemas.narrative_schema import RiskNarrative
from theme import RISK_RGB, risk_band

_DARK = (11, 18, 32)
_ACCENT = (34, 211, 238)
_INK = (15, 23, 42)
_MUTED = (100, 116, 139)
_LINE = (226, 232, 240)
_ZEBRA = (248, 250, 252)
_SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

_TRANS = str.maketrans({
    "—": "-", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"',
    "≥": ">=", "≤": "<=", "·": "-", "…": "...", "→": "->",
    "€": "EUR ", "£": "GBP ", "₹": "Rs ",
})


def _safe(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value).translate(_TRANS))
    return text.encode("latin-1", "ignore").decode("latin-1")


def _block(value: object, width: int = 88) -> str:
    return textwrap.fill(_safe(value), width=width, break_long_words=True, break_on_hyphens=True)


def _severity_sorted(narratives: dict[str, RiskNarrative], limit: int) -> list[tuple[str, RiskNarrative]]:
    ordered = sorted(
        narratives.items(),
        key=lambda item: (_SEVERITY_ORDER.get(item[1].overall_risk.value, 9), -item[1].confidence),
    )
    return ordered[:limit]


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
        pdf.cell(width - 8, 4, label.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(x + 4, y + 11)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(*_INK)
        pdf.cell(width - 8, 8, _safe(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(y + 25 + 7)


def render_pdf_report(
    scored_df: pl.DataFrame,
    narratives: dict[str, RiskNarrative],
    scenario_name: str = "Default",
    scenario_config: object | None = None,
) -> bytes:
    pdf = _PDFReport()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    effective_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*_INK)
    pdf.cell(0, 8, _safe(f"Scenario: {scenario_name}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_MUTED)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(0, 6, _safe(f"Generated {generated}  ·  Board-ready analysis"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if scenario_config is not None:
        meta = (
            f"Weighting: {getattr(scenario_config, 'weighting', 'balanced')}  ·  "
            f"Risk window: {getattr(scenario_config, 'min_risk_threshold', 0.0):.2f}-"
            f"{getattr(scenario_config, 'max_risk_threshold', 1.0):.2f}  ·  "
            f"Regions: {', '.join(getattr(scenario_config, 'regions', []))}"
        )
        pdf.cell(0, 6, _safe(meta), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    total_suppliers = scored_df.height
    avg_risk = 0.0
    high_risk_count = 0
    critical_count = 0

    if "composite_risk" in scored_df.columns and scored_df.height > 0:
        mean_value = scored_df["composite_risk"].mean()
        avg_risk = float(mean_value) if mean_value is not None else 0.0
        high_risk_count = scored_df.filter(pl.col("composite_risk") >= 0.7).height
        critical_count = scored_df.filter(pl.col("composite_risk") >= 0.85).height

    _section(pdf, "Portfolio Risk Metrics")
    _kpi_row(
        pdf,
        [
            ("Total Entities", f"{total_suppliers:,}", _ACCENT),
            ("Portfolio Risk Index", f"{avg_risk:.3f}", (129, 140, 248)),
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
        if pdf.get_y() > pdf.h - 32:
            pdf.add_page()
            pdf.set_font("Helvetica", "", 8)

        pdf.set_x(pdf.l_margin)
        if row_idx % 2 == 0:
            pdf.set_fill_color(*_ZEBRA)
        else:
            pdf.set_fill_color(255, 255, 255)

        risk_val = float(row.get("composite_risk", 0.0))
        band = risk_band(risk_val)
        band_rgb = RISK_RGB[band]

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

    _section(pdf, "AI Risk Narratives (Top-5)")

    if not narratives:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*_MUTED)
        pdf.cell(0, 7, "No narratives available for this scenario.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        for supplier_id, narrative in _severity_sorted(narratives, 5):
            if pdf.get_y() > pdf.h - 55:
                pdf.add_page()

            band = narrative.overall_risk.value
            band_rgb = RISK_RGB.get(band, _MUTED)
            y0 = pdf.get_y()

            pdf.set_font("Helvetica", "B", 10.5)
            pdf.set_text_color(*_INK)
            pdf.cell(0, 6, _safe(f"{narrative.supplier_name}  //  {supplier_id}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*band_rgb)
            pdf.cell(0, 5.5, _safe(f"[{band}]"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(0, 5, _block(f"Key Risks: {', '.join(narrative.key_risks)}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.multi_cell(0, 5, _block(f"Recommendation: {narrative.recommendation}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.multi_cell(0, 5, _block(f"Confidence: {narrative.confidence:.2f}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            y1 = pdf.get_y()
            pdf.set_fill_color(*band_rgb)
            pdf.rect(12, y0, 1.3, y1 - y0, "F")
            pdf.ln(4)

    return bytes(pdf.output())
