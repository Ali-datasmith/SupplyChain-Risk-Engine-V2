"""Phase 3 tests: headless Folium map builder and DOM-safe rendering."""
from __future__ import annotations

import folium
import polars as pl
import pytest
from folium.plugins import FastMarkerCluster

from geo.map_builder import build_map
from schemas.scenario_schema import ScenarioConfig

MAP_TEST_POINTS = 50_000


def _small_df() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "supplier_id": "SUP-001",
                "supplier_name": "Alpha",
                "region": "EMEA",
                "tier": 1,
                "composite_risk": 0.82,
                "latitude": 51.5072,
                "longitude": -0.1276,
            },
            {
                "supplier_id": "SUP-002",
                "supplier_name": "Beta",
                "region": "APAC",
                "tier": 3,
                "composite_risk": 0.34,
                "latitude": 35.6762,
                "longitude": 139.6503,
            },
        ]
    )


@pytest.fixture(scope="module")
def large_map_df() -> pl.DataFrame:
    n = MAP_TEST_POINTS

    return (
        pl.DataFrame({"i": pl.Series(range(1, n + 1))})
        .with_columns(
            ((pl.col("i") % 18_000) / 100 - 90).cast(pl.Float64).alias("latitude"),
            ((pl.col("i") % 36_000) / 100 - 180).cast(pl.Float64).alias("longitude"),
            pl.concat_str(pl.lit("Point "), pl.col("i").cast(pl.String)).alias("popup_text"),
        )
        .select(["latitude", "longitude", "popup_text"])
    )


def _iter_elements(element):
    yield element
    for child in getattr(element, "_children", {}).values():
        yield from _iter_elements(child)


def test_build_map_returns_folium_map_with_fast_marker_cluster() -> None:
    m = build_map(_small_df(), ScenarioConfig(scenario_name="small"))

    assert isinstance(m, folium.Map)

    children = list(getattr(m, "_children", {}).values())
    assert any(isinstance(child, FastMarkerCluster) for child in children)


def test_map_options_prefer_canvas() -> None:
    m = build_map(_small_df(), ScenarioConfig(scenario_name="canvas"))

    options = getattr(m, "options", {}) or {}
    html = m.get_root().render().lower()

    assert (
        options.get("preferCanvas") is True
        or options.get("prefer_canvas") is True
        or ("prefercanvas" in html and "true" in html)
    )


def test_js_callback_present_in_rendered_html() -> None:
    m = build_map(_small_df(), ScenarioConfig(scenario_name="callback"))
    html = m.get_root().render()

    assert "L.circleMarker" in html
    assert "bindPopup" in html
    assert "row[2]" in html


def test_headless_render_smoke() -> None:
    m = build_map(_small_df(), ScenarioConfig(scenario_name="smoke"))
    html = m.get_root().render()

    assert isinstance(html, str)
    assert len(html) > 1_000


def test_zero_python_marker_objects_at_50k_points(large_map_df: pl.DataFrame) -> None:
    m = build_map(large_map_df, ScenarioConfig(scenario_name="large"))

    elements = list(_iter_elements(m))

    marker_count = sum(isinstance(el, folium.Marker) for el in elements)
    fast_cluster_count = sum(isinstance(el, FastMarkerCluster) for el in elements)

    assert marker_count == 0
    assert fast_cluster_count >= 1
