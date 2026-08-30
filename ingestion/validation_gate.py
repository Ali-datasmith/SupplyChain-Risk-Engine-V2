"""
Validation gate.

- Collects only when schema-level pushdown has already been applied to the LazyFrame.
- Runs SupplierRecord.validate(..., lazy=True).
- Raises IngestionError carrying pandera failure_cases for UI rendering.
"""
from __future__ import annotations

import io
from typing import Any

import pandera.errors
import polars as pl

from schemas.supplier_schema import SupplierRecord


class IngestionError(Exception):
    """Structured ingestion failure carrying row-addressable Pandera failure cases."""

    def __init__(
        self,
        message: str,
        *,
        failure_cases: Any | None = None,
        schema_errors: list[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.failure_cases = failure_cases
        self.schema_errors = schema_errors or []


def _collect_validated_frame(validated: pl.DataFrame | pl.LazyFrame) -> pl.DataFrame:
    if isinstance(validated, pl.LazyFrame):
        return validated.collect()
    return validated


def validate_supplier_lazyframe(lf: pl.LazyFrame | pl.DataFrame) -> pl.DataFrame:
    """
    Validate supplier data against SupplierRecord.

    Returns a collected, validated pl.DataFrame.
    Raises IngestionError on schema failure.
    """
    if isinstance(lf, pl.DataFrame):
        lf = lf.lazy()

    try:
        df = lf.collect()
    except pl.exceptions.PolarsError as exc:
        raise IngestionError(
            "Polars failed to materialize supplier CSV for validation.",
            failure_cases=None,
            schema_errors=[],
        ) from exc

    try:
        validated = SupplierRecord.validate(df, lazy=True)
        return _collect_validated_frame(validated)
    except pandera.errors.SchemaErrors as exc:
        raise IngestionError(
            f"Supplier data failed schema validation: {len(exc.schema_errors)} error(s).",
            failure_cases=exc.failure_cases,
            schema_errors=exc.schema_errors,
        ) from exc
    except pandera.errors.SchemaError as exc:
        raise IngestionError(
            "Supplier data failed schema validation.",
            failure_cases=getattr(exc, "failure_cases", None),
            schema_errors=[exc],
        ) from exc


def ingest_supplier_csv(source: bytes | bytearray | io.BytesIO | str | Any) -> pl.DataFrame:
    """End-to-end Phase 2 ingestion: scan -> validate -> collect."""
    from ingestion.csv_loader import load_supplier_csv

    return validate_supplier_lazyframe(load_supplier_csv(source))
