"""Phase 2 tests: lazy CSV loader + 50k-row performance gate."""
from __future__ import annotations

import io
import time

import polars as pl
import pytest

from ingestion.csv_loader import load_supplier_csv
from ingestion.validation_gate import validate_supplier_lazyframe

SYNTHETIC_ROW_COUNT = 50_000
PERFORMANCE_BUDGET_SECONDS = 3.0


def _synthetic_supplier_df(n: int) -> pl.DataFrame:
    regions = ["EMEA", "APAC", "NA", "LATAM"]
    idx = range(1, n + 1)

    supplier_id = [f"SUP-{i:06d}" for i in idx]
    supplier_name = [f"Supplier {i}" for i in idx]
    risk_score = [(i % 100) / 100.0 for i in idx]
    latitude = [(i % 18_000) / 100.0 - 90.0 for i in idx]
    longitude = [(i % 36_000) / 100.0 - 180.0 for i in idx]
    region = [regions[i % 4] for i in idx]
    tier = [(i % 4) + 1 for i in idx]
    annual_spend_usd = [
        10_000.0 + float(i) if ((i % 4) + 1) == 1 else float(i) for i in idx
    ]
    last_audit_date = [None if i % 10 == 0 else "2025-01-01" for i in idx]

    return pl.DataFrame(
        {
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "risk_score": risk_score,
            "latitude": latitude,
            "longitude": longitude,
            "region": region,
            "tier": tier,
            "annual_spend_usd": annual_spend_usd,
            "last_audit_date": last_audit_date,
        }
    )


@pytest.fixture(scope="module")
def synthetic_supplier_csv_bytes() -> bytes:
    buf = io.BytesIO()
    _synthetic_supplier_df(SYNTHETIC_ROW_COUNT).write_csv(buf)
    return buf.getvalue()


def _run_pipeline(payload: bytes) -> pl.DataFrame:
    lf = load_supplier_csv(payload)
    assert isinstance(lf, pl.LazyFrame)
    return validate_supplier_lazyframe(lf)


def test_load_supplier_csv_returns_lazyframe(synthetic_supplier_csv_bytes: bytes) -> None:
    lf = load_supplier_csv(synthetic_supplier_csv_bytes)
    assert isinstance(lf, pl.LazyFrame)


def test_schema_overrides_are_applied(synthetic_supplier_csv_bytes: bytes) -> None:
    df = load_supplier_csv(synthetic_supplier_csv_bytes).head(5).collect()

    assert df.schema["supplier_id"] == pl.String
    assert df.schema["risk_score"] == pl.Float64
    assert df.schema["latitude"] == pl.Float64
    assert df.schema["longitude"] == pl.Float64
    assert df.schema["region"] == pl.String
    assert df.schema["tier"] == pl.Int64
    assert df.schema["annual_spend_usd"] == pl.Float64
    assert df.schema["last_audit_date"] == pl.String


def test_scan_validate_collect_50k_under_3_seconds(synthetic_supplier_csv_bytes: bytes) -> None:
    start = time.perf_counter()
    df = _run_pipeline(synthetic_supplier_csv_bytes)
    elapsed = time.perf_counter() - start

    # One bounded retry absorbs Colab cold-start jitter while preserving the hard budget.
    if elapsed >= PERFORMANCE_BUDGET_SECONDS:
        start = time.perf_counter()
        df = _run_pipeline(synthetic_supplier_csv_bytes)
        elapsed = time.perf_counter() - start

    assert df.height == SYNTHETIC_ROW_COUNT
    assert elapsed < PERFORMANCE_BUDGET_SECONDS
