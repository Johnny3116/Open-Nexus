"""Trace — emit lifecycle events tied to a turn's trace_id."""

from __future__ import annotations

from typing import Any

from open_nexus.observability.events import Event
from open_nexus.observability.logger import get_logger


class Trace:
    """A thin per-turn event emitter. One Trace per turn, keyed by trace_id."""

    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self._log = get_logger("open_nexus.trace")

    def emit(self, event: Event, **fields: Any) -> None:
        """Record a lifecycle event. Phase 0: log line; later: structured sink."""
        extra = " ".join(f"{k}={v!r}" for k, v in fields.items())
        self._log.info("[%s] %s %s", self.trace_id, event.value, extra)
