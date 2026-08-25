"""
JS-side cluster payload construction.

Contract:
- select exactly latitude, longitude, popup_text
- materialize via to_numpy().tolist()
- return plain Python list[list], no numpy scalar leakage
"""
from __future__ import annotations

import polars as pl


def build_cluster_payload(df: pl.DataFrame | pl.LazyFrame) -> list[list]:
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    return df.select(["latitude", "longitude", "popup_text"]).to_numpy().tolist()
