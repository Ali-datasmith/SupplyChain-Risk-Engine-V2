"""V2.1 tests: intelligence session keys and news TTL."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from state.session_contract import (
    init_session_state,
    make_weather_key,
    news_is_stale,
    register_upload,
)


def test_new_intel_keys_reset_on_new_upload() -> None:
    state = {}
    init_session_state(state)
    register_upload(state, b"upload-a")

    state["news_done"] = True
    state["news_items"] = ["x"]
    state["news_last_fetch"] = datetime.now(timezone.utc)
    state["weather_done"] = True
    state["weather_report"] = "report"
    state["weather_key"] = ("h", "SUP-1")
    state["ai_news_done"] = True
    state["ai_news_digest"] = "digest"

    is_new = register_upload(state, b"upload-b")

    assert is_new is True
    assert state["news_done"] is False
    assert state["news_items"] == []
    assert state["news_last_fetch"] is None
    assert state["weather_done"] is False
    assert state["weather_report"] is None
    assert state["weather_key"] is None
    assert state["ai_news_done"] is False
    assert state["ai_news_digest"] is None


def test_same_upload_preserves_intel_state() -> None:
    state = {}
    init_session_state(state)
    register_upload(state, b"same")

    state["news_done"] = True

    is_new = register_upload(state, b"same")

    assert is_new is False
    assert state["news_done"] is True


def test_news_ttl_stale_and_fresh() -> None:
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    stale_state = {"news_last_fetch": now - timedelta(seconds=901)}
    fresh_state = {"news_last_fetch": now - timedelta(seconds=899)}
    empty_state = {}

    assert news_is_stale(stale_state, now=now) is True
    assert news_is_stale(fresh_state, now=now) is False
    assert news_is_stale(empty_state, now=now) is True


def test_make_weather_key_composite() -> None:
    state = {"raw_upload_hash": "abc"}
    assert make_weather_key(state, "SUP-1") == ("abc", "SUP-1")
