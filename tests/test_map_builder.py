"""Phase 3 tests: pydeck geospatial builder (headless, offline)."""
from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import pydeck as pdk

from geo.map_builder import build_map, deck_to_html
from schemas.scenario_schema import ScenarioConfig

MAP_TEST_POINTS = 50_000


def _small_df() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {"supplier_id": "SUP-001", "supplier_name": "Alpha", "region": "EMEA",
             "tier": 1, "composite_risk": 0.92, "latitude": 51.5072, "longitude": -0.1276},
            {"supplier_id": "SUP-002", "supplier_name": "Beta", "region": "APAC",
             "tier": 3, "composite_risk": 0.34, "latitude": 35.6762, "longitude": 139.6503},
        ]
    )


def _large_df(n: int = MAP_TEST_POINTS) -> pl.DataFrame:
    return (
        pl.DataFrame({"i": pl.Series(range(1, n + 1))})
        .with_columns(
            pl.concat_str(pl.lit("SUP-"), pl.col("i").cast(pl.String).str.zfill(6)).alias("supplier_id"),
            pl.concat_str(pl.lit("Entity "), pl.col("i").cast(pl.String)).alias("supplier_name"),
            pl.when(pl.col("i") % 2 == 0).then(pl.lit("EMEA")).otherwise(pl.lit("APAC")).alias("region"),
            ((pl.col("i") % 18_000) / 100 - 90).cast(pl.Float64).alias("latitude"),
            ((pl.col("i") % 36_000) / 100 - 180).cast(pl.Float64).alias("longitude"),
            ((pl.col("i") % 100) / 100).cast(pl.Float64).alias("composite_risk"),
        )
    )


def test_build_map_returns_pydeck_deck() -> None:
    deck = build_map(_small_df(), ScenarioConfig(scenario_name="small"))
    assert isinstance(deck, pdk.Deck)
    assert len(deck.layers) == 1
    assert deck.layers[0].type == "ScatterplotLayer"


def test_deck_carries_50k_points_without_python_markers() -> None:
    deck = build_map(_large_df(), ScenarioConfig(scenario_name="large"))
    assert len(deck.layers[0].data) == MAP_TEST_POINTS


def test_max_map_points_cap() -> None:
    deck = build_map(_large_df(), ScenarioConfig(scenario_name="cap", max_map_points=1_000))
    assert len(deck.layers[0].data) == 1_000


def test_deck_serializes_with_tooltip_and_colors() -> None:
    deck = build_map(_small_df(), ScenarioConfig(scenario_name="json"))
    payload = json.loads(deck.to_json())

    blob = json.dumps(payload)
    assert "ScatterplotLayer" in blob
    assert "supplier_name" in blob
    assert "risk_rgb" in blob
    assert payload.get("mapStyle") is not None or "dark" in blob


def test_headless_render_smoke() -> None:
    """Standalone deck.gl HTML must be returned as a non-empty string."""
    deck = build_map(_small_df(), ScenarioConfig(scenario_name="smoke"))
    html = deck_to_html(deck)

    assert isinstance(html, str)
    assert len(html) > 1_000
    assert "ScatterplotLayer" in html


def test_no_folium_dependency_in_map_builder() -> None:
    source = Path("geo/map_builder.py").read_text().lower()
    assert "folium" not in source
    assert "streamlit_folium" not in source
