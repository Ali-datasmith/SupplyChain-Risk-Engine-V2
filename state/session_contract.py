"""
Session state contract implementing the Single-Path Guard Pattern (V2.1).

All guard functions are Streamlit-agnostic and operate on MutableMapping so they
can be driven by plain dicts in pytest without a Streamlit runtime.

V2 keys (exact init values) + V2.1 intelligence keys.
"""
from __future__ import annotations

import hashlib
from collections import deque
from collections.abc import MutableMapping
from datetime import datetime, timezone
from typing import Any

NEWS_TTL_SECONDS = 900  # 15 minutes

SESSION_KEYS: dict[str, Any] = {
    # ── V2 core ────────────────────────────────────────────
    "raw_upload_hash": None,
    "validation_done": False,
    "validation_errors": None,
    "validated_df": None,
    "scenario_config": None,
    "scoring_done": False,
    "scored_df": None,
    "map_render_done": False,
    "ai_call_count": 0,
    "ai_narratives": {},
    "ai_generation_done": False,
    "report_pdf_bytes": None,
    "report_html_str": None,
    "log_buffer": None,  # initialized in init_session_state
    "last_error": None,
    # ── V2.1 intelligence layer ────────────────────────────
    "news_items": None,  # initialized in init_session_state
    "news_done": False,
    "news_last_fetch": None,
    "weather_report": None,
    "weather_done": False,
    "weather_key": None,
    "ai_news_digest": None,
    "ai_news_done": False,
}


def init_session_state(state: MutableMapping[str, Any]) -> None:
    """Initialize session state idempotently. Safe to call on every rerun."""
    for key, default in SESSION_KEYS.items():
        if key not in state:
            if key == "log_buffer":
                state[key] = deque(maxlen=1000)
            elif key in ("ai_narratives",):
                state[key] = {}
            elif key in ("news_items",):
                state[key] = []
            else:
                state[key] = default


def register_upload(state: MutableMapping[str, Any], upload_bytes: bytes) -> bool:
    """
    Register a new upload via SHA-256 hash.

    Returns True if the hash is new (invalidating ALL downstream *_done flags,
    caches, and V2.1 intelligence state).
    Returns False if the hash matches the current upload (no invalidation).
    """
    current_hash = hashlib.sha256(upload_bytes).hexdigest()

    if state.get("raw_upload_hash") == current_hash:
        return False

    state["raw_upload_hash"] = current_hash

    # V2 downstream invalidation
    state["validation_done"] = False
    state["validation_errors"] = None
    state["validated_df"] = None
    state["scoring_done"] = False
    state["scored_df"] = None
    state["map_render_done"] = False
    state["ai_call_count"] = 0
    state["ai_narratives"] = {}
    state["ai_generation_done"] = False
    state["report_pdf_bytes"] = None
    state["report_html_str"] = None

    # V2.1 intelligence invalidation
    state["news_items"] = []
    state["news_done"] = False
    state["news_last_fetch"] = None
    state["weather_report"] = None
    state["weather_done"] = False
    state["weather_key"] = None
    state["ai_news_digest"] = None
    state["ai_news_done"] = False

    return True


def is_done(state: MutableMapping[str, Any], key: str) -> bool:
    """Check if a stage is complete."""
    return bool(state.get(key, False))


def complete(state: MutableMapping[str, Any], key: str) -> None:
    """Mark a stage as complete."""
    state[key] = True


def scenario_key(state: MutableMapping[str, Any]) -> tuple[Any, Any]:
    """Composite key for scenario-dependent stages (scoring, AI)."""
    return (state.get("raw_upload_hash"), state.get("scenario_config"))


def news_is_stale(
    state: MutableMapping[str, Any],
    ttl_seconds: int = NEWS_TTL_SECONDS,
    now: datetime | None = None,
) -> bool:
    """Pure TTL helper: True when the news cache is missing or older than ttl."""
    last = state.get("news_last_fetch")
    if last is None:
        return True

    now = now or datetime.now(timezone.utc)
    return (now - last).total_seconds() > ttl_seconds


def make_weather_key(state: MutableMapping[str, Any], supplier_id: str) -> tuple[Any, str]:
    """Composite key binding a weather fetch to the current upload + supplier."""
    return (state.get("raw_upload_hash"), supplier_id)
