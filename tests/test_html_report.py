"""Phase 5 tests: Jinja2 + Plotly HTML report."""
from __future__ import annotations

import polars as pl

from reporting.html_report import render_html_report
from schemas.narrative_schema import RiskLevel, RiskNarrative


def test_html_report_contains_expected_elements() -> None:
    df = pl.DataFrame(
        [
            {
                "supplier_id": "SUP-001",
                "supplier_name": "Acme Corp",
                "composite_risk": 0.85,
                "region": "EMEA",
            }
        ]
    )
    narratives = {
        "SUP-001": RiskNarrative(
            supplier_name="Acme Corp",
            overall_risk=RiskLevel.HIGH,
            key_risks=["debt"],
            recommendation="conduct audit",
            confidence=0.9,
        )
    }

    html = render_html_report(df, narratives)

    assert "<html" in html.lower()
    assert "plotly" in html.lower()
    assert "Acme Corp" in html
    assert "conduct audit" in html
