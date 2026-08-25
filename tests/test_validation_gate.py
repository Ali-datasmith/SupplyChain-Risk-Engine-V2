"""Phase 2 tests: validation gate and IngestionError row-addressability."""
from __future__ import annotations

import polars as pl
import pytest

from ingestion.validation_gate import (
    IngestionError,
    ingest_supplier_csv,
    validate_supplier_lazyframe,
)


def _valid_rows() -> list[dict]:
    return [
        {
            "supplier_id": "SUP-001",
            "supplier_name": "Northwind Components",
            "risk_score": 0.12,
            "latitude": 51.5072,
            "longitude": -0.1276,
            "region": "EMEA",
            "tier": 2,
            "annual_spend_usd": 250_000.0,
            "last_audit_date": "2025-11-30",
        },
        {
            "supplier_id": "SUP-002",
            "supplier_name": "Pacific Precision",
            "risk_score": 0.88,
            "latitude": 35.6762,
            "longitude": 139.6503,
            "region": "APAC",
            "tier": 1,
            "annual_spend_usd": 1_250_000.0,
            "last_audit_date": None,
        },
    ]


def _validate_rows(rows: list[dict]) -> pl.DataFrame:
    return validate_supplier_lazyframe(pl.DataFrame(rows).lazy())


def _failure_case_count(failure_cases: object) -> int:
    if failure_cases is None:
        return 0
    if hasattr(failure_cases, "height"):
        return int(failure_cases.height)
    if hasattr(failure_cases, "shape"):
        return int(failure_cases.shape[0])
    try:
        return len(failure_cases)
    except TypeError:
        return 1 if failure_cases else 0


def _to_list(values: object) -> list:
    if values is None:
        return []
    if hasattr(values, "to_list"):
        return values.to_list()
    if hasattr(values, "tolist"):
        return values.tolist()
    return list(values)


def _failure_values(error: IngestionError, field: str) -> list[str]:
    failure_cases = error.failure_cases
    if failure_cases is None:
        return []

    if hasattr(failure_cases, "columns") and field in failure_cases.columns:
        return [str(value) for value in _to_list(failure_cases[field])]

    return []


def test_valid_rows_pass_validation_gate() -> None:
    validated = _validate_rows(_valid_rows())
    assert isinstance(validated, pl.DataFrame)
    assert validated.height == 2


def test_bad_region_raises_ingestion_error_with_failure_cases() -> None:
    rows = _valid_rows()
    rows[0]["region"] = "MARS"

    with pytest.raises(IngestionError) as excinfo:
        _validate_rows(rows)

    error = excinfo.value
    assert error.failure_cases is not None
    assert _failure_case_count(error.failure_cases) > 0

    observed = " ".join(
        _failure_values(error, "column")
        + _failure_values(error, "check")
        + _failure_values(error, "failure_case")
        + [str(error.failure_cases)]
    )

    assert "region" in observed
    assert "MARS" in observed


def test_out_of_range_risk_score_raises_ingestion_error() -> None:
    rows = _valid_rows()
    rows[0]["risk_score"] = 1.2

    with pytest.raises(IngestionError) as excinfo:
        _validate_rows(rows)

    error = excinfo.value
    assert error.failure_cases is not None
    assert _failure_case_count(error.failure_cases) > 0

    observed = " ".join(
        _failure_values(error, "column")
        + _failure_values(error, "check")
        + _failure_values(error, "failure_case")
        + [str(error.failure_cases)]
    )

    assert "risk_score" in observed
    assert any(token in observed for token in ("1.2", "1.200000"))


def test_tier_1_spend_floor_raises_ingestion_error() -> None:
    rows = _valid_rows()
    rows[1]["tier"] = 1
    rows[1]["annual_spend_usd"] = 9_999.99

    with pytest.raises(IngestionError) as excinfo:
        _validate_rows(rows)

    error = excinfo.value
    assert error.failure_cases is not None
    assert _failure_case_count(error.failure_cases) > 0

    observed = " ".join(
        _failure_values(error, "column")
        + _failure_values(error, "check")
        + _failure_values(error, "failure_case")
        + [str(error.failure_cases)]
    )

    assert (
        "spend_matches_tier_floor" in observed
        or ("tier" in observed and "annual_spend_usd" in observed)
        or ("tier" in observed and "9999.99" in observed)
    )


def test_missing_column_raises_ingestion_error() -> None:
    df = pl.DataFrame(_valid_rows()).drop("region")

    with pytest.raises(IngestionError) as excinfo:
        validate_supplier_lazyframe(df.lazy())

    error = excinfo.value
    assert error.failure_cases is not None
    assert _failure_case_count(error.failure_cases) > 0

    observed = " ".join(
        _failure_values(error, "column")
        + _failure_values(error, "check")
        + _failure_values(error, "failure_case")
        + [str(error.failure_cases)]
    )

    assert "region" in observed


def test_ingest_supplier_csv_end_to_end_bad_region() -> None:
    csv_bytes = (
        b"supplier_id,supplier_name,risk_score,latitude,longitude,region,tier,annual_spend_usd,last_audit_date\n"
        b"SUP-001,Acme,0.5,10.0,10.0,MARS,2,50000.0,2025-01-01\n"
    )

    with pytest.raises(IngestionError) as excinfo:
        ingest_supplier_csv(csv_bytes)

    error = excinfo.value
    assert error.failure_cases is not None

    observed = " ".join(
        _failure_values(error, "column")
        + _failure_values(error, "check")
        + _failure_values(error, "failure_case")
        + [str(error.failure_cases)]
    )

    assert "region" in observed
    assert "MARS" in observed
