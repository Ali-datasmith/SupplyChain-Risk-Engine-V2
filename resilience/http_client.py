"""
Shared resilience layer.

- httpx.Client singleton with connection-level retries (HTTPTransport).
- tenacity policy for HTTP-status retries (429/502/503).
- Categorized error classification: typed HTTP status checks take precedence
  over substring heuristics to avoid misclassification.
"""
from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

_http_client: httpx.Client | None = None


def get_http_client() -> httpx.Client:
    """Cached singleton httpx.Client with connection-level retries."""
    global _http_client
    if _http_client is None:
        transport = httpx.HTTPTransport(retries=2)
        _http_client = httpx.Client(transport=transport, timeout=30.0)
    return _http_client


def _is_retryable_http_error(exc: BaseException) -> bool:
    """Tenacity predicate: retry only on 429, 502, 503."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 502, 503}
    return False


http_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=0.1, min=0.01, max=0.05),
    retry=retry_if_exception(_is_retryable_http_error),
    reraise=True,
)


def classify_error(exc: BaseException) -> str:
    """Categorized error mapping. Categories: rate_limit, timeout, schema, auth, fallback."""
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code == 429:
            return "rate_limit"
        if code in (401, 403):
            return "auth"
        if code in (502, 503, 504):
            return "timeout"

    msg = str(exc).lower()

    if "429" in msg or "quota" in msg or "rate_limit" in msg:
        return "rate_limit"

    if "504" in msg or "timeout" in msg or "deadline" in msg:
        return "timeout"

    if "401" in msg or "403" in msg or "auth" in msg or "api_key" in msg:
        return "auth"

    if "schema" in msg or "validation" in msg or "pydantic" in msg or "pydantic_core" in msg:
        return "schema"

    return "fallback"
