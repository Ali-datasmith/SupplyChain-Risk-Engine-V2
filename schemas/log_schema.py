"""
Pydantic v2 contract for routing structured loguru records into Streamlit.
This model is the stable boundary between telemetry and UI rendering.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AppLog(BaseModel):
    model_config = {"frozen": True}

    timestamp: datetime
    level: str
    message: str
    module: str
    function: str
    line: int
    request_id: str | None = None
    supplier_id: str | None = None
    batch_id: str | None = None
    extra: dict[str, object] = Field(default_factory=dict)

    @classmethod
    def from_loguru_record(cls, record: dict) -> "AppLog":
        extra = dict(record.get("extra", {}))
        return cls(
            timestamp=record["time"],
            level=record["level"].name,
            message=record["message"],
            module=record["module"],
            function=record["function"],
            line=record["line"],
            request_id=extra.pop("request_id", None),
            supplier_id=extra.pop("supplier_id", None),
            batch_id=extra.pop("batch_id", None),
            extra=extra,
        )
