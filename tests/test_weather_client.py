"""V2.1 tests: Open-Meteo client parsing and deterministic risk boundaries."""
from __future__ import annotations

import httpx
import pytest

import resilience.http_client as hc
from feeds.weather_client import classify_shipping_risk, fetch_weather
from schemas.weather_schema import ShippingRisk


def _payload(wind: list[float], precip: list[float], temp: list[float], code: list[int]) -> dict:
    return {
        "hourly": {
            "time": ["2026-01-01T00:00", "2026-01-01T01:00"],
            "temperature_2m": temp,
            "windspeed_10m": wind,
            "precipitation_probability": precip,
            "weathercode": code,
        }
    }


@pytest.fixture
def mock_weather_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=_payload([40.0, 60.0], [10, 20], [5.0, 6.0], [3, 61]),
        )

    old = hc._http_client
    hc._http_client = httpx.Client(transport=httpx.MockTransport(handler))
    yield
    hc._http_client = old


def test_fetch_weather_parses_report(mock_weather_transport) -> None:
    report = fetch_weather(51.5, -0.12)

    assert report.wind_kmh == 60.0
    assert report.temperature_c == 6.0
    assert report.precip_prob_pct == 20.0
    assert report.condition == "Light rain"
    assert report.risk_level == ShippingRisk.HIGH
    assert report.latitude == 51.5


@pytest.mark.parametrize(
    ("wind", "precip", "expected"),
    [
        (29.0, 10.0, ShippingRisk.LOW),
        (30.0, 10.0, ShippingRisk.MODERATE),
        (49.0, 39.0, ShippingRisk.MODERATE),
        (50.0, 0.0, ShippingRisk.HIGH),
        (79.0, 59.0, ShippingRisk.HIGH),
        (0.0, 60.0, ShippingRisk.HIGH),
        (80.0, 0.0, ShippingRisk.SEVERE),
        (0.0, 80.0, ShippingRisk.SEVERE),
    ],
)
def test_risk_boundaries(wind: float, precip: float, expected: ShippingRisk) -> None:
    assert classify_shipping_risk(wind, precip) == expected
