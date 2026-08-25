"""
FPDF2 executive PDF report.

Consumes aggregated pl.DataFrame + dict[str, RiskNarrative].
Header/footer, KPI summary, top-10 risk table, narrative section (top-5 suppliers).
Returns bytes.
"""
from __future__ import annotations

import textwrap
import unicodedata

import polars as pl
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from schemas.narrative_schema import RiskNarrative


def _safe(value: object) -> str:
    """Normalize text to latin-1-safe output for core FPDF fonts."""
    text = str(value)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "ignore").decode("latin-1")


def _block(value: object, width: int = 80) -> str:
    """Wrapped, latin-1-safe text block for multi_cell rendering."""
    return textwrap.fill(
        _safe(value),
        width=width,
        break_long_words=True,
        break_on_hyphens=True,
    )


class _PDFReport(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(
            0,
            10,
            _safe("Supply Chain Risk Engine V2 - Executive Report"),
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def render_pdf_report(
    scored_df: pl.DataFrame,
    narratives: dict[str, RiskNarrative],
    scenario_name: str = "Default",
) -> bytes:
    """Render an executive PDF report and return bytes."""
    pdf = _PDFReport()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    effective_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(
        0,
        10,
        _block(f"Scenario: {scenario_name}", width=70),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(2)

    total_suppliers = scored_df.height
    avg_risk = 0.0
    high_risk_count = 0

    if "composite_risk" in scored_df.columns and scored_df.height > 0:
        mean_value = scored_df["composite_risk"].mean()
        avg_risk = float(mean_value) if mean_value is not None else 0.0
        high_risk_count = scored_df.filter(pl.col("composite_risk") >= 0.7).height

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, _safe("KPI Summary"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, _safe(f"Total Suppliers: {total_suppliers}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 7, _safe(f"Average Composite Risk: {avg_risk:.3f}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 7, _safe(f"High-Risk Suppliers (>=0.7): {high_risk_count}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, _safe("Top-10 Highest Risk Suppliers"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "B", 9)

    headers = ["Supplier ID", "Name", "Risk", "Region"]
    widths = [
        effective_width * 0.22,
        effective_width * 0.38,
        effective_width * 0.18,
    ]
    widths.append(effective_width - sum(widths))

    for idx, (header, width) in enumerate(zip(headers, widths)):
        new_x = XPos.LMARGIN if idx == len(widths) - 1 else XPos.RIGHT
        new_y = YPos.NEXT if idx == len(widths) - 1 else YPos.TOP
        pdf.cell(width, 8, _safe(header), border=1, new_x=new_x, new_y=new_y)

    pdf.set_font("Helvetica", "", 8)

    top_10 = (
        scored_df.sort("composite_risk", descending=True).head(10)
        if "composite_risk" in scored_df.columns
        else scored_df.head(10)
    )

    for row in top_10.iter_rows(named=True):
        pdf.set_x(pdf.l_margin)

        values = [
            str(row.get("supplier_id", ""))[:24],
            str(row.get("supplier_name", ""))[:42],
            f"{row.get('composite_risk', 0.0):.3f}",
            str(row.get("region", ""))[:20],
        ]

        for idx, value in enumerate(values):
            new_x = XPos.LMARGIN if idx == len(values) - 1 else XPos.RIGHT
            new_y = YPos.NEXT if idx == len(values) - 1 else YPos.TOP
            pdf.cell(widths[idx], 7, _safe(value), border=1, new_x=new_x, new_y=new_y)

    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, _safe("AI Risk Narratives (Top-5)"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if not narratives:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, _safe("No narratives available."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        top_narratives = sorted(
            narratives.items(),
            key=lambda item: item[1].confidence,
            reverse=True,
        )[:5]

        for supplier_id, narrative in top_narratives:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(
                0,
                7,
                _block(f"Supplier: {narrative.supplier_name} (ID: {supplier_id})", width=75),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(
                0,
                6,
                _block(f"Overall Risk: {narrative.overall_risk.value}", width=80),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.multi_cell(
                0,
                6,
                _block(f"Key Risks: {', '.join(narrative.key_risks)}", width=80),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.multi_cell(
                0,
                6,
                _block(f"Recommendation: {narrative.recommendation}", width=80),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.multi_cell(
                0,
                6,
                _block(f"Confidence: {narrative.confidence:.2f}", width=80),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.ln(3)

    return bytes(pdf.output())
