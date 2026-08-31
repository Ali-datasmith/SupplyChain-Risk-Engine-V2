"""Streamlit loguru handler with safe dictionary formatting and wrapped lines."""
from collections import deque

import streamlit as st
from loguru import logger


class StreamlitLogHandler:
    def __init__(self, buffer: deque | None = None):
        self.buffer = buffer if buffer is not None else deque(maxlen=1000)
        self.handler_id = None

    def attach(self):
        if self.handler_id is None:
            self.handler_id = logger.add(
                self._sink,
                level="INFO",
                enqueue=False,
                format="{message}",
            )

    def _sink(self, message):
        record = message.record
        time_str = record['time'].strftime('%H:%M:%S')
        level = record['level'].name
        msg = record['message']
        extra = record.get('extra', {})

        extra_str = ""
        if extra:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in extra.items())

        self.buffer.append(f"{time_str} | {level:<8} | {msg}{extra_str}")

    def render(self):
        with st.expander("◈ System Telemetry", expanded=False):
            if not self.buffer:
                st.caption("No logs recorded yet.")
            else:
                st.code("\n".join(reversed(list(self.buffer))), language="log", height=300, wrap_lines=True)

    def detach(self):
        if self.handler_id is not None:
            logger.remove(self.handler_id)
            self.handler_id = None
