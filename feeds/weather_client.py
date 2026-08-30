"""
Open-Meteo shipping-risk client (free, no API key).

All outbound HTTP goes through resilience.http_client.
"""
from __future__ import annotations

from resilience.http_client import get_http_client, http_retry
from schemas.weather_schema import ShippingRisk, WeatherReport
from telemetry.logger import logger

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

CONDITION_MAP: dict[int, str] = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def classify_shipping_risk(wind_kmh: float, precip_prob_pct: float) -> ShippingRisk:
    """Deterministic shipping-risk rules."""
    if wind_kmh >= 80 or precip_prob_pct >= 80:
        return ShippingRisk.SEVERE
    if wind_kmh >= 50 or precip_prob_pct >= 60:
        return ShippingRisk.HIGH
    if wind_kmh >= 30 or precip_prob_pct >= 40:
        return ShippingRisk.MODERATE
    return ShippingRisk.LOW


@http_retry
def _fetch_payload(latitude: float, longitude: float) -> dict:
    client = get_http_client()
    response = client.get(
        OPEN_METEO_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,windspeed_10m,precipitation_probability,weathercode",
            "forecast_days": 1,
        },
        timeout=20.0,
    )
    response.raise_for_status()
    return response.json()


def fetch_weather(latitude: float, longitude: float) -> WeatherReport:
    """
    Fetch hourly forecast and derive a deterministic WeatherReport for the
    worst-wind hour of the forecast window. Handles missing keys gracefully.
    """
    payload = _fetch_payload(latitude, longitude)
    hourly = payload.get("hourly", {})

    winds_raw = hourly.get("windspeed_10m") or [0.0]
    precip_raw = hourly.get("precipitation_probability") or [0.0]
    temps_raw = hourly.get("temperature_2m") or [20.0]
    codes_raw = hourly.get("weathercode") or [0]

    length = max(len(winds_raw), len(precip_raw), len(temps_raw), len(codes_raw), 1)

    winds = [float(v) if v is not None else 0.0 for v in (winds_raw + [0.0] * length)[:length]]
    precip = [float(v) if v is not None else 0.0 for v in (precip_raw + [0.0] * length)[:length]]
    temps = [float(v) if v is not None else 20.0 for v in (temps_raw + [20.0] * length)[:length]]
    codes = [int(v) if v is not None else 0 for v in (codes_raw + [0] * length)[:length]]

    idx = max(range(len(winds)), key=lambda i: winds[i]) if winds else 0

    wind_kmh = winds[idx]
    precip_pct = precip[idx]
    condition = CONDITION_MAP.get(codes[idx], "Unknown")
    risk = classify_shipping_risk(wind_kmh, precip_pct)

    logger.bind(source="open-meteo").info(
        f"Weather fetched for ({latitude}, {longitude}): risk={risk.value}"
    )

    return WeatherReport(
        temperature_c=temps[idx],
        wind_kmh=wind_kmh,
        precip_prob_pct=precip_pct,
        condition=condition,
        risk_level=risk,
        latitude=latitude,
        longitude=longitude,
    )
