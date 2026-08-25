"""V2.1 tests: RSS client parsing, keyword filter, retry, and hygiene."""
from __future__ import annotations

from pathlib import Path

import httpx
import pytest

import resilience.http_client as hc
from feeds.rss_client import fetch_news

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Port strike disrupts EMEA lanes</title>
      <link>https://example.com/1</link>
      <pubDate>Mon, 05 Jan 2026 10:00:00 GMT</pubDate>
      <description>Dockworkers strike spreads</description>
    </item>
    <item>
      <title>Chip shortage eases in APAC</title>
      <link>https://example.com/2</link>
      <pubDate>Tue, 06 Jan 2026 09:00:00 GMT</pubDate>
      <description>Semiconductor supply recovers</description>
    </item>
  </channel>
</rss>
"""


@pytest.fixture
def mock_rss_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=SAMPLE_RSS)

    old = hc._http_client
    hc._http_client = httpx.Client(transport=httpx.MockTransport(handler))
    yield
    hc._http_client = old


def test_fetch_news_parses_and_sorts_desc(mock_rss_transport) -> None:
    items = fetch_news(sources=["Supply Chain Dive"])

    assert len(items) == 2
    assert items[0].title == "Chip shortage eases in APAC"
    assert items[1].title == "Port strike disrupts EMEA lanes"
    assert items[0].source == "Supply Chain Dive"
    assert items[0].url == "https://example.com/2"


def test_keyword_filter(mock_rss_transport) -> None:
    items = fetch_news(keywords="strike", sources=["Supply Chain Dive"])

    assert len(items) == 1
    assert "strike" in items[0].title.lower()


def test_retry_on_503_then_200() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(503, text="unavailable")
        return httpx.Response(200, text=SAMPLE_RSS)

    old = hc._http_client
    hc._http_client = httpx.Client(transport=httpx.MockTransport(handler))

    try:
        items = fetch_news(sources=["FreightWaves"])
    finally:
        hc._http_client = old

    assert calls["count"] == 2
    assert len(items) == 2


def test_no_requests_import_in_feeds() -> None:
    for path in Path("feeds").glob("*.py"):
        assert "import requests" not in path.read_text()
