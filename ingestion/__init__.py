"""Phase 2 ingestion package."""

from ingestion.csv_loader import load_supplier_csv
from ingestion.validation_gate import (
    IngestionError,
    ingest_supplier_csv,
    validate_supplier_lazyframe,
)

__all__ = [
    "load_supplier_csv",
    "IngestionError",
    "ingest_supplier_csv",
    "validate_supplier_lazyframe",
]
