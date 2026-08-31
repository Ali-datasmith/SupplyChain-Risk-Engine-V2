"""Phase 5 tests: session state contract and Single-Path Guard."""
from __future__ import annotations

from collections import deque

from state.session_contract import (
    complete,
    init_session_state,
    is_done,
    register_upload,
    scenario_key,
)


def test_init_session_state_idempotency() -> None:
    state = {}
    init_session_state(state)
    init_session_state(state)

    assert "raw_upload_hash" in state
    assert state["validation_done"] is False
    assert isinstance(state["log_buffer"], deque)
    assert state["log_buffer"].maxlen == 1000


def test_register_upload_invalidates_downstream_flags() -> None:
    state = {}
    init_session_state(state)

    state["validation_done"] = True
    state["scoring_done"] = True
    state["ai_generation_done"] = True
    state["ai_call_count"] = 5

    is_new = register_upload(state, b"new data")

    assert is_new is True
    assert state["validation_done"] is False
    assert state["scoring_done"] is False
    assert state["ai_generation_done"] is False
    assert state["ai_call_count"] == 0
    assert state["ai_narratives"] == {}


def test_same_upload_does_not_invalidate() -> None:
    state = {}
    init_session_state(state)

    register_upload(state, b"same data")
    state["validation_done"] = True

    is_new = register_upload(state, b"same data")

    assert is_new is False
    assert state["validation_done"] is True


def test_stage_callback_invoked_once_across_reruns() -> None:
    state = {}
    init_session_state(state)
    register_upload(state, b"data")

    call_count = {"count": 0}

    def expensive_stage():
        if not is_done(state, "validation_done"):
            call_count["count"] += 1
            complete(state, "validation_done")

    for _ in range(5):
        expensive_stage()

    assert call_count["count"] == 1


def test_ai_call_count_stable_across_reruns() -> None:
    state = {}
    init_session_state(state)
    register_upload(state, b"data")
    state["scenario_config"] = {"name": "test"}

    for _ in range(5):
        if not is_done(state, "ai_generation_done"):
            state["ai_call_count"] += 1
            complete(state, "ai_generation_done")

    assert state["ai_call_count"] == 1


def test_scenario_change_rearms_scoring_and_ai_but_not_validation() -> None:
    state = {}
    init_session_state(state)
    register_upload(state, b"data")
    complete(state, "validation_done")
    complete(state, "scoring_done")
    complete(state, "ai_generation_done")

    state["scenario_config"] = {"name": "new_scenario"}
    state["scoring_done"] = False
    state["ai_generation_done"] = False

    assert state["validation_done"] is True
    assert state["scoring_done"] is False
    assert state["ai_generation_done"] is False


def test_scenario_key_composite() -> None:
    state = {}
    init_session_state(state)
    state["raw_upload_hash"] = "abc123"
    state["scenario_config"] = {"name": "test"}

    key = scenario_key(state)
    assert key == ("abc123", {"name": "test"})
