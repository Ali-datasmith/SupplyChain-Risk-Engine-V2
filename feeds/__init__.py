"""V2.1 live intelligence package."""

from feeds.rss_client import RSS_SOURCES, fetch_news
from feeds.weather_client import fetch_weather

__all__ = ["RSS_SOURCES", "fetch_news", "fetch_weather"]
