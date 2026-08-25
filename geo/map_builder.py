"""
DOM-safe Folium map construction.

- build_map() is headless and unit-testable.
- render_in_streamlit() lazily imports streamlit-folium.
- FastMarkerCluster performs one JS-side injection.
- CartoDB dark_matter tiles; cyan/indigo cluster styling.
"""
from __future__ import annotations

import folium
import polars as pl
from folium.plugins import FastMarkerCluster

from geo.cluster_payload import build_cluster_payload
from schemas.scenario_schema import ScenarioConfig

JS_CALLBACK = """
function (row) {
    return L.circleMarker([row[0], row[1]], {
        radius: 4,
        weight: 0.6,
        color: '#22D3EE',
        opacity: 0.95,
        fillColor: '#818CF8',
        fillOpacity: 0.75
    }).bindPopup(row[2], {className: 'obsidian-popup'});
}
""".strip()

CARTO_DARK_TILES = (
    "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
)
CARTO_ATTRIBUTION = (
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    '&copy; <a href="https://carto.com/attributions">CARTO</a>'
)


def _popup_expression(df: pl.DataFrame) -> pl.Expr:
    parts: list[pl.Expr] = []

    for column in ("supplier_id", "supplier_name", "region"):
        if column in df.columns:
            if parts:
                parts.append(pl.lit(" | "))
            parts.append(pl.col(column).cast(pl.String))

    if "tier" in df.columns:
        if parts:
            parts.append(pl.lit(" | tier="))
        parts.append(pl.col("tier").cast(pl.String))

    risk_column = None
    if "composite_risk" in df.columns:
        risk_column = "composite_risk"
    elif "risk_score" in df.columns:
        risk_column = "risk_score"

    if risk_column is not None:
        if parts:
            parts.append(pl.lit(" | risk="))
        parts.append(pl.col(risk_column).cast(pl.String))

    if not parts:
        parts = [
            pl.lit("lat="),
            pl.col("latitude").cast(pl.String),
            pl.lit(" lon="),
            pl.col("longitude").cast(pl.String),
        ]

    return pl.concat_str(parts).alias("popup_text")


def _ensure_popup_text(df: pl.DataFrame) -> pl.DataFrame:
    if "popup_text" in df.columns:
        return df.with_columns(
            pl.col("popup_text").fill_null("").cast(pl.String)
        )
    return df.with_columns(_popup_expression(df))


def _map_center(df: pl.DataFrame) -> list[float]:
    if df.height == 0:
        return [0.0, 0.0]
    center = df.select(
        pl.col("latitude").mean().fill_null(0.0),
        pl.col("longitude").mean().fill_null(0.0),
    ).row(0)
    return [float(center[0]), float(center[1])]


def build_map(df: pl.DataFrame | pl.LazyFrame, config: ScenarioConfig) -> folium.Map:
    """Pure headless builder. CartoDB dark_matter + FastMarkerCluster."""
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    if config.max_map_points is not None and df.height > config.max_map_points:
        df = df.head(config.max_map_points)

    df = _ensure_popup_text(df)
    center = _map_center(df)
    payload = build_cluster_payload(df)

    m = folium.Map(
        location=center,
        prefer_canvas=True,
        tiles=CARTO_DARK_TILES,
        attr=CARTO_ATTRIBUTION,
        zoom_start=2,
    )

    FastMarkerCluster(
        data=payload,
        callback=JS_CALLBACK,
        options={
            "showCoverageOnHover": False,
            "spiderfyOnMaxZoom": True,
        },
    ).add_to(m)

    return m


def render_in_streamlit(map_obj: folium.Map):
    """Lazy streamlit-folium import; headless-safe."""
    from streamlit_folium import st_folium

    return st_folium(map_obj, returned_objects=[], height=560)
