"""Phase 3 tests: JSON-safe FastMarkerCluster payload."""
from __future__ import annotations

import time

import polars as pl
import pytest

from geo.cluster_payload import build_cluster_payload

PAYLOAD_ROW_COUNT = 50_000
PAYLOAD_BUDGET_SECONDS = 2.0


@pytest.fixture(scope="module")
def payload_df() -> pl.DataFrame:
    n = PAYLOAD_ROW_COUNT

    return (
        pl.DataFrame({"i": pl.Series(range(1, n + 1))})
        .with_columns(
            ((pl.col("i") % 18_000) / 100 - 90).cast(pl.Float64).alias("latitude"),
            ((pl.col("i") % 36_000) / 100 - 180).cast(pl.Float64).alias("longitude"),
            pl.concat_str(pl.lit("Point "), pl.col("i").cast(pl.String)).alias("popup_text"),
        )
        .select(["latitude", "longitude", "popup_text"])
    )


def test_payload_row_shape_and_plain_python_types(payload_df: pl.DataFrame) -> None:
    payload = build_cluster_payload(payload_df)

    assert len(payload) == PAYLOAD_ROW_COUNT

    row = payload[0]
    assert len(row) == 3

    assert type(row[0]) is float
    assert type(row[1]) is float
    assert type(row[2]) is str

    assert "numpy" not in type(row[0]).__module__
    assert "numpy" not in type(row[1]).__module__
    assert "numpy" not in type(row[2]).__module__


def test_payload_build_50k_under_2_seconds(payload_df: pl.DataFrame) -> None:
    start = time.perf_counter()
    payload = build_cluster_payload(payload_df)
    elapsed = time.perf_counter() - start

    # One bounded retry absorbs Colab cold-start jitter while preserving the hard budget.
    if elapsed >= PAYLOAD_BUDGET_SECONDS:
        start = time.perf_counter()
        payload = build_cluster_payload(payload_df)
        elapsed = time.perf_counter() - start

    assert len(payload) == PAYLOAD_ROW_COUNT
    assert elapsed < PAYLOAD_BUDGET_SECONDS
