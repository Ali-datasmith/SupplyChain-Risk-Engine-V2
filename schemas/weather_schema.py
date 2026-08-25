"""Pydantic v2 contract for Open-Meteo shipping risk."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ShippingRisk(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class WeatherReport(BaseModel):
    model_config = {"frozen": True}

    temperature_c: float
    wind_kmh: float
    precip_prob_pct: float
    condition: str
    risk_level: ShippingRisk
    latitude: float
    longitude: float
