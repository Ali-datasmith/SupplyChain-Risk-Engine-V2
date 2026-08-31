"""Phase 4 AI package."""

from ai.genai_client import get_client, get_model_id
from ai.narrative_generator import generate

__all__ = [
    "generate",
    "get_client",
    "get_model_id",
]
