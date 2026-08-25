"""
Gemini Structured Output Contract (Section 4.3).

Passed directly as response_schema to google.genai. The SDK parses the JSON
response into this model and returns it as response.parsed.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskNarrative(BaseModel):
    """Typed AI response boundary. NO manual json.loads permitted."""

    supplier_name: str = Field(description="Name of the supplier being summarized")
    overall_risk: RiskLevel
    key_risks: list[str] = Field(description="Top risk factors, most severe first", max_length=3)
    recommendation: str = Field(description="One actionable, board-ready recommendation")
    confidence: float = Field(ge=0.0, le=1.0)
