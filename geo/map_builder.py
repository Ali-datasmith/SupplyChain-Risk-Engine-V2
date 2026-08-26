"""
GPU-accelerated geospatial rendering via pydeck / deck.gl.

Replaces the legacy Leaflet-based renderer (release-candidate instability on
Streamlit Cloud) with the native Streamlit + deck.gl stack: 50k+ points, dark
basemap, typed tooltips, zero per-point Python DOM objects.
"""
from __future__ import annotations

import polars as pl
import pydeck as pdk

from schemas.scenario_schema import ScenarioConfig
from theme import RISK_RGB


def _risk_rgb_columns(df: pl.DataFrame, risk_col: str) -> pl.DataFrame:
    """Vectorized severity -> RGBA list column for deck.gl fill colors."""
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
        pl.lit(200).alias("_c3"),
    ).with_columns(pl.concat_list("_c0", "_c1", "_c2", "_c3").alias("risk_rgb"))


def build_map(df: pl.DataFrame | pl.LazyFrame, config: ScenarioConfig) -> pdk.Deck:
    """Pure headless builder returning a pydeck Deck (dark basemap)."""
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    if config.max_map_points is not None and df.height > config.max_map_points:
        df = df.head(config.max_map_points)

    risk_col = "composite_risk" if "composite_risk" in df.columns else "risk_score"

    df = df.with_columns(
        pl.col(risk_col).cast(pl.Float64).fill_null(0.0).round(3).cast(pl.String).alias("risk_display"),
        pl.col("supplier_id").cast(pl.String).fill_null("ENTITY").alias("supplier_id"),
        pl.col("supplier_name").cast(pl.String).fill_null("Unknown Entity").alias("supplier_name")
        if "supplier_name" in df.columns
        else pl.lit("Unknown Entity").alias("supplier_name"),
        pl.col("region").cast(pl.String).fill_null("—").alias("region")
        if "region" in df.columns
        else pl.lit("—").alias("region"),
    )
    df = _risk_rgb_columns(df, risk_col)

    data = df.select(
        ["supplier_id", "supplier_name", "region", "latitude", "longitude", "risk_display", "risk_rgb"]
    ).to_dicts()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        id="supplier-risk-layer",
        get_position=["longitude", "latitude"],
        get_fill_color="risk_rgb",
        get_radius=30_000,
        radius_min_pixels=3,
        radius_max_pixels=14,
        pickable=True,
        opacity=0.88,
        auto_highlight=True,
    )

    center = df.select(
        pl.col("latitude").mean().fill_null(0.0),
        pl.col("longitude").mean().fill_null(0.0),
    ).row(0)

    view_state = pdk.ViewState(
        latitude=float(center[0]),
        longitude=float(center[1]),
        zoom=2.4,
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


def render_in_streamlit(map_obj: pdk.Deck):
    """Native Streamlit deck.gl render; headless-safe (lazy import)."""
    import streamlit as st

    return st.pydeck_chart(map_obj, use_container_width=True)
