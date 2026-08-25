"""Phase 5 tests: Streamlit AppTest smoke test."""
from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_app_path_exists() -> None:
    assert APP_PATH.is_file(), f"app.py not found at {APP_PATH}"


def test_app_smoke_test_no_exceptions() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()

    assert not at.exception


def test_app_rerun_stability() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert not at.exception

    at.run()
    assert not at.exception
