"""
Ingestion-edge schema. Uses pandera.polars (NOT top-level pandera — deprecated
since 0.29.0 for Polars backends per 2026 audit). This is the single gate every
uploaded CSV must pass before any row reaches engine/.

2026 runtime corrections:
- pandera[polars] 0.32.x passes an internal PolarsData object into dataframe checks.
- DataFrame-level checks must return a Polars LazyFrame, not a bare Expr.
- Coercion is disabled at the schema boundary so missing columns surface as
  structured pandera.errors.SchemaErrors. Dtype coercion belongs in Phase 2
  via pl.scan_csv(..., schema_overrides=...).
"""
from __future__ import annotations

import pandera.polars as pa
import polars as pl
from pandera.typing.polars import Series


def _get_check_lazyframe(check_object: object) -> pl.LazyFrame:
    """
    Resolve the underlying Polars LazyFrame from the object supplied to a
    pandera.polars dataframe check.

    Pandera 0.32.x may pass:
    - a raw LazyFrame,
    - a raw DataFrame,
    - or an internal PolarsData wrapper.
    """
    if isinstance(check_object, pl.LazyFrame):
        return check_object

    if isinstance(check_object, pl.DataFrame):
        return check_object.lazy()

    candidates: list[object] = []

    for attr in (
        "lazyframe",
        "lazy_frame",
        "lf",
        "_lazyframe",
        "_lf",
        "dataframe",
        "df",
        "frame",
        "data",
    ):
        candidates.append(getattr(check_object, attr, None))

    try:
        candidates.extend(vars(check_object).values())
    except Exception:
        pass

    as_dict = getattr(check_object, "_asdict", None)
    if callable(as_dict):
        try:
            candidates.extend(as_dict().values())
        except Exception:
            pass

    for candidate in candidates:
        if candidate is None:
            continue

        if isinstance(candidate, pl.LazyFrame):
            return candidate

        if isinstance(candidate, pl.DataFrame):
            return candidate.lazy()

        lazy_method = getattr(candidate, "lazy", None)
        if callable(lazy_method):
            try:
                maybe_lf = lazy_method()
            except Exception:
                continue

            if isinstance(maybe_lf, pl.LazyFrame):
                return maybe_lf

            if isinstance(maybe_lf, pl.DataFrame):
                return maybe_lf.lazy()

    raise TypeError("Unable to resolve a Polars LazyFrame from pandera check object.")


class SupplierRecord(pa.DataFrameModel):
    supplier_id: Series[str] = pa.Field(str_length={"min_value": 3, "max_value": 20}, unique=True)
    supplier_name: Series[str] = pa.Field(str_length={"min_value": 1, "max_value": 200})
    risk_score: Series[float] = pa.Field(ge=0.0, le=1.0, nullable=False)
    latitude: Series[float] = pa.Field(ge=-90.0, le=90.0)
    longitude: Series[float] = pa.Field(ge=-180.0, le=180.0)
    region: Series[str] = pa.Field(isin=["EMEA", "APAC", "NA", "LATAM"])
    tier: Series[int] = pa.Field(ge=1, le=4)
    annual_spend_usd: Series[float] = pa.Field(ge=0.0)
    last_audit_date: Series[str] = pa.Field(str_matches=r"^\d{4}-\d{2}-\d{2}$", nullable=True)

    class Config:
        strict = True
        coerce = False

    @pa.dataframe_check
    @classmethod
    def spend_matches_tier_floor(cls, data: object) -> pl.LazyFrame:
        """Tier-1 (critical) suppliers must carry non-trivial annual spend."""
        lf = _get_check_lazyframe(data)
        return lf.select(
            ((pl.col("tier") != 1) | (pl.col("annual_spend_usd") >= 10_000.0)).alias(
                "spend_matches_tier_floor"
            )
        )
