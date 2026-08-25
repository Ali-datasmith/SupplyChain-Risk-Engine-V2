"""
Out-of-core cross-table joins via DuckDB's native CSV reader.

2026 rule: use DuckDB read_csv(), not read_csv_auto().
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl


def _to_polars(rel: object) -> pl.DataFrame:
    if hasattr(rel, "pl"):
        return rel.pl()
    return pl.from_arrow(rel.fetch_arrow_table())


def _sql_path(path: str | Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def join_sanctions_screening(
    supplier_csv_path: str | Path,
    sanctions_csv_path: str | Path,
) -> pl.DataFrame:
    """
    Left-join suppliers against a sanctions reference list without loading both
    CSVs into Python memory.

    Expected sanctions columns:
    - entity_id
    - entity_name
    - list_source
    """
    supplier_sql_path = _sql_path(supplier_csv_path)
    sanctions_sql_path = _sql_path(sanctions_csv_path)

    fallback_query = f"""
SELECT
    s.*,
    x.entity_id IS NOT NULL AS is_sanctioned,
    COALESCE(x.list_source, 'NONE') AS sanctions_list_source
FROM read_csv({supplier_sql_path}) AS s
LEFT JOIN read_csv({sanctions_sql_path}) AS x
    ON s.supplier_id = x.entity_id
ORDER BY s.supplier_id
"""

    try:
        suppliers = duckdb.read_csv(str(supplier_csv_path))
        sanctions = duckdb.read_csv(str(sanctions_csv_path))

        create_supplier_view = getattr(suppliers, "create_view", None)
        create_sanctions_view = getattr(sanctions, "create_view", None)

        if callable(create_supplier_view) and callable(create_sanctions_view):
            duckdb.sql("DROP VIEW IF EXISTS __scv2_suppliers")
            duckdb.sql("DROP VIEW IF EXISTS __scv2_sanctions")

            create_supplier_view("__scv2_suppliers")
            create_sanctions_view("__scv2_sanctions")

            try:
                rel = duckdb.sql(
                    """
SELECT
    s.*,
    x.entity_id IS NOT NULL AS is_sanctioned,
    COALESCE(x.list_source, 'NONE') AS sanctions_list_source
FROM __scv2_suppliers AS s
LEFT JOIN __scv2_sanctions AS x
    ON s.supplier_id = x.entity_id
ORDER BY s.supplier_id
"""
                )
                return _to_polars(rel)
            finally:
                duckdb.sql("DROP VIEW IF EXISTS __scv2_suppliers")
                duckdb.sql("DROP VIEW IF EXISTS __scv2_sanctions")
    except Exception:
        pass

    return _to_polars(duckdb.sql(fallback_query))
