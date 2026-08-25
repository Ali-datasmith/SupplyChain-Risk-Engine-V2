"""
Jinja2 + Plotly interactive HTML report (Executive Light palette).

Reports are print-friendly for boards — never use the dark OBSIDIAN theme.
"""
from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import polars as pl
from jinja2 import Environment, FileSystemLoader, select_autoescape

from schemas.narrative_schema import RiskNarrative

TEMPLATE_DIR = Path(__file__).parent / "templates"

# Executive Light palette for the embedded Plotly figure (print-friendly)
_EXEC_PLOTLY = {
    "paper_bgcolor": "#FFFFFF",
    "plot_bgcolor": "#FFFFFF",
    "font": {"family": "'Inter', sans-serif", "color": "#0F172A"},
    "xaxis": {
        "gridcolor": "#E2E8F0",
        "zerolinecolor": "#E2E8F0",
        "color": "#475569",
    },
    "yaxis": {
        "gridcolor": "#E2E8F0",
        "zerolinecolor": "#E2E8F0",
        "color": "#475569",
    },
    "margin": {"l": 0, "r": 0, "t": 24, "b": 24},
}


def render_html_report(
    scored_df: pl.DataFrame,
    narratives: dict[str, RiskNarrative],
    scenario_name: str = "Default",
) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report.html.j2")

    total_suppliers = scored_df.height
    avg_risk = 0.0
    high_risk_count = 0

    if "composite_risk" in scored_df.columns and scored_df.height > 0:
        mean_val = scored_df["composite_risk"].mean()
        avg_risk = float(mean_val) if mean_val is not None else 0.0
        high_risk_count = scored_df.filter(pl.col("composite_risk") >= 0.7).height

    top_10 = (
        scored_df.sort("composite_risk", descending=True).head(10)
        if "composite_risk" in scored_df.columns
        else scored_df.head(10)
    )

    top_10_list = [
        {
            "supplier_id": row.get("supplier_id", ""),
            "supplier_name": row.get("supplier_name", ""),
            "composite_risk": row.get("composite_risk", 0.0),
            "region": row.get("region", ""),
        }
        for row in top_10.iter_rows(named=True)
    ]

    region_data = (
        scored_df.group_by("region")
        .agg(pl.col("composite_risk").mean().alias("avg_risk"))
        .sort("avg_risk", descending=True)
        if "composite_risk" in scored_df.columns and "region" in scored_df.columns
        else pl.DataFrame({"region": [], "avg_risk": []})
    )

    fig = go.Figure(
        data=[
            go.Bar(
                x=region_data["region"].to_list() if region_data.height > 0 else [],
                y=region_data["avg_risk"].to_list() if region_data.height > 0 else [],
                marker_color="#2563EB",
            )
        ]
    )
    fig.update_layout(
        title={"text": "Average Risk by Region", "x": 0, "font": {"size": 13}},
        xaxis_title="Region",
        yaxis_title="Average Composite Risk",
        **_EXEC_PLOTLY,
    )
    plotly_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    top_narratives = sorted(
        narratives.items(),
        key=lambda item: item[1].confidence,
        reverse=True,
    )[:5]

    return template.render(
        scenario_name=scenario_name,
        total_suppliers=total_suppliers,
        avg_risk=avg_risk,
        high_risk_count=high_risk_count,
        top_10=top_10_list,
        plotly_html=plotly_html,
        top_narratives=top_narratives,
    )
