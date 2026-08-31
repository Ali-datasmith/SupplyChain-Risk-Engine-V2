"""Phase 4 tests: AI narrative generation, retry, and error classification."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from ai import narrative_generator
from resilience.http_client import (
    CAT_AUTH,
    CAT_FALLBACK,
    CAT_QUOTA,
    CAT_SCHEMA,
    CAT_TIMEOUT,
    classify_error,
)
from schemas.narrative_schema import RiskLevel, RiskNarrative


@pytest.fixture
def mock_genai_client():
    client = MagicMock()
    client.models = MagicMock()
    with patch("ai.narrative_generator.get_client", return_value=client):
        yield client


def test_happy_path_returns_risk_narrative(mock_genai_client: MagicMock) -> None:
    n1 = RiskNarrative(
        supplier_name="Acme",
        overall_risk=RiskLevel.HIGH,
        key_risks=["debt"],
        recommendation="audit",
        confidence=0.9,
    )
    mock_response = MagicMock()
    mock_response.parsed = [n1]
    mock_genai_client.models.generate_content.return_value = mock_response

    rows = [{"supplier_id": "SUP-1", "supplier_name": "Acme", "risk_score": 0.8}]
    result = narrative_generator.generate(rows)

    assert "SUP-1" in result
    assert isinstance(result["SUP-1"], RiskNarrative)
    assert result["SUP-1"].overall_risk == RiskLevel.HIGH


def test_no_json_loads_in_narrative_generator() -> None:
    """Source-grep assertion: manual JSON parsing is strictly forbidden."""
    with open("ai/narrative_generator.py", "r") as f:
        content = f.read()
    assert "json.loads" not in content


def test_retry_fails_twice_then_succeeds(mock_genai_client: MagicMock) -> None:
    """Verify tenacity retry catches 503 and succeeds on the 3rd attempt."""
    n1 = RiskNarrative(
        supplier_name="Acme",
        overall_risk=RiskLevel.LOW,
        key_risks=[],
        recommendation="ok",
        confidence=1.0,
    )

    attempts = {"count": 0}

    def side_effect(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] <= 2:
            req = httpx.Request("POST", "http://test")
            res = httpx.Response(503, request=req)
            raise httpx.HTTPStatusError("503 Service Unavailable", request=req, response=res)

        mock_resp = MagicMock()
        mock_resp.parsed = [n1]
        return mock_resp

    mock_genai_client.models.generate_content.side_effect = side_effect

    rows = [{"supplier_id": "SUP-1", "supplier_name": "Acme"}]
    result = narrative_generator.generate(rows)

    assert attempts["count"] == 3
    assert "SUP-1" in result


def test_batch_splitting_exceeds_10k_tokens(mock_genai_client: MagicMock) -> None:
    """Verify >10k tokens triggers multiple batches and all IDs are returned."""
    large_text = "x" * 45000  # ~11.25k tokens
    rows = [
        {"supplier_id": f"SUP-{i}", "supplier_name": f"Sup {i}", "extra": large_text}
        for i in range(2)
    ]

    def gen_content(**kwargs):
        return MagicMock(
            parsed=[
                RiskNarrative(
                    supplier_name="Sup 0",
                    overall_risk=RiskLevel.LOW,
                    key_risks=[],
                    recommendation="ok",
                    confidence=1.0,
                ),
                RiskNarrative(
                    supplier_name="Sup 1",
                    overall_risk=RiskLevel.LOW,
                    key_risks=[],
                    recommendation="ok",
                    confidence=1.0,
                ),
            ]
        )

    mock_genai_client.models.generate_content.side_effect = gen_content

    result = narrative_generator.generate(rows)

    assert len(result) == 2
    assert mock_genai_client.models.generate_content.call_count > 1
    assert "SUP-0" in result
    assert "SUP-1" in result


def test_classify_error_categories() -> None:
    """Verify categorized error mapping from multi-ai-research-digest."""
    assert classify_error(Exception("429 Too Many Requests")) == CAT_QUOTA
    assert classify_error(Exception("quota exceeded")) == CAT_QUOTA

    assert classify_error(Exception("504 Gateway Timeout")) == CAT_TIMEOUT
    assert classify_error(Exception("Deadline Exceeded")) == CAT_TIMEOUT

    assert classify_error(Exception("Pydantic validation error")) == CAT_SCHEMA
    assert classify_error(Exception("schema mismatch")) == CAT_SCHEMA

    assert classify_error(Exception("401 Unauthorized api_key")) == CAT_AUTH
    assert classify_error(Exception("403 Forbidden")) == CAT_AUTH

    assert classify_error(Exception("Unknown random error")) == CAT_FALLBACK
