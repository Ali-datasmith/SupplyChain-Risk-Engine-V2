"""
Loguru 0.7.x structured telemetry configuration.
- JSON-only line format via AppLog contract
- enqueue=True for async-safe emission
- daily rotation, 30-day retention, gz compression
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from schemas.log_schema import AppLog

_CONFIGURED = False


def json_formatter(record: dict[str, Any]) -> str:
    """Serialize the loguru record through the typed AppLog contract."""
    log = AppLog.from_loguru_record(record)
    payload = log.model_dump(mode="json")
    return json.dumps(payload, ensure_ascii=False, default=str) + "\n"


def configure_logging(
    *,
    level: str | None = None,
    log_file: str | None = None,
    stderr: bool = True,
) -> None:
    """
    Configure process-wide loguru sinks.

    Set APP_LOG_FILE=false/0/no/off to disable file output (useful in tests).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    resolved_level = (level or os.getenv("APP_LOG_LEVEL", "INFO")).upper()

    logger.remove()

    if stderr:
        logger.add(
            sys.stderr,
            format=json_formatter,
            level=resolved_level,
            enqueue=True,
            colorize=False,
            backtrace=False,
            diagnose=False,
            catch=True,
        )

    resolved_file = log_file if log_file is not None else os.getenv("APP_LOG_FILE", "logs/app.log")
    if resolved_file and resolved_file.lower() not in {"0", "false", "no", "off"}:
        path = Path(resolved_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(path),
            format=json_formatter,
            level=resolved_level,
            enqueue=True,
            rotation="1 day",
            retention="30 days",
            compression="gz",
            backtrace=False,
            diagnose=False,
            catch=True,
            encoding="utf-8",
        )

    _CONFIGURED = True


configure_logging()
