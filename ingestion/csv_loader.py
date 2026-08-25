"""
Lazy CSV ingestion edge.

2026 Polars rules enforced:
- pl.scan_csv() only.
- Never pass rechunk=, cache=, or retries=.
- Use schema_overrides for deterministic dtypes.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Iterable, Mapping

import polars as pl

DEFAULT_SUPPLIER_SCHEMA_OVERRIDES: dict[str, object] = {
    "supplier_id": pl.String,
    "supplier_name": pl.String,
    "risk_score": pl.Float64,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "region": pl.String,
    "tier": pl.Int64,
    "annual_spend_usd": pl.Float64,
    "last_audit_date": pl.String,
}


def load_supplier_csv(
    source: bytes | bytearray | io.BytesIO | str | Path,
    *,
    schema_overrides: Mapping[str, object] | None = None,
    infer_schema_length: int = 10_000,
    null_values: Iterable[str] = ("", "NULL", "null", "N/A"),
) -> pl.LazyFrame:
    """
    Convert an uploaded buffer/path into a Polars LazyFrame without materializing
    the full dataset into Python memory.

    Note: "NA" is intentionally excluded from default null_values because it is a
    valid region enum (North America) in the SupplierRecord schema.
    """
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(bytes(source))

    if hasattr(source, "seek"):
        try:
            source.seek(0)
        except Exception:
            pass

    overrides = {
        **DEFAULT_SUPPLIER_SCHEMA_OVERRIDES,
        **(schema_overrides or {}),
    }

    scan_kwargs: dict[str, Any] = {
        "schema_overrides": overrides,
        "infer_schema_length": infer_schema_length,
        "null_values": list(null_values),
    }

    return pl.scan_csv(source, **scan_kwargs)
