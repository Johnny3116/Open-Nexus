"""Per-session message queue.

Serialises concurrent messages for a single session so the "a message arrives
mid-run" case is handled cleanly (borrowed from OpenClaw's design). Each session
gets its own FIFO; turns for a session run one at a time, while different
sessions proceed in parallel.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict


class SessionQueues:
    """One asyncio.Queue per session id."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def queue_for(self, session_id: str) -> asyncio.Queue:
        return self._queues[session_id]

    def lock_for(self, session_id: str) -> asyncio.Lock:
        """Held for the duration of a turn so a session processes serially."""
        return self._locks[session_id]


# TODO(phase-0): a worker that drains each session's queue under its lock and
# dispatches to agent_turn.
