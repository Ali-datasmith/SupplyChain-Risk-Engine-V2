"""
AI narrative generation with 10k-token batching and shared resilience.

2026 rules enforced:
- NO manual JSON parsing on model output. Consume response.parsed directly.
- NO manual retry logic. Reuse resilience.http_client.http_retry.
"""
from __future__ import annotations

import json

from google.genai import types

from ai.genai_client import get_client, get_model_id
from ai.prompts import NARRATIVE_PROMPT_TEMPLATE
from resilience.http_client import http_retry
from schemas.narrative_schema import RiskNarrative

MAX_INPUT_TOKENS = 10_000


def _estimate_tokens(text: str) -> int:
    """Heuristic: ~4 characters per token."""
    return len(text) // 4


def _chunk_rows(rows: list[dict], max_tokens: int = MAX_INPUT_TOKENS) -> list[list[dict]]:
    """Split supplier rows into batches under the 10k input token budget."""
    chunks: list[list[dict]] = []
    current_chunk: list[dict] = []
    current_tokens = 0

    for row in rows:
        row_text = json.dumps(row)
        row_tokens = _estimate_tokens(row_text)

        if current_tokens + row_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(row)
        current_tokens += row_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


@http_retry
def _generate_batch(
    client: object,
    model_id: str,
    rows: list[dict],
) -> list[RiskNarrative]:
    """Single batch generation wrapped in the shared tenacity retry policy."""
    prompt_text = NARRATIVE_PROMPT_TEMPLATE.format(suppliers=json.dumps(rows))

    response = client.models.generate_content(  # type: ignore[attr-defined]
        model=model_id,
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[RiskNarrative],
            temperature=0.1,
        ),
    )

    parsed = response.parsed
    if not isinstance(parsed, list):
        parsed = [parsed]

    return parsed


def generate(supplier_rows: list[dict]) -> dict[str, RiskNarrative]:
    """
    Generate risk narratives for a list of supplier rows.

    Returns a dict keyed by supplier_id, matching the Streamlit session contract.
    """
    client = get_client()
    model_id = get_model_id()

    name_to_id = {
        row["supplier_name"]: row["supplier_id"]
        for row in supplier_rows
        if "supplier_name" in row and "supplier_id" in row
    }

    results: dict[str, RiskNarrative] = {}
    chunks = _chunk_rows(supplier_rows)

    for chunk in chunks:
        narratives = _generate_batch(client, model_id, chunk)
        for narrative in narratives:
            sid = name_to_id.get(narrative.supplier_name, "UNKNOWN")
            results[sid] = narrative

    return results
