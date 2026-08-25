"""
Single-call typed AI news synthesis (response_schema + response.parsed).
NO json.loads. Shared http_retry + lazy genai client.
"""
from __future__ import annotations

from google.genai import types

from ai.genai_client import get_client, get_model_id
from resilience.http_client import http_retry
from schemas.news_schema import NewsDigest, NewsItem
from telemetry.logger import logger

NEWS_DIGEST_PROMPT_TEMPLATE = """
You are an elite supply chain intelligence analyst. Synthesize the following
live news items into a single NewsDigest object.

Strictly adhere to the response_schema. No markdown, no commentary.

News items:
{items}
"""


@http_retry
def _generate(client, model_id: str, prompt: str) -> NewsDigest:
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NewsDigest,
            temperature=0.2,
        ),
    )
    return response.parsed


def generate_news_digest(news_items: list[NewsItem]) -> NewsDigest:
    """Typed synthesis of the current news landscape."""
    client = get_client()
    model_id = get_model_id()

    lines = "\n".join(
        f"- [{item.source}] {item.title} ({item.published.isoformat()}): {item.summary or ''}"
        for item in news_items
    )
    prompt = NEWS_DIGEST_PROMPT_TEMPLATE.format(items=lines)

    digest = _generate(client, model_id, prompt)
    logger.bind(source="genai").info("News digest generated")
    return digest
