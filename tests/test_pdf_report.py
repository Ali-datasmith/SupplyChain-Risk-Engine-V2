"""Phase 5 tests: FPDF2 PDF report."""
from __future__ import annotations

import polars as pl

from reporting.pdf_report import render_pdf_report
from schemas.narrative_schema import RiskLevel, RiskNarrative


def test_pdf_report_returns_bytes_with_pdf_header() -> None:
    df = pl.DataFrame(
        [
            {
                "supplier_id": "SUP-001",
                "supplier_name": "Acme",
                "composite_risk": 0.85,
                "region": "EMEA",
            }
        ]
    )
    narratives = {
        "SUP-001": RiskNarrative(
            supplier_name="Acme",
            overall_risk=RiskLevel.HIGH,
            key_risks=["debt"],
            recommendation="audit",
            confidence=0.9,
        )
    }

    pdf_bytes = render_pdf_report(df, narratives)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
