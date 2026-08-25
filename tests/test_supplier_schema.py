"""
Phase 1 rigorous schema-gate tests.

Every invalid scenario must raise pandera.errors.SchemaErrors and expose
row/column-addressable failure_cases.
"""
from __future__ import annotations

import pandera.errors
import polars as pl
import pytest

from schemas.supplier_schema import SupplierRecord


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


def _valid_df() -> pl.DataFrame:
    return pl.DataFrame(_valid_rows())


def _validate(df: pl.DataFrame) -> pl.DataFrame:
    """
    Validation invocation contract from spec.md:
    SupplierRecord.validate(lf.collect(), lazy=True)
    """
    validated = SupplierRecord.validate(df, lazy=True)
    if isinstance(validated, pl.LazyFrame):
        return validated.collect()
    return validated


def _failure_case_count(failure_cases) -> int:
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


def _to_list(values):
    if values is None:
        return []
    if hasattr(values, "to_list"):
        return values.to_list()
    if hasattr(values, "tolist"):
        return values.tolist()
    return list(values)


def _failure_values(excinfo, field: str) -> list[str]:
    """
    Extract a failure_cases column as strings, robust to both Pandas and Polars
    failure_cases representations.
    """
    failure_cases = excinfo.value.failure_cases
    if failure_cases is None:
        return []

    if hasattr(failure_cases, "columns") and field in failure_cases.columns:
        return [str(value) for value in _to_list(failure_cases[field])]

    return []


def test_valid_supplier_payload_passes() -> None:
    validated = _validate(_valid_df())

    assert isinstance(validated, pl.DataFrame)
    assert validated.height == 2
    assert "supplier_id" in validated.columns
    assert "annual_spend_usd" in validated.columns


def test_missing_required_column_is_rejected() -> None:
    df = _valid_df().drop("region")

    with pytest.raises(pandera.errors.SchemaErrors) as excinfo:
        _validate(df)

    failure_cases = excinfo.value.failure_cases
    assert failure_cases is not None
    assert _failure_case_count(failure_cases) > 0

    observed = " ".join(
        _failure_values(excinfo, "column")
        + _failure_values(excinfo, "check")
        + _failure_values(excinfo, "failure_case")
        + [str(failure_cases)]
    )
    assert "region" in observed


def test_bad_region_enum_is_rejected() -> None:
    rows = _valid_rows()
    rows[0]["region"] = "MARS"
    df = pl.DataFrame(rows)

    with pytest.raises(pandera.errors.SchemaErrors) as excinfo:
        _validate(df)

    failure_cases = excinfo.value.failure_cases
    assert failure_cases is not None
    assert _failure_case_count(failure_cases) > 0

    columns = _failure_values(excinfo, "column")
    checks = _failure_values(excinfo, "check")
    failure_values = _failure_values(excinfo, "failure_case")
    observed = " ".join(columns + checks + failure_values + [str(failure_cases)])

    assert any("region" in value for value in columns + checks + failure_values + [observed])
    assert any("MARS" in value for value in failure_values + [observed])


def test_out_of_range_risk_score_is_rejected() -> None:
    rows = _valid_rows()
    rows[0]["risk_score"] = 1.2
    df = pl.DataFrame(rows)

    with pytest.raises(pandera.errors.SchemaErrors) as excinfo:
        _validate(df)

    failure_cases = excinfo.value.failure_cases
    assert failure_cases is not None
    assert _failure_case_count(failure_cases) > 0

    columns = _failure_values(excinfo, "column")
    checks = _failure_values(excinfo, "check")
    failure_values = _failure_values(excinfo, "failure_case")
    observed = " ".join(columns + checks + failure_values + [str(failure_cases)])

    assert any("risk_score" in value for value in columns + checks + failure_values + [observed])
    assert any(token in observed for token in ("1.2", "1.200000"))


def test_tier_1_spend_floor_violation_is_rejected() -> None:
    rows = _valid_rows()
    rows[1]["tier"] = 1
    rows[1]["annual_spend_usd"] = 9_999.99
    df = pl.DataFrame(rows)

    with pytest.raises(pandera.errors.SchemaErrors) as excinfo:
        _validate(df)

    failure_cases = excinfo.value.failure_cases
    assert failure_cases is not None
    assert _failure_case_count(failure_cases) > 0

    columns = _failure_values(excinfo, "column")
    checks = _failure_values(excinfo, "check")
    failure_values = _failure_values(excinfo, "failure_case")
    observed = " ".join(columns + checks + failure_values + [str(failure_cases)])

    assert (
        "spend_matches_tier_floor" in observed
        or ("tier" in observed and "annual_spend_usd" in observed)
        or ("tier" in observed and "9999.99" in observed)
    )
