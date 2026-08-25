"""
RSS intelligence client.

All outbound HTTP goes through resilience.http_client (cached client + shared
tenacity policy). feedparser only parses bytes fetched by httpx.
"""
from __future__ import annotations

from calendar import timegm
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


def fetch_news(
    keywords: str | None = None,
    sources: list[str] | None = None,
) -> list[NewsItem]:
    """
    Fetch, filter, and sort news items from the configured RSS sources.

    Keywords are comma-separated and matched case-insensitively against
    title + summary. Returns items sorted by published desc.
    """
    selected = sources or list(RSS_SOURCES.keys())
    keyword_list = [k.strip().lower() for k in (keywords or "").split(",") if k.strip()]

    items: list[NewsItem] = []

    for name in selected:
        url = RSS_SOURCES[name]

        try:
            payload = _fetch_feed(url)
        except Exception as exc:
            logger.bind(source="rss").warning(f"Feed fetch failed for {name}: {exc}")
            continue

        parsed = feedparser.parse(payload)

        for entry in parsed.entries:
            title = str(entry.get("title", ""))
            summary = entry.get("summary") or None

            if keyword_list and not any(
                k in f"{title} {summary or ''}".lower() for k in keyword_list
            ):
                continue

            items.append(
                NewsItem(
                    title=title,
                    url=str(entry.get("link", "")),
                    source=name,
                    published=_parse_published(entry),
                    summary=summary,
                )
            )

        logger.bind(source="rss").info(
            f"Fetched {len(parsed.entries)} entries from {name}"
        )

    items.sort(key=lambda item: item.published, reverse=True)
    return items
