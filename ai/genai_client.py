"""
Lazy, cached google.genai.Client singleton.

NEVER construct at import time. Tests and CI must import this module without
requiring API credentials.
"""
from __future__ import annotations

import os
from typing import Any

_client: Any | None = None


def _resolve_model_id() -> str:
    """Resolve model ID from Streamlit secrets, env vars, or default."""
    try:
        import streamlit as st  # type: ignore

        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            return str(st.secrets["GEMINI_MODEL"])
    except Exception:
        pass

    return os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")


def get_client() -> Any:
    """Lazy singleton google.genai.Client factory."""
    global _client
    if _client is None:
        from google import genai

        _client = genai.Client()
    return _client


def get_model_id() -> str:
    return _resolve_model_id()
