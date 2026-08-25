"""Phase 2 tests: DuckDB out-of-core CSV join."""
from __future__ import annotations

from pathlib import Path

import polars as pl

from engine.duckdb_joins import join_sanctions_screening


def test_duckdb_sanctions_join_flags_matched_suppliers(tmp_path: Path) -> None:
    supplier_csv = tmp_path / "suppliers.csv"
    sanctions_csv = tmp_path / "sanctions.csv"

    supplier_csv.write_text(
        """supplier_id,supplier_name,risk_score,latitude,longitude,region,tier,annual_spend_usd,last_audit_date
SUP-001,Alpha Ltd,0.21,10.0,10.0,EMEA,1,25000.0,2025-01-01
SUP-002,Beta GmbH,0.35,20.0,20.0,APAC,2,5000.0,2025-01-02
SUP-003,Gamma SA,0.77,30.0,30.0,LATAM,3,8000.0,2025-01-03
"""
    )

    sanctions_csv.write_text(
        """entity_id,entity_name,list_source
SUP-001,Alpha Holdings,OFAC
SUP-003,Gamma International,EU
"""
    )

    result = join_sanctions_screening(supplier_csv, sanctions_csv)

    assert isinstance(result, pl.DataFrame)
    assert result.height == 3
    assert "is_sanctioned" in result.columns
    assert "sanctions_list_source" in result.columns

    sanctioned_ids = (
        result.filter(pl.col("is_sanctioned"))
        .get_column("supplier_id")
        .to_list()
    )
    assert sanctioned_ids == ["SUP-001", "SUP-003"]

    clean_row = result.filter(pl.col("supplier_id") == "SUP-002")
    assert clean_row.get_column("is_sanctioned").to_list() == [False]
    assert clean_row.get_column("sanctions_list_source").to_list() == ["NONE"]
