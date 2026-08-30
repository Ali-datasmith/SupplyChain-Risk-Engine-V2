"""Phase 4 tests: httpx client singleton and mock transport retry verification."""
from __future__ import annotations

import httpx

import resilience.http_client as hc
from resilience.http_client import get_http_client, http_retry


from resilience.http_client import CAT_AUTH, CAT_QUOTA, CAT_SCHEMA, CAT_TIMEOUT, classify_error


def test_classify_error_categories() -> None:
    assert classify_error(httpx.HTTPStatusError("429 Rate Limit", request=None, response=httpx.Response(429))) == CAT_QUOTA
    assert classify_error(httpx.HTTPStatusError("401 Unauthorized", request=None, response=httpx.Response(401))) == CAT_AUTH
    assert classify_error(httpx.HTTPStatusError("504 Gateway Timeout", request=None, response=httpx.Response(504))) == CAT_TIMEOUT
    assert classify_error(ValueError("Pydantic schema validation error")) == CAT_SCHEMA


def test_http_client_is_singleton() -> None:
    c1 = get_http_client()
    c2 = get_http_client()
    assert c1 is c2


def test_http_retry_with_mock_transport() -> None:
    """
    Verify httpx MockTransport + tenacity integration:
    Fails twice with 503, then succeeds with 200. Handler invoked exactly 3 times.
    """
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] <= 2:
            return httpx.Response(503, request=request)
        return httpx.Response(200, request=request, json={"status": "ok"})

    transport = httpx.MockTransport(handler)

    old_client = hc._http_client
    hc._http_client = httpx.Client(transport=transport)

    @http_retry
    def make_request():
        res = hc._http_client.get("http://test")
        res.raise_for_status()
        return res.json()

    try:
        result = make_request()
        assert result == {"status": "ok"}
        assert attempts["count"] == 3
    finally:
        hc._http_client = old_client
