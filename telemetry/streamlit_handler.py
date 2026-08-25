"""
Streamlit telemetry surface.

This module is importable without a live Streamlit runtime. Streamlit is imported
lazily inside render() so unit tests and headless pipelines remain deterministic.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from schemas.log_schema import AppLog


class StreamlitLogHandler:
    """
    Bounded in-memory log buffer backed by collections.deque(maxlen=1000).

    Attach as a loguru sink with handler.attach(), then render in the Streamlit
    sidebar using handler.render().
    """

    def __init__(self, maxlen: int = 1000, buffer: deque[AppLog] | None = None) -> None:
        self.maxlen = maxlen
        self.buffer: deque[AppLog] = buffer if buffer is not None else deque(maxlen=maxlen)

    def write(self, message: Any) -> None:
        """Loguru sink interface."""
        record = getattr(message, "record", message)
        self.buffer.append(AppLog.from_loguru_record(record))

    def attach(self, *, level: str = "DEBUG", enqueue: bool = False) -> int:
        """Attach this buffer as a loguru sink and return the handler id."""
        from telemetry.logger import logger

        return logger.add(
            self.write,
            level=level,
            enqueue=enqueue,
            catch=True,
        )

    def clear(self) -> None:
        self.buffer.clear()

    def recent(self, limit: int = 100) -> tuple[AppLog, ...]:
        items = tuple(self.buffer)
        if limit <= 0:
            return ()
        return items[-limit:]

    def render(self, *, st: Any | None = None, container: Any | None = None, limit: int = 100) -> None:
        """
        Render recent logs into a Streamlit sidebar expander.

        Pass st explicitly in tests to inject a mocked Streamlit context.
        """
        if st is None:
            import streamlit as st  # type: ignore

        target = container if container is not None else st.sidebar

        with target.expander("Telemetry", expanded=False) as expander:
            if not self.buffer:
                expander.caption("No telemetry recorded.")
                return

            for entry in reversed(self.recent(limit=limit)):
                expander.caption(
                    f"{entry.timestamp.isoformat()} | {entry.level} | "
                    f"{entry.module}.{entry.function}:{entry.line}"
                )
                expander.code(entry.model_dump_json(indent=2), language="json")
