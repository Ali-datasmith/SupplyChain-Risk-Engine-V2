"""
GPU-accelerated geospatial rendering via pydeck / deck.gl.

Security: all user-supplied strings are HTML-escaped before entering the
deck.gl tooltip template (stored-XSS vector via uploaded CSVs).
Readability: marker radius scales with composite risk and layers carry a
subtle stroke so severity bands separate visually on the dark basemap.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import polars as pl
import pydeck as pdk

from schemas.scenario_schema import ScenarioConfig
from theme import RISK_RGB


def _esc(column: str) -> pl.Expr:
    """Vectorized HTML-escape for tooltip-safe strings (& first)."""
    return (
        pl.col(column)
        .str.replace_all("&", "&amp;")
        .str.replace_all("<", "&lt;")
        .str.replace_all(">", "&gt;")
        .str.replace_all('"', "&quot;")
        .str.replace_all("'", "&#39;")
    )


def _risk_rgb_columns(df: pl.DataFrame, risk_col: str) -> pl.DataFrame:
    crit = RISK_RGB["CRITICAL"]
    high = RISK_RGB["HIGH"]
    med = RISK_RGB["MEDIUM"]
    low = RISK_RGB["LOW"]

    def _ch(idx: int, vals: dict[str, int]) -> pl.Expr:
        return (
            pl.when(pl.col(risk_col) >= 0.85).then(pl.lit(vals["CRITICAL"]))
            .when(pl.col(risk_col) >= 0.70).then(pl.lit(vals["HIGH"]))
            .when(pl.col(risk_col) >= 0.40).then(pl.lit(vals["MEDIUM"]))
            .otherwise(pl.lit(vals["LOW"]))
            .alias(f"_c{idx}")
        )

    return df.with_columns(
        _ch(0, {"CRITICAL": crit[0], "HIGH": high[0], "MEDIUM": med[0], "LOW": low[0]}),
        _ch(1, {"CRITICAL": crit[1], "HIGH": high[1], "MEDIUM": med[1], "LOW": low[1]}),
        _ch(2, {"CRITICAL": crit[2], "HIGH": high[2], "MEDIUM": med[2], "LOW": low[2]}),
        pl.lit(210).alias("_c3"),
    ).with_columns(pl.concat_list("_c0", "_c1", "_c2", "_c3").alias("risk_rgb"))


def build_map(df: pl.DataFrame | pl.LazyFrame, config: ScenarioConfig) -> pdk.Deck:
    """Pure headless builder returning a pydeck Deck (CARTO dark basemap)."""
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    if config.max_map_points is not None and df.height > config.max_map_points:
        df = df.head(config.max_map_points)

    risk_col = "composite_risk" if "composite_risk" in df.columns else "risk_score"
    risk = pl.col(risk_col).cast(pl.Float64).fill_null(0.0).fill_nan(0.0)

    df = df.with_columns(
        risk.round(3).cast(pl.String).alias("risk_display"),
        (60_000.0 + risk * 240_000.0).alias("risk_radius"),
        pl.col("supplier_id").cast(pl.String).fill_null("ENTITY"),
        pl.col("supplier_name").cast(pl.String).fill_null("Unknown Entity")
        if "supplier_name" in df.columns
        else pl.lit("Unknown Entity").alias("supplier_name"),
        pl.col("region").cast(pl.String).fill_null("-")
        if "region" in df.columns
        else pl.lit("-").alias("region"),
    )
    df = _risk_rgb_columns(df, risk_col)
    df = df.with_columns(
        _esc("supplier_id").alias("supplier_id"),
        _esc("supplier_name").alias("supplier_name"),
        _esc("region").alias("region"),
    )

    data = df.select(
        ["supplier_id", "supplier_name", "region", "latitude", "longitude",
         "risk_display", "risk_rgb", "risk_radius"]
    ).to_dicts()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        id="supplier-risk-layer",
        get_position=["longitude", "latitude"],
        get_fill_color="risk_rgb",
        get_radius="risk_radius",
        radius_min_pixels=5,
        radius_max_pixels=22,
        stroked=True,
        get_line_color=[230, 237, 246, 70],
        get_line_width=1,
        line_width_min_pixels=1,
        pickable=True,
        opacity=0.95,
        auto_highlight=True,
    )

    center = df.select(
        pl.col("latitude").mean().fill_null(0.0),
        pl.col("longitude").mean().fill_null(0.0),
    ).row(0)

    view_state = pdk.ViewState(
        latitude=float(center[0]),
        longitude=float(center[1]),
        zoom=1.6,
        pitch=0,
    )

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="dark",
        tooltip={
            "html": (
                "<b>{supplier_name}</b><br/>"
                "ID: {supplier_id} · {region}<br/>"
                "Composite Risk: {risk_display}"
            ),
            "style": {
                "backgroundColor": "#111C30",
                "color": "#E6EDF6",
                "border": "1px solid #1E2A44",
                "borderRadius": "8px",
                "padding": "10px 12px",
                "fontSize": "12px",
                "fontFamily": "'JetBrains Mono', monospace",
            },
        },
    )


def deck_to_html(map_obj: pdk.Deck) -> str:
    """Materialize the standalone deck.gl HTML document via temp file."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tmp:
        path = tmp.name

    map_obj.to_html(filename=path, open_browser=False, notebook_display=False)
    html = Path(path).read_text(encoding="utf-8")
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass
    return html


def render_in_streamlit(map_obj: pdk.Deck, height: int = 680):
    """Embed the self-contained deck.gl document in a Streamlit iframe / html."""
    import streamlit as st

    try:
        html = deck_to_html(map_obj)
    except Exception:
        html = ""

    if html:
        st.markdown('<div class="map-frame">', unsafe_allow_html=True)
        if hasattr(st, "html"):
            st.html(html, height=height, scrolling=False)
        elif hasattr(st, "iframe"):
            st.iframe(html, height=height, scrolling=False)
        else:
            import streamlit.components.v1 as components
            components.html(html, height=height, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.pydeck_chart(map_obj, width="stretch")
