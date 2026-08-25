"""
UI input contract for scenario execution.
Pydantic v2, frozen, extra=forbid, threshold-order validation.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class RiskWeighting(str, Enum):
    BALANCED = "balanced"
    FINANCIAL_HEAVY = "financial_heavy"
    OPERATIONAL_HEAVY = "operational_heavy"
    GEOPOLITICAL_HEAVY = "geopolitical_heavy"


class ScenarioConfig(BaseModel):
    model_config = {"frozen": True, "extra": "forbid"}

    scenario_name: str = Field(min_length=1, max_length=100)
    regions: list[str] = Field(default_factory=lambda: ["EMEA", "APAC", "NA", "LATAM"])
    min_risk_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    max_risk_threshold: float = Field(default=1.0, ge=0.0, le=1.0)
    weighting: RiskWeighting = RiskWeighting.BALANCED
    include_ai_narrative: bool = True
    max_map_points: int = Field(default=50_000, gt=0, le=250_000)

    @model_validator(mode="after")
    def check_threshold_order(self) -> "ScenarioConfig":
        if self.min_risk_threshold > self.max_risk_threshold:
            raise ValueError("min_risk_threshold must be <= max_risk_threshold")
        return self
