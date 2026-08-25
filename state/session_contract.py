"""
Session state contract implementing the Single-Path Guard Pattern.

All guard functions are Streamlit-agnostic and operate on MutableMapping so they
can be driven by plain dicts in pytest without a Streamlit runtime.

Section 7 keys (exact init values):
- raw_upload_hash: None
- validation_done: False
- validation_errors: None
- validated_df: None
- scenario_config: None
- scoring_done: False
- scored_df: None
- map_render_done: False
- ai_call_count: 0
- ai_narratives: {}
- ai_generation_done: False
- report_pdf_bytes: None
- report_html_str: None
- log_buffer: deque(maxlen=1000)
- last_error: None
"""
from __future__ import annotations

import hashlib
from collections import deque
from typing import Any, MutableMapping

SESSION_KEYS: dict[str, Any] = {
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
}


def init_session_state(state: MutableMapping[str, Any]) -> None:
    """Initialize session state idempotently. Safe to call on every rerun."""
    for key, default in SESSION_KEYS.items():
        if key not in state:
            if key == "log_buffer":
                state[key] = deque(maxlen=1000)
            elif key == "ai_narratives":
                state[key] = {}
            else:
                state[key] = default


def register_upload(state: MutableMapping[str, Any], upload_bytes: bytes) -> bool:
    """
    Register a new upload via SHA-256 hash.

    Returns True if the hash is new (invalidating all downstream *_done flags).
    Returns False if the hash matches the current upload (no invalidation).
    """
    current_hash = hashlib.sha256(upload_bytes).hexdigest()

    if state.get("raw_upload_hash") == current_hash:
        return False

    state["raw_upload_hash"] = current_hash
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
