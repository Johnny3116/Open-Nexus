"""Heartbeat — wake, review the checklist, ping only if something matters."""

from __future__ import annotations


class Heartbeat:
    def __init__(self, *, interval_seconds: int = 1800) -> None:
        self.interval_seconds = interval_seconds

    async def tick(self) -> None:
        # TODO(phase: scheduling): assemble a check turn; return silently if
        # nothing is actionable; respect quiet hours; never trigger a paid action.
        raise NotImplementedError("Heartbeat.tick: scheduling phase")
