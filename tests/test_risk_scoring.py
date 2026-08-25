"""Phase 3 tests: vectorized risk scoring."""
from __future__ import annotations

import time

import polars as pl
import pytest

from engine.risk_scoring import score_suppliers
from schemas.scenario_schema import RiskWeighting, ScenarioConfig

SYNTHETIC_ROW_COUNT = 50_000
SCORING_BUDGET_SECONDS = 2.0


def _scenario_df() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "supplier_id": "SUP-FIN",
                "supplier_name": "Financial Heavy Supplier",
                "risk_score": 0.10,
                "latitude": 10.0,
                "longitude": 10.0,
                "region": "NA",
                "tier": 4,
                "annual_spend_usd": 1_000_000.0,
                "last_audit_date": "2025-12-31",
            },
            {
                "supplier_id": "SUP-GEO",
                "supplier_name": "Geopolitical Heavy Supplier",
                "risk_score": 0.50,
                "latitude": 20.0,
                "longitude": 20.0,
                "region": "EMEA",
                "tier": 4,
                "annual_spend_usd": 1_000.0,
                "last_audit_date": "2025-12-31",
            },
            {
                "supplier_id": "SUP-OPS",
                "supplier_name": "Operational Heavy Supplier",
                "risk_score": 0.50,
                "latitude": 30.0,
                "longitude": 30.0,
                "region": "NA",
                "tier": 1,
                "annual_spend_usd": 1_000.0,
                "last_audit_date": "2025-12-31",
            },
            {
                "supplier_id": "SUP-STALE",
                "supplier_name": "Stale Audit Supplier",
                "risk_score": 0.20,
                "latitude": 40.0,
                "longitude": 40.0,
                "region": "LATAM",
                "tier": 4,
                "annual_spend_usd": 1_000.0,
                "last_audit_date": None,
            },
        ]
    )


@pytest.fixture(scope="module")
def synthetic_suppliers() -> pl.DataFrame:
    n = SYNTHETIC_ROW_COUNT

    return (
        pl.DataFrame({"i": pl.Series(range(1, n + 1))})
        .with_columns(
            pl.concat_str(pl.lit("SUP-"), pl.col("i").cast(pl.String).str.zfill(6)).alias("supplier_id"),
            pl.concat_str(pl.lit("Supplier "), pl.col("i").cast(pl.String)).alias("supplier_name"),
            ((pl.col("i") % 100) / 100).cast(pl.Float64).alias("risk_score"),
            ((pl.col("i") % 18_000) / 100 - 90).cast(pl.Float64).alias("latitude"),
            ((pl.col("i") % 36_000) / 100 - 180).cast(pl.Float64).alias("longitude"),
            pl.when((pl.col("i") % 4) == 0)
            .then(pl.lit("EMEA"))
            .when((pl.col("i") % 4) == 1)
            .then(pl.lit("APAC"))
            .when((pl.col("i") % 4) == 2)
            .then(pl.lit("NA"))
            .otherwise(pl.lit("LATAM"))
            .alias("region"),
            pl.when((pl.col("i") % 4) == 0)
            .then(1)
            .when((pl.col("i") % 4) == 1)
            .then(2)
            .when((pl.col("i") % 4) == 2)
            .then(3)
            .otherwise(4)
            .alias("tier"),
            pl.when((pl.col("i") % 4) == 0)
            .then(10_000.0 + pl.col("i").cast(pl.Float64))
            .otherwise(pl.col("i").cast(pl.Float64))
            .alias("annual_spend_usd"),
            pl.when((pl.col("i") % 10) == 0)
            .then(pl.lit(None).cast(pl.String))
            .otherwise(pl.lit("2025-01-01"))
            .alias("last_audit_date"),
        )
        .select(
            [
                "supplier_id",
                "supplier_name",
                "risk_score",
                "latitude",
                "longitude",
                "region",
                "tier",
                "annual_spend_usd",
                "last_audit_date",
            ]
        )
    )


def _order_by_risk(df: pl.DataFrame) -> list[str]:
    return (
        df.sort(["composite_risk", "supplier_id"], descending=[True, False])
        .get_column("supplier_id")
        .to_list()
    )


def test_scenario_threshold_order_validator() -> None:
    with pytest.raises(ValueError):
        ScenarioConfig(
            scenario_name="invalid",
            min_risk_threshold=0.8,
            max_risk_threshold=0.2,
        )


def test_scenario_forbids_extra_fields() -> None:
    with pytest.raises(ValueError):
        ScenarioConfig(scenario_name="invalid", unknown_field=1)


def test_weighting_presets_produce_different_orderings() -> None:
    df = _scenario_df()

    configs = {
        RiskWeighting.BALANCED: ScenarioConfig(scenario_name="balanced"),
        RiskWeighting.FINANCIAL_HEAVY: ScenarioConfig(
            scenario_name="financial",
            weighting=RiskWeighting.FINANCIAL_HEAVY,
        ),
        RiskWeighting.OPERATIONAL_HEAVY: ScenarioConfig(
            scenario_name="operational",
            weighting=RiskWeighting.OPERATIONAL_HEAVY,
        ),
        RiskWeighting.GEOPOLITICAL_HEAVY: ScenarioConfig(
            scenario_name="geopolitical",
            weighting=RiskWeighting.GEOPOLITICAL_HEAVY,
        ),
    }

    orders = {
        weighting: _order_by_risk(score_suppliers(df, config, apply_filters=False))
        for weighting, config in configs.items()
    }

    assert orders[RiskWeighting.FINANCIAL_HEAVY][0] == "SUP-FIN"
    assert orders[RiskWeighting.OPERATIONAL_HEAVY][0] == "SUP-OPS"
    assert orders[RiskWeighting.GEOPOLITICAL_HEAVY][0] == "SUP-GEO"

    unique_orders = {tuple(order) for order in orders.values()}
    assert len(unique_orders) > 1


def test_composite_risk_is_clamped_to_unit_interval() -> None:
    df = pl.DataFrame(
        [
            {
                "supplier_id": "SUP-HIGH",
                "supplier_name": "Overflow",
                "risk_score": 5.0,
                "latitude": 0.0,
                "longitude": 0.0,
                "region": "EMEA",
                "tier": 1,
                "annual_spend_usd": 1_000_000_000.0,
                "last_audit_date": None,
            },
            {
                "supplier_id": "SUP-LOW",
                "supplier_name": "Underflow",
                "risk_score": -5.0,
                "latitude": 0.0,
                "longitude": 0.0,
                "region": "NA",
                "tier": 4,
                "annual_spend_usd": 0.0,
                "last_audit_date": "2025-12-31",
            },
        ]
    )

    config = ScenarioConfig(scenario_name="clamp")
    scored = score_suppliers(df, config, apply_filters=False)

    assert scored.get_column("composite_risk").max() <= 1.0
    assert scored.get_column("composite_risk").min() >= 0.0


def test_threshold_filtering_applies_scenario_bounds() -> None:
    df = _scenario_df()
    full = score_suppliers(df, ScenarioConfig(scenario_name="full"), apply_filters=False)

    filtered = score_suppliers(
        df,
        ScenarioConfig(
            scenario_name="filtered",
            min_risk_threshold=0.4,
            max_risk_threshold=1.0,
        ),
    )

    assert 0 <= filtered.height < full.height
    assert (
        filtered.filter(
            (pl.col("composite_risk") < 0.4) | (pl.col("composite_risk") > 1.0)
        ).height
        == 0
    )


def test_score_50k_suppliers_under_2_seconds(synthetic_suppliers: pl.DataFrame) -> None:
    config = ScenarioConfig(scenario_name="performance")

    def run() -> pl.DataFrame:
        return score_suppliers(synthetic_suppliers, config, apply_filters=False)

    start = time.perf_counter()
    scored = run()
    elapsed = time.perf_counter() - start

    # One bounded retry absorbs Colab cold-start jitter while preserving the hard budget.
    if elapsed >= SCORING_BUDGET_SECONDS:
        start = time.perf_counter()
        scored = run()
        elapsed = time.perf_counter() - start

    assert scored.height == SYNTHETIC_ROW_COUNT
    assert "composite_risk" in scored.columns
    assert elapsed < SCORING_BUDGET_SECONDS
