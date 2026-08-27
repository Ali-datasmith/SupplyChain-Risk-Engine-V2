"""
Lazy CSV ingestion edge with a vectorized sanitization stage.

Pipeline: scan (all-String) -> trim/de-space/repair -> typed casts -> LazyFrame.
Real-world dirty payloads (padded enums, spaced numerics, broken dates) are
repaired; genuinely invalid values become null via strict=False casts and are
then surfaced by the Pandera gate as structured failure cases.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Iterable, Mapping

import polars as pl

STRING_COLUMNS = ("supplier_id", "supplier_name", "region", "last_audit_date")
NUMERIC_COLUMNS = {
    "risk_score": pl.Float64,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "annual_spend_usd": pl.Float64,
}
INT_COLUMNS = {"tier": pl.Int64}

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

_NULL_LITERALS = ["NULL", "null", "N/A", " ", ""]


def _sanitized(lf: pl.LazyFrame, final_dtypes: Mapping[str, object]) -> pl.LazyFrame:
    present = lf.collect_schema().names()

    trim_exprs = [
        pl.col(c).str.strip_chars()
        for c in STRING_COLUMNS
        if c in present
    ]
    null_exprs = [
        pl.when(pl.col(c).is_in(_NULL_LITERALS))
        .then(None)
        .otherwise(pl.col(c))
        .alias(c)
        for c in STRING_COLUMNS
        if c in present
    ]
    despace_exprs = [
        pl.col(c).str.replace_all(r"\s+", "").alias(c)
        for c in ("supplier_id", "region", "last_audit_date")
        if c in present
    ]
    cast_exprs = []
    for c, dtype in {**NUMERIC_COLUMNS, **INT_COLUMNS}.items():
        if c in present:
            cast_exprs.append(
                pl.col(c)
                .str.replace_all(r"\s+", "")
                .cast(dtype, strict=False)
                .alias(c)
            )
    for c, dtype in final_dtypes.items():
        if c in present and c in STRING_COLUMNS:
            cast_exprs.append(pl.col(c).cast(dtype, strict=False).alias(c))

    if trim_exprs:
        lf = lf.with_columns(trim_exprs)
    if null_exprs:
        lf = lf.with_columns(null_exprs)
    if despace_exprs:
        lf = lf.with_columns(despace_exprs)
    if cast_exprs:
        lf = lf.with_columns(cast_exprs)
    return lf


def load_supplier_csv(
    source: bytes | bytearray | io.BytesIO | str | Path,
    *,
    schema_overrides: Mapping[str, object] | None = None,
    infer_schema_length: int = 10_000,
    null_values: Iterable[str] = (" ", "NULL", "null", "N/A"),
) -> pl.LazyFrame:
    """Scan an uploaded buffer/path lazily and return a sanitized, typed LazyFrame."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(bytes(source))

    if hasattr(source, "seek"):
        try:
            source.seek(0)
        except Exception:
            pass

    final_dtypes = {
        **DEFAULT_SUPPLIER_SCHEMA_OVERRIDES,
        **(schema_overrides or {}),
    }

    lf = pl.scan_csv(
        source,
        schema_overrides={c: pl.String for c in final_dtypes},
        infer_schema_length=infer_schema_length,
        null_values="",
    )
    return _sanitized(lf, final_dtypes)
