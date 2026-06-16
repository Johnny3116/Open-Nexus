"""Heartbeat — "only ping when something matters" (OpenClaw style)."""

from __future__ import annotations


class Heartbeat:
    def __init__(self, *, interval_seconds: int, identity, core, channel) -> None:
        self.interval_seconds = interval_seconds
        self.identity = identity      # to read HEARTBEAT.md
        self.core = core              # to run a check turn
        self.channel = channel        # where to ping, if needed

    async def tick(self) -> None:
        """Run one heartbeat check; ping only if the checklist is actionable."""
        # TODO(phase-2): assemble a check turn from HEARTBEAT.md; if nothing is
        # actionable, return silently. Respect quiet hours from USER.md. Never
        # trigger a paid action on a heartbeat — that's how budgets get drained.
        raise NotImplementedError("Heartbeat.tick: Phase 2")

    async def run(self) -> None:
        """Loop forever, ticking every interval_seconds."""
        raise NotImplementedError("Heartbeat.run: Phase 2")
