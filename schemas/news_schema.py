"""Pydantic v2 contracts for the RSS intelligence layer."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    model_config = {"frozen": True}

    title: str
    url: str
    source: str
    published: datetime
    summary: str | None = None


class NewsDigest(BaseModel):
    """Single-call typed synthesis contract (response_schema)."""

    headline_synthesis: str = Field(description="One-paragraph synthesis of the current news landscape")
    top_disruptions: list[str] = Field(max_length=5, description="Most severe active disruptions first")
    supply_chain_impact: str = Field(description="Board-ready impact statement for supplier risk")
    confidence: float = Field(ge=0.0, le=1.0)
