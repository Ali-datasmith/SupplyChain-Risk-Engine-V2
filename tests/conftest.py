"""
Pytest bootstrap for Phase 1.

- Ensures project root is importable in Colab.
- Disables file logging for tests unless explicitly overridden.
- Provides a mocked Streamlit context for telemetry handler tests.
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("APP_LOG_FILE", "false")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def mock_streamlit(monkeypatch):
    """
    Mock Streamlit module/context for headless tests.

    Supports:
    - st.session_state
    - st.sidebar.expander(...) context manager
    """
    st = MagicMock(name="streamlit")
    st.session_state = {}

    expander = MagicMock(name="expander")
    st.sidebar.expander.return_value.__enter__.return_value = expander

    monkeypatch.setitem(sys.modules, "streamlit", st)
    return st


@pytest.fixture
def streamlit_log_handler(mock_streamlit):
    """Fresh StreamlitLogHandler instance for UI-independent tests."""
    from telemetry.streamlit_handler import StreamlitLogHandler

    return StreamlitLogHandler()
