"""
RSS intelligence client.

All outbound HTTP goes through resilience.http_client (cached client + shared
tenacity policy). feedparser only parses bytes fetched by httpx.
Sources are fetched concurrently (thread pool) to bound worst-case latency.
"""
from __future__ import annotations

from calendar import timegm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import feedparser

from resilience.http_client import get_http_client, http_retry
from schemas.news_schema import NewsItem
from telemetry.logger import logger

RSS_SOURCES: dict[str, str] = {
    "Supply Chain Dive": "https://www.supplychaindive.com/feeds/news/",
    "Logistics Management": "https://www.logisticsmgmt.com/rss/feed",
    "FreightWaves": "https://www.freightwaves.com/news/feed",
    "DC Velocity": "https://www.dcvelocity.com/rss/feed",
    "JOC": "https://www.joc.com/rss.xml",
    "Hellenic Shipping News": "https://www.hellenicshippingnews.com/feed/",
    "Reuters Trade": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    "Bloomberg Supply Chain": "https://feeds.bloomberg.com/markets/news.rss",
}


@http_retry
def _fetch_feed(url: str) -> bytes:
    client = get_http_client()
    response = client.get(url, timeout=20.0)
    response.raise_for_status()
    return response.content


def _parse_published(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        struct = getattr(entry, attr, None)
        if struct:
            return datetime.fromtimestamp(timegm(struct), tz=timezone.utc)
    return datetime.fromtimestamp(0, tz=timezone.utc)


def _fetch_one(name: str) -> list[NewsItem]:
    url = RSS_SOURCES.get(name, name)
    try:
        payload = _fetch_feed(url)
    except Exception as exc:
        logger.bind(source="rss").warning(f"Feed fetch failed for {name}: {exc}")
        return []

    try:
        parsed = feedparser.parse(payload)
        if getattr(parsed, "bozo", 0) and not parsed.entries:
            logger.bind(source="rss").warning(f"Feed parsing bozo flag set for {name}")
            return []

        items = [
            NewsItem(
                title=str(entry.get("title", "") or "Untitled"),
                url=str(entry.get("link", "") or url),
                source=name,
                published=_parse_published(entry),
                summary=entry.get("summary") or None,
            )
            for entry in parsed.entries
        ]
        logger.bind(source="rss").info(f"Fetched {len(items)} entries from {name}")
        return items
    except Exception as exc:
        logger.bind(source="rss").warning(f"Feed parsing error for {name}: {exc}")
        return []


def fetch_news(
    keywords: str | None = None,
    sources: list[str] | None = None,
) -> list[NewsItem]:
    """Fetch, filter, and sort news items from the configured RSS sources."""
    selected = sources or list(RSS_SOURCES.keys())
    keyword_list = [k.strip().lower() for k in (keywords or "").split(",") if k.strip()]

    items: list[NewsItem] = []
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(selected)))) as pool:
        for batch in pool.map(_fetch_one, selected):
            items.extend(batch)

    if keyword_list:
        items = [
            i for i in items
            if any(k in f"{i.title} {i.summary or ''}".lower() for k in keyword_list)
        ]

    items.sort(key=lambda item: item.published, reverse=True)
    return items
