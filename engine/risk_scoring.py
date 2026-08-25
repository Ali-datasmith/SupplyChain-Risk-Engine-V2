"""
Vectorized risk engine.

Forbidden patterns intentionally absent:
- no .apply()
- no .map_elements()
- no iter_rows()
- no Python row loops
"""
from __future__ import annotations

from datetime import date

import polars as pl

from schemas.scenario_schema import RiskWeighting, ScenarioConfig

REFERENCE_DATE = date(2026, 1, 1)
STALENESS_HALF_LIFE_DAYS = 730.0

_COMPONENT_NAMES = (
    "component_base",
    "component_financial",
    "component_operational",
    "component_geopolitical",
    "component_audit_staleness",
)

_WEIGHT_VECTORS: dict[RiskWeighting, tuple[float, float, float, float, float]] = {
    RiskWeighting.BALANCED: (0.25, 0.25, 0.25, 0.15, 0.10),
    RiskWeighting.FINANCIAL_HEAVY: (0.15, 0.45, 0.15, 0.15, 0.10),
    RiskWeighting.OPERATIONAL_HEAVY: (0.15, 0.15, 0.45, 0.15, 0.10),
    RiskWeighting.GEOPOLITICAL_HEAVY: (0.15, 0.15, 0.15, 0.45, 0.10),
}


def _base_expression() -> pl.Expr:
    return (
        pl.col("risk_score")
        .cast(pl.Float64)
        .fill_null(0.0)
        .fill_nan(0.0)
        .alias(_COMPONENT_NAMES[0])
    )


def _financial_expression() -> pl.Expr:
    raw = (
        pl.col("annual_spend_usd")
        .cast(pl.Float64)
        .fill_null(0.0)
        .fill_nan(0.0)
        .log1p()
    )
    normalized = raw / raw.max()
    return (
        normalized
        .fill_nan(0.0)
        .fill_null(0.0)
        .alias(_COMPONENT_NAMES[1])
    )


def _operational_expression() -> pl.Expr:
    return (
        1.0
        - ((pl.col("tier").cast(pl.Float64).fill_null(4.0) - 1.0) / 3.0)
    ).alias(_COMPONENT_NAMES[2])


def _geopolitical_expression() -> pl.Expr:
    return (
        pl.when(pl.col("region") == "EMEA")
        .then(0.8)
        .when(pl.col("region") == "APAC")
        .then(0.7)
        .when(pl.col("region") == "LATAM")
        .then(0.6)
        .otherwise(0.3)
        .cast(pl.Float64)
        .alias(_COMPONENT_NAMES[3])
    )


def _audit_staleness_expression() -> pl.Expr:
    audit_date = pl.col("last_audit_date").str.to_date(format="%Y-%m-%d", strict=False)
    age_days = (
        pl.lit(REFERENCE_DATE).cast(pl.Date) - audit_date
    ).dt.total_days()

    return (
        (age_days / STALENESS_HALF_LIFE_DAYS)
        .clip(0.0, 1.0)
        .fill_nan(1.0)
        .fill_null(1.0)
        .alias(_COMPONENT_NAMES[4])
    )


def _component_expressions() -> list[pl.Expr]:
    return [
        _base_expression(),
        _financial_expression(),
        _operational_expression(),
        _geopolitical_expression(),
        _audit_staleness_expression(),
    ]


def score_suppliers(
    df: pl.DataFrame | pl.LazyFrame,
    config: ScenarioConfig,
    *,
    apply_filters: bool = True,
) -> pl.DataFrame:
    """
    Score suppliers vectorized and return a collected DataFrame with:
    - component_* columns
    - composite_risk clamped to [0, 1]

    If apply_filters=True, applies ScenarioConfig threshold and region filters.
    """
    if isinstance(df, pl.LazyFrame):
        lf = df
    elif isinstance(df, pl.DataFrame):
        lf = df.lazy()
    else:
        lf = pl.DataFrame(df).lazy()

    lf = lf.with_columns(_component_expressions())

    weights = _WEIGHT_VECTORS[config.weighting]
    composite = pl.lit(0.0)
    for weight, column in zip(weights, _COMPONENT_NAMES):
        composite = composite + (pl.lit(weight) * pl.col(column))

    lf = lf.with_columns(composite.clip(0.0, 1.0).alias("composite_risk"))

    if apply_filters:
        lf = lf.filter(pl.col("composite_risk") >= config.min_risk_threshold)
        lf = lf.filter(pl.col("composite_risk") <= config.max_risk_threshold)

        if config.regions:
            lf = lf.filter(pl.col("region").is_in(config.regions))

    return lf.collect()
